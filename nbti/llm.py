import json
import time
import logging

from nbti import http_client
from nbti.utils import (
    normalize_answer_question, parse_answer_meta, extract_scene_summary,
    commit_answer_to_history, is_complete_assess, parse_json_answer
)
from nbti.conversation import store
from nbti.providers import get_provider

logger = logging.getLogger(__name__)


def build_thinking_params(profile):
    """薄封装：委托给供应商注册表构建 thinking 参数。

    具体差异（豆包/DeepSeek/LongCat/LM Studio/通用）由 nbti.providers 中
    对应的适配器实现；未知 vendor 回退到 openai_compatible。
    """
    provider = get_provider(profile.get("vendor", "doubao"))
    return provider.build_thinking_params(profile)


def get_chat_completions_url(profile):
    """薄封装：委托给供应商注册表构建 chat/completions 端点 URL。"""
    provider = get_provider(profile.get("vendor", ""))
    return provider.chat_completions_url(profile)


def build_assess_schema():
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "phase": {"type": "string", "enum": ["ASSESS"]},
            "q": {"type": "integer", "minimum": 1},
            "comment": {"type": "string", "minLength": 1, "maxLength": 40},
            "scene": {"type": "string", "minLength": 1, "maxLength": 100},
            "options": {
                "type": "array",
                "minItems": 2,
                "maxItems": 4,
                "items": {"type": "string", "minLength": 1}
            },
            "nb": {"type": "integer"},
            "bh": {"type": "integer"},
            "tf": {"type": "integer"},
            "ip": {"type": "integer"},
            "next_dim": {"type": "string", "enum": ["NB", "BH", "TF", "IP", "END"]},
            "can_conclude": {"type": "boolean"}
        },
        "required": [
            "phase", "q", "comment", "scene", "options",
            "nb", "bh", "tf", "ip", "next_dim", "can_conclude"
        ]
    }


def build_result_schema():
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "phase": {"type": "string", "enum": ["RESULT"]},
            "type": {"type": "string", "minLength": 4, "maxLength": 4},
            "name": {"type": "string", "minLength": 1, "maxLength": 20},
            "oneline": {"type": "string", "minLength": 1, "maxLength": 40},
            "scene": {"type": "string", "minLength": 1, "maxLength": 100},
            "adapt": {"type": "string", "minLength": 1, "maxLength": 60},
            "crash": {"type": "string", "minLength": 1, "maxLength": 60},
            "interpretation": {"type": "string", "minLength": 80, "maxLength": 900},
            "pseudo_science": {"type": "string", "minLength": 80, "maxLength": 1200},
            "closing": {"type": "string", "minLength": 1, "maxLength": 200}
        },
        "required": [
            "phase", "type", "name", "oneline", "scene",
            "adapt", "crash", "interpretation", "pseudo_science", "closing"
        ]
    }


def build_response_format(profile, phase):
    """薄封装：委托给供应商注册表构建 response_format。

    具体差异（豆包/LongCat 返回 {}、DeepSeek 走 json_object、其余走严格
    json_schema）由 nbti.providers 中对应适配器实现；未知 vendor 回退到
    openai_compatible。
    """
    provider = get_provider(profile.get("vendor", "doubao"))
    return provider.build_response_format(profile, phase)


def _is_valid_final_answer(answer, phase, expected_q=None):
    """校验流式最终答案是否完整可入库：assess/init 校验题号与结构，result 校验 RESULT JSON"""
    if phase == 'result':
        data = parse_json_answer(answer)
        return isinstance(data, dict) and data.get('phase') == 'RESULT'
    return is_complete_assess(answer, expected_q)


