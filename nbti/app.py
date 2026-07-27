"""NBTI Flask app factory with all routes registered"""

import copy
import os
import time
import uuid
import logging
import threading
import requests
from urllib.parse import urlparse
from flask import Flask, request, jsonify, send_from_directory, Response

from nbti.config import (
    load_config, save_config, find_profile_for_phase, find_profile,
    get_model_for_phase, _migrate_old_config, DEFAULT_CONFIG, CONFIG_FILE
)
from nbti.conversation import store, is_valid_conversation_id, ConversationStore
from nbti.llm import (
    build_thinking_params, build_response_format, get_chat_completions_url,
    stream_generator
)
from nbti.utils import (
    normalize_answer_question, parse_answer_meta, normalize_options,
    expected_next_question, inject_question_control, is_complete_assess,
    commit_answer_to_history, extract_scene_summary, trim_history
)
from nbti.themes import get_themes, THEMES
from nbti.prompts import get_prompt, get_prompt_presets, ALL_STYLES

logger = logging.getLogger(__name__)

STATIC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_LOCAL_IPS = ('127.0.0.1', '::1')


class ShareStore(ConversationStore):
    """分享快照存储：复用会话的文件 JSON 模式（id 字符集校验 + 原子写），快照整体读写"""

    def save_snapshot(self, share_id, snapshot):
        with self.lock:
            self._write(share_id, snapshot)

    def get_snapshot(self, share_id):
        data = self._read(share_id)
        return data or None


share_store = ShareStore(os.path.join(STATIC_DIR, 'data', 'shares'))

# 分享快照 result 各字段长度上限（字符数），scores 取值范围 ±99
_SHARE_RESULT_LIMITS = {
    'type': 16, 'name': 32, 'oneline': 128,
    'scene': 256, 'adapt': 256, 'crash': 256,
    'interpretation': 2000, 'pseudo_science': 2000, 'closing': 512,
}
_SHARE_SCORE_KEYS = ('nb', 'bh', 'tf', 'ip')


def _sanitize_share_payload(data):
    """校验并规范化分享快照：result 必须为 dict，字段缺省空串并按上限截断；scores 四键转 int 并 clamp ±99。
    合法返回 (result, scores)，非法返回 None"""
    if not isinstance(data, dict):
        return None
    result = data.get('result')
    if not isinstance(result, dict):
        return None
    clean_result = {}
    for key, limit in _SHARE_RESULT_LIMITS.items():
        value = result.get(key, '')
        if not isinstance(value, str):
            value = str(value)
        clean_result[key] = value[:limit]
    scores = data.get('scores')
    if not isinstance(scores, dict):
        scores = {}
    clean_scores = {}
    for key in _SHARE_SCORE_KEYS:
        try:
            value = int(scores.get(key, 0))
        except (TypeError, ValueError):
            value = 0
        clean_scores[key] = max(-99, min(99, value))
    return clean_result, clean_scores


def _client_ip():
    """获取真实客户端 IP：仅当直连对端是本机（前端代理）时才信任 X-Forwarded-For"""
    remote = request.remote_addr or ''
    if remote in _LOCAL_IPS:
        xff = request.headers.get('X-Forwarded-For', '')
        if xff:
            return xff.split(',')[0].strip()
    return remote


def _is_admin_request():
    """判定是否为管理员：携带正确的 X-Admin-Token；未配置 NBTI_ADMIN_TOKEN 时仅本机请求视为管理员"""
    admin_token = os.environ.get('NBTI_ADMIN_TOKEN', '')
    if admin_token:
        return request.headers.get('X-Admin-Token', '') == admin_token
    return _client_ip() in _LOCAL_IPS


def _unauthorized():
    return jsonify({"error": "unauthorized"}), 401


def _mask_config(config):
    """深拷贝配置并掩码所有 profile 的 api_key：空串保持空串，长度≤4 全掩码，否则仅保留后 4 位"""
    masked = copy.deepcopy(config)
    for p in masked.get('llm_profiles', []):
        key = p.get('api_key', '')
        if key:
            p['api_key'] = '***' + key[-4:] if len(key) > 4 else '***'
    return masked


def _invalid_conversation_id(conversation_id):
    """非空且非法的 conversation_id 判定（空 id 走各端点现有逻辑）"""
    return bool(conversation_id) and not is_valid_conversation_id(conversation_id)