def stream_generator(profile, payload, conversation_id=None, history=None, message=None, phase=None, save_history=False, config=None):
    """流式生成器：读取 LLM 响应并转发给客户端
    
    Args:
        profile: LLM profile
        payload: 请求 payload
        conversation_id: 对话 ID（用于保存历史）
        history: 对话历史（用于保存）
        message: 用户消息（用于保存）
        phase: 阶段（assess/init/result，用于保存场景）
        save_history: 是否保存历史
        config: 配置（传给 normalize_answer_question）
    
    Yields:
        SSE 格式的事件流
    """
    from flask import stream_with_context
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {profile['api_key']}"
    }
    
    # 添加 stream=True
    payload['stream'] = True
    
    first_token_sent = False
    full_content = []
    tokens_used = 0
    
    try:
        response = http_client.post(
            get_chat_completions_url(profile),
            headers=headers,
            json={k: v for k, v in payload.items() if not k.startswith('_')},
            timeout=120,
            stream=True
        )
        
        if response.status_code == 200:
            response.encoding = 'utf-8'
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        data = json.loads(data_str)
                        choices = data.get('choices') or []
                        choice = choices[0] if choices else {}
                        delta = choice.get('delta') or {}
                        message_delta = choice.get('message') or {}
                        content = (
                            delta.get('content')
                            or message_delta.get('content')
                            or ''
                        )
                        
                        if content:
                            full_content.append(content)
                            
                            # 发送 first_token 事件
                            if not first_token_sent:
                                first_token_sent = True
                                yield f'data: {json.dumps({"event": "first_token", "timestamp": int(time.time() * 1000)})}\n\n'
                            
                            # 发送 chunk 事件
                            yield f'data: {json.dumps({"event": "chunk", "content": content})}\n\n'
                        
                        # 获取 usage 信息（部分模型在最后一个 chunk 中包含）
                        if 'usage' in data:
                            usage = data.get('usage') or {}
                            tokens_used = usage.get('total_tokens', 0)
                    except json.JSONDecodeError:
                        continue
            
            # 发送 done 事件
            full_answer = ''.join(full_content)
            expected_q = payload.get('_expected_q')
            full_answer = normalize_answer_question(full_answer, expected_q, config)

            # 先保存历史，再通知前端完成，避免用户快速点击下一题时读到旧历史。
            # 残缺/非预期 JSON 的答案不入库，避免污染后续上下文（done 事件照常发，前端有重试机制）。
            if save_history and conversation_id and history is not None and message:
                if _is_valid_final_answer(full_answer, phase, expected_q):
                    commit_answer_to_history(conversation_id, message, full_answer, phase)
                else:
                    logger.warning(f"[STREAM] 残缺答案不入库 | conversation_id={conversation_id} | "
                                   f"phase={phase} | answer_preview={full_answer[:80]}...")

            done_event = {
                "event": "done",
                "answer": full_answer,
                "tokens_used": tokens_used
            }
            if conversation_id:
                done_event["conversation_id"] = conversation_id
            
            yield f'data: {json.dumps(done_event)}\n\n'
            
            # 记录日志
            meta = parse_answer_meta(full_answer)
            logger.info(f"[STREAM] 响应成功 | conversation_id={conversation_id} | "
                       f"Q={meta['q']} | dim_nb={meta['nb']} dim_bh={meta['bh']} dim_tf={meta['tf']} dim_ip={meta['ip']} | "
                       f"next_dim={meta['next_dim']} | can_conclude={meta['can_conclude']} | tokens={tokens_used}")
            logger.info(f"[STREAM] 响应正文预览 | answer_preview={full_answer[:80]}...")
        
        else:
            error_event = {
                "event": "error",
                "error": f"API 错误: {response.status_code}",
                "detail": response.text
            }
            if conversation_id:
                error_event["conversation_id"] = conversation_id
            yield f'data: {json.dumps(error_event)}\n\n'
            
    except Exception as e:
        error_event = {
            "event": "error",
            "error": str(e)
        }
        if conversation_id:
            error_event["conversation_id"] = conversation_id
        yield f'data: {json.dumps(error_event)}\n\n'