def _normalize_theme_id(theme_id):
    """theme 来自客户端/会话文件，不可信：仅接受已知字符串 id，其余回退 workplace。
    dict/list 等不可哈希值会在 get_prompt 的 `theme_id not in THEMES` 处抛 TypeError。"""
    if isinstance(theme_id, str) and theme_id in THEMES:
        return theme_id
    return 'workplace'


def _parse_chat_body(data):
    """校验聊天端点请求体：必须为 JSON object；message 强制转 str（客户端可伪造任意类型）。
    非法返回 None（各端点据此返回 400），合法返回 (message, data)"""
    if not isinstance(data, dict):
        return None
    message = data.get('message', '')
    if not isinstance(message, str):
        message = str(message)
    return message, data


class _RateLimiter:
    """IP 级滑动窗口限流器（进程内 dict + 锁，仅适配单 worker 部署，见 gunicorn.conf.py）"""

    def __init__(self):
        self._hits = {}
        self._lock = threading.Lock()

    def check(self, key, limit, window=60):
        """记录一次访问；超限返回 (False, retry_after 秒)，否则 (True, 0)。limit<=0 表示不限"""
        if limit <= 0:
            return True, 0
        now = time.time()
        with self._lock:
            # key 只增不删会随独立 IP 数无限膨胀：超阈值时惰性全量驱逐窗口外记录
            if len(self._hits) > 1000:
                self._hits = {
                    k: v for k, v in
                    ((k, [t for t in v if now - t < window]) for k, v in self._hits.items()) if v
                }
            hits = [t for t in self._hits.get(key, []) if now - t < window]
            if len(hits) >= limit:
                retry_after = max(1, int(window - (now - hits[0])) + 1)
                self._hits[key] = hits
                return False, retry_after
            hits.append(now)
            self._hits[key] = hits
            return True, 0

    def reset(self):
        """清空限流状态（测试隔离用）"""
        with self._lock:
            self._hits.clear()


_rate_limiter = _RateLimiter()


def _rate_limit_exceeded(config):
    """按 config.rate_limit_per_minute 对当前 IP 限流（默认 30 次/分钟，0=不限）；超限返回 429 响应，否则 None"""
    limit = int(config.get('rate_limit_per_minute', 30))
    allowed, retry_after = _rate_limiter.check(_client_ip(), limit)
    if allowed:
        return None
    logger.warning(f"[RATE_LIMIT] 触发限流 | ip={_client_ip()} | limit={limit}/min | retry_after={retry_after}s")
    return jsonify({"error": "rate_limited", "retry_after": retry_after}), 429


_cleanup_thread_lock = threading.Lock()
_cleanup_thread_started = False


def _cleanup_loop():
    """后台守护循环：每小时清理一次超过 24h 未更新的会话文件与超过 30 天的分享快照"""
    while True:
        time.sleep(3600)
        try:
            removed = store.cleanup_old(24)
            logger.info(f"[CLEANUP] 定期清理完成 | removed={removed}")
        except Exception as e:
            logger.warning(f"[CLEANUP] 定期清理异常: {e}")
        try:
            removed = share_store.cleanup_old(30 * 24)
            logger.info(f"[CLEANUP] 分享快照定期清理完成 | removed={removed}")
        except Exception as e:
            logger.warning(f"[CLEANUP] 分享快照定期清理异常: {e}")


def ensure_cleanup_thread():
    """启动会话清理守护线程（幂等：进程内仅启动一次；gunicorn preload 下 fork 后需在 post_worker_init 再次调用）"""
    global _cleanup_thread_started
    with _cleanup_thread_lock:
        if _cleanup_thread_started:
            return
        thread = threading.Thread(target=_cleanup_loop, daemon=True, name='nbti-cleanup')
        thread.start()
        _cleanup_thread_started = True


def create_app():
    app = Flask(__name__)

    # 启动时清理一次过期会话（>24h）与过期分享快照（>30天），并启动后台定时清理线程（幂等）
    removed = store.cleanup_old(24)
    if removed:
        logger.info(f"[CLEANUP] 启动清理完成 | removed={removed}")
    removed = share_store.cleanup_old(30 * 24)
    if removed:
        logger.info(f"[CLEANUP] 分享快照启动清理完成 | removed={removed}")
    ensure_cleanup_thread()

    # ---- Health check ----
    @app.route('/api/health', methods=['GET'])
    def health():
        config = load_config()
        return jsonify({
            "status": "ok",
            "profiles": len(config.get("llm_profiles", [])),
            "active_preset": config.get("active_preset", ""),
            "themes_count": len(get_themes()),
            "styles_count": len(ALL_STYLES),
            "version": "3.0.0-multitheme"
        })

    # ---- Themes & Styles endpoints ----
    @app.route('/api/themes', methods=['GET'])
    def themes():
        return jsonify(get_themes())

    @app.route('/api/styles', methods=['GET'])
    def styles():
        return jsonify(ALL_STYLES)

    def _get_dynamic_prompt(theme_id, style_name, phase, **kwargs):
        prompts = get_prompt(theme_id, style_name)
        prompt_key = f'prompt_{phase}'
        prompt_template = prompts[prompt_key]
        if callable(prompt_template):
            return prompt_template(**kwargs)
        else:
            result = prompt_template
            for k, v in kwargs.items():
                result = result.replace('{' + k + '}', str(v))
            return result

    # ---- Chat endpoints ----
    @app.route('/api/chat', methods=['POST'])
    def chat():
        parsed_body = _parse_chat_body(request.json)
        if parsed_body is None:
            return jsonify({"error": "Invalid JSON body"}), 400
        message, data = parsed_body
        conversation_id = data.get('conversation_id', '')
        if _invalid_conversation_id(conversation_id):
            logger.warning(f"[CHAT] 非法 conversation_id: {conversation_id!r}")
            return jsonify({"error": "Invalid conversation_id"}), 400
        config = load_config()
        limited = _rate_limit_exceeded(config)
        if limited:
            return limited

        use_stream = request.args.get('stream') == '1'
        logger.info(f"[CHAT] id={conversation_id} | msg={message[:50]}... | stream={use_stream}")

        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            store.save_history(conversation_id, [])

        is_new_session = message in ['开始测试', '开始'] or not store.get_history(conversation_id)
        theme_id = data.get('theme', 'workplace')
        style_name = data.get('style', '暴躁老油条')
        
        if is_new_session:
            theme_id = _normalize_theme_id(theme_id)
            store.set_theme(conversation_id, theme_id)
            store.set_style(conversation_id, style_name)
        else:
            theme_id = _normalize_theme_id(store.get_theme(conversation_id))
            style_name = store.get_style(conversation_id)

        history = store.get_history(conversation_id)
        expected_q = None

        eggs = config.get('easter_eggs', {})
        egg_params = {f'easter_{key}': str(eggs.get(key, 1)) for key in ['schrodinger', 'hexagon', 'buddha', 'double', 'mouthpiece']}

        if is_new_session:
            phase = 'init'
            expected_q = 1
            system_prompt = _get_dynamic_prompt(theme_id, style_name, 'init')
        elif '[PHASE:RESULT]' in message or '[CAN_CONCLUDE:true]' in message:
            phase = 'result'
            system_prompt = _get_dynamic_prompt(theme_id, style_name, 'result', **egg_params)
        else:
            phase = 'assess'
            expected_q = expected_next_question(history)
            scenes = store.get_scenes(conversation_id)
            if scenes:
                scenes_text = '\n'.join([f"- {s}" for s in scenes])
            else:
                scenes_text = '（暂无，你是第一题）'
            min_q = int(config.get("min_questions", 20))
            max_q = int(config.get("max_questions", 25))
            system_prompt = _get_dynamic_prompt(
                theme_id, style_name, 'assess',
                previous_scenes=scenes_text,
                min_questions=str(min_q),
                min_questions_minus_1=str(min_q - 1),
                max_questions=str(max_q)
            )

        if phase in ['init', 'assess']:
            system_prompt = inject_question_control(system_prompt, expected_q)

        # 发给 LLM 的上下文只带最近 12 条历史，降低 token 膨胀；题号统计与落库仍基于完整 history
        messages = [{"role": "system", "content": system_prompt}]
        for msg in trim_history(history):
            if msg.get("role") != "system":
                messages.append(msg)
        messages.append({"role": "user", "content": message})

        profile = find_profile_for_phase(config, phase)
        if not profile:
            logger.error(f"[CHAT] 无可用 LLM profile | phase={phase}")
            return jsonify({"error": "No LLM profile configured", "conversation_id": conversation_id}), 500

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {profile['api_key']}"
        }

        payload = {
            "model": profile['model'],
            "messages": messages,
            "temperature": profile.get('temperature', 0.9),
            "max_tokens": profile.get('max_tokens', 2000)
        }
        if expected_q:
            payload['_expected_q'] = expected_q

        thinking_params = build_thinking_params(profile)
        payload.update(thinking_params)
        rf = build_response_format(profile, phase)
        if rf:
            payload.update(rf)

        logger.info(f"[CHAT] call LLM | phase={phase} | q={expected_q} | profile={profile.get('name')} | model={profile['model']}")

        if use_stream:
            return Response(
                stream_generator(profile, payload, conversation_id, history, message, phase, save_history=True, config=config),
                mimetype='text/event-stream',
                headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
            )
        else:
            try:
                response = requests.post(
                    get_chat_completions_url(profile),
                    headers=headers,
                    json={k: v for k, v in payload.items() if not k.startswith('_')},
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    answer = result['choices'][0]['message']['content']
                    answer = normalize_answer_question(answer, expected_q, config)
                    tokens_used = result.get('usage', {}).get('total_tokens', 0)
                    meta = parse_answer_meta(answer)
                    logger.info(f"[CHAT] OK | Q={meta['q']} | tokens={tokens_used}")
                    commit_answer_to_history(conversation_id, message, answer, phase)
                    return jsonify({"answer": answer, "conversation_id": conversation_id, "tokens_used": tokens_used})
                else:
                    logger.error(f"[CHAT] API error {response.status_code}")
                    return jsonify({"error": f"API error: {response.status_code}", "detail": response.text, "conversation_id": conversation_id}), 500
            except Exception as e:
                logger.error(f"[CHAT] Exception: {e}")
                return jsonify({"error": str(e), "conversation_id": conversation_id}), 500

    @app.route('/api/chat/preload', methods=['POST'])
    def preload():
        parsed_body = _parse_chat_body(request.json)
        if parsed_body is None:
            return jsonify({"error": "Invalid JSON body"}), 400
        message, data = parsed_body
        conversation_id = data.get('conversation_id', '')
        if _invalid_conversation_id(conversation_id):
            logger.warning(f"[PRELOAD] 非法 conversation_id: {conversation_id!r}")
            return jsonify({"error": "Invalid conversation_id"}), 400
        config = load_config()
        limited = _rate_limit_exceeded(config)
        if limited:
            return limited

        use_stream = request.args.get('stream') == '1'
        logger.info(f"[PRELOAD] id={conversation_id} | msg={message[:50]}...")

        history = list(store.get_history(conversation_id)) if conversation_id else []
        expected_q = None

        if conversation_id:
            theme_id = _normalize_theme_id(store.get_theme(conversation_id))
            style_name = store.get_style(conversation_id)
        else:
            theme_id = _normalize_theme_id(data.get('theme', 'workplace'))
            style_name = data.get('style', '暴躁老油条')

        eggs = config.get('easter_eggs', {})
        egg_params = {f'easter_{key}': str(eggs.get(key, 1)) for key in ['schrodinger', 'hexagon', 'buddha', 'double', 'mouthpiece']}

        if '[PHASE:RESULT]' in message or '[CAN_CONCLUDE:true]' in message:
            phase = 'result'
            system_prompt = _get_dynamic_prompt(theme_id, style_name, 'result', **egg_params)
        else:
            phase = 'assess'
            expected_q = expected_next_question(history)
            scenes = store.get_scenes(conversation_id) if conversation_id else []
            if scenes:
                scenes_text = '\n'.join([f"- {s}" for s in scenes])
            else:
                scenes_text = '（暂无，你是第一题）'
            min_q = int(config.get("min_questions", 20))
            max_q = int(config.get("max_questions", 25))
            system_prompt = _get_dynamic_prompt(
                theme_id, style_name, 'assess',
                previous_scenes=scenes_text,
                min_questions=str(min_q),
                min_questions_minus_1=str(min_q - 1),
                max_questions=str(max_q)
            )

        if phase == 'assess':
            system_prompt = inject_question_control(system_prompt, expected_q)

        # 发给 LLM 的上下文只带最近 12 条历史，降低 token 膨胀；题号统计与落库仍基于完整 history
        messages = [{"role": "system", "content": system_prompt}]
        for msg in trim_history(history):
            if msg.get("role") != "system":
                messages.append(msg)
        messages.append({"role": "user", "content": message})

        profile = find_profile_for_phase(config, phase)
        if not profile:
            logger.error(f"[PRELOAD] 无可用 LLM profile | phase={phase}")
            return jsonify({"error": "No LLM profile configured"}), 500

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {profile['api_key']}"
        }

        payload = {
            "model": profile['model'],
            "messages": messages,
            "temperature": profile.get('temperature', 0.9),
            "max_tokens": profile.get('max_tokens', 2000)
        }
        if expected_q:
            payload['_expected_q'] = expected_q

        thinking_params = build_thinking_params(profile)
        payload.update(thinking_params)
        rf = build_response_format(profile, phase)
        if rf:
            payload.update(rf)

        if use_stream:
            return Response(
                stream_generator(profile, payload, conversation_id, config=config),
                mimetype='text/event-stream',
                headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
            )
        else:
            try:
                response = requests.post(
                    get_chat_completions_url(profile),
                    headers=headers,
                    json={k: v for k, v in payload.items() if not k.startswith('_')},
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    answer = result['choices'][0]['message']['content']
                    answer = normalize_answer_question(answer, expected_q, config)
                    tokens_used = result.get('usage', {}).get('total_tokens', 0)
                    meta = parse_answer_meta(answer)
                    logger.info(f"[PRELOAD] OK | Q={meta['q']} | tokens={tokens_used}")
                    if conversation_id and message:
                        if meta.get('phase') == 'ASSESS' and not is_complete_assess(answer, expected_q):
                            logger.warning(f"[PRELOAD] Discard incomplete draft")
                        else:
                            store.save_preload_draft(conversation_id, message, answer, tokens_used)
                    return jsonify({"answer": answer, "tokens_used": tokens_used})
                else:
                    logger.error(f"[PRELOAD] API error {response.status_code}")
                    return jsonify({"error": f"API error: {response.status_code}", "detail": response.text}), 500
            except Exception as e:
                logger.error(f"[PRELOAD] Exception: {e}")
                return jsonify({"error": str(e)}), 500

    @app.route('/api/chat/preload/commit', methods=['POST'])
    def commit_preload():
        limited = _rate_limit_exceeded(load_config())
        if limited:
            return limited
        data = request.json
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON body"}), 400
        message = data.get('message', '')
        if not isinstance(message, str):
            message = str(message)
        conversation_id = data.get('conversation_id', '')

        if not conversation_id or not message:
            return jsonify({"error": "Missing conversation_id or message"}), 400
        if not is_valid_conversation_id(conversation_id):
            logger.warning(f"[PRELOAD_COMMIT] 非法 conversation_id: {conversation_id!r}")
            return jsonify({"error": "Invalid conversation_id"}), 400

        draft = store.get_preload_draft(conversation_id, message)
        if not draft:
            return jsonify({"error": "Preload draft not found or expired", "conversation_id": conversation_id}), 404

        answer = draft.get('answer', '')
        tokens_used = draft.get('tokens_used', 0)
        history = store.get_history(conversation_id)
        meta = parse_answer_meta(answer)
        expected_q = expected_next_question(history)
        if meta.get('phase') == 'ASSESS' and not is_complete_assess(answer, expected_q):
            logger.warning(f"[PRELOAD_COMMIT] Reject incomplete draft | q={expected_q} | Q={meta.get('q')}")
            return jsonify({"error": "Preload draft incomplete or expired", "conversation_id": conversation_id}), 409

        answer_phase = 'result' if meta.get('phase') == 'RESULT' else 'assess'
        commit_answer_to_history(conversation_id, message, answer, answer_phase)
        store.clear_preloads(conversation_id)

        logger.info(f"[PRELOAD_COMMIT] OK | Q={meta['q']} | phase={meta['phase']}")
        return jsonify({"answer": answer, "conversation_id": conversation_id, "tokens_used": tokens_used, "committed": True})

    @app.route('/api/chat/stream', methods=['POST'])
    def chat_stream():
        from werkzeug.datastructures import MultiDict
        request.args = MultiDict([('stream', '1')])
        return chat()

    @app.route('/api/chat/preload/stream', methods=['POST'])
    def preload_stream():
        from werkzeug.datastructures import MultiDict
        request.args = MultiDict([('stream', '1')])
        return preload()

    # ---- Config endpoints ----
    @app.route('/api/config', methods=['GET'])
    def get_config():
        config = load_config()
        if _is_admin_request():
            return jsonify(config)
        masked = _mask_config(config)
        masked['_readonly'] = True
        return jsonify(masked)

    @app.route('/api/config', methods=['POST'])
    def update_config():
        if not _is_admin_request():
            logger.warning(f"[CONFIG] 未授权的配置写请求 | ip={_client_ip()}")
            return _unauthorized()
        config = request.json
        config = _migrate_old_config(config)
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        save_config(config)
        logger.info(f"[CONFIG] Updated")
        return jsonify({"success": True})

    @app.route('/api/config/test-connection', methods=['POST'])
    def test_connection():
        if not _is_admin_request():
            logger.warning(f"[CONFIG] 未授权的 test-connection 请求 | ip={_client_ip()}")
            return _unauthorized()
        data = request.json
        if not data:
            return jsonify({"error": "Missing profile data"}), 400

        base_url = data.get('base_url', '')
        api_key = data.get('api_key', '')
        model = data.get('model', '')
        vendor = data.get('vendor', '')

        if not base_url or not api_key:
            return jsonify({"error": "Missing base_url or api_key"}), 400

        # SSRF 防护：仅允许 http/https 且必须有 hostname（不封禁内网 IP，局域网 LM Studio 属合法用途）
        parsed = urlparse(base_url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname:
            logger.warning(f"[CONFIG] test-connection 非法 base_url: {base_url!r}")
            return jsonify({"error": "Invalid base_url: only http/https URLs are allowed"}), 400

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 1
        }

        try:
            test_profile = {"base_url": base_url, "vendor": vendor}
            resp = requests.post(
                get_chat_completions_url(test_profile),
                headers=headers, json=payload, timeout=15
            )
            if resp.status_code == 200:
                result = resp.json()
                model_used = result.get('model', model)
                return jsonify({"success": True, "model": model_used, "message": f"Connected! Model: {model_used}"})
            elif resp.status_code in (401, 403):
                return jsonify({"success": False, "error": f"Auth failed ({resp.status_code})"}), 200
            else:
                return jsonify({"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}), 200
        except requests.exceptions.Timeout:
            return jsonify({"success": False, "error": "Timeout (15s)"}), 200
        except requests.exceptions.ConnectionError:
            return jsonify({"success": False, "error": "Cannot connect to server"}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 200

    @app.route('/api/config/reset', methods=['POST'])
    def reset_config():
        if not _is_admin_request():
            logger.warning(f"[CONFIG] 未授权的配置重置请求 | ip={_client_ip()}")
            return _unauthorized()
        save_config(DEFAULT_CONFIG)
        logger.info("[CONFIG] Reset to defaults")
        return jsonify({"success": True})

    # ---- Stats endpoint ----
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        conv_dir = store.base_dir
        total = 0
        if os.path.exists(conv_dir):
            total = len([f for f in os.listdir(conv_dir) if f.endswith('.json')])
        config = load_config()
        return jsonify({
            "total_conversations": total,
            "active_preset": config.get("active_preset", ""),
            "profiles_count": len(config.get("llm_profiles", []))
        })

    # ---- Share endpoints ----
    # 分享是公开功能：无需管理鉴权，也不依赖 conversation
    @app.route('/api/share', methods=['POST'])
    def create_share():
        config = load_config()
        limited = _rate_limit_exceeded(config)
        if limited:
            return limited
        parsed = _sanitize_share_payload(request.json)
        if not parsed:
            logger.warning(f"[SHARE] 非法快照结构 | ip={_client_ip()}")
            return jsonify({"error": "Invalid share payload"}), 400
        result, scores = parsed
        share_id = uuid.uuid4().hex[:8]
        snapshot = {"result": result, "scores": scores, "created_at": int(time.time())}
        share_store.save_snapshot(share_id, snapshot)
        logger.info(f"[SHARE] 创建快照 | id={share_id} | type={result.get('type')}")
        return jsonify({"id": share_id})

    @app.route('/api/share/<share_id>', methods=['GET'])
    def get_share(share_id):
        if not is_valid_conversation_id(share_id):
            logger.warning(f"[SHARE] 非法 share_id: {share_id!r}")
            return jsonify({"error": "Share not found"}), 404
        snapshot = share_store.get_snapshot(share_id)
        if not snapshot:
            return jsonify({"error": "Share not found"}), 404
        return jsonify(snapshot)

    return app
