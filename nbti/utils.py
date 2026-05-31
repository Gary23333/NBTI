import json
import re
import random
import logging

from nbti.conversation import store

logger = logging.getLogger(__name__)


def trim_history(history, max_messages=12):
    """Limit history length, keep most recent max_messages entries."""
    if len(history) > max_messages:
        return history[-max_messages:]
    return history


def parse_json_answer(answer):
    """尝试将 AI 回复解析为 JSON，支持多种包裹模式。失败返回 None"""
    text = answer.strip()
    if not text:
        return None

    def try_parse(s):
        """尝试解析 JSON，支持修复常见错误"""
        try:
            return json.loads(s)
        except (json.JSONDecodeError, ValueError):
            pass
        # 修复常见错误：多余括号、尾逗号
        try:
            fixed = re.sub(r',\s*([}\]])', r'\1', s)  # 去尾逗号
            # 修复 options 数组多余 ]：],"nb" -> ],"nb"
            fixed = re.sub(r'\]\s*\]', ']', fixed)
            return json.loads(fixed)
        except (json.JSONDecodeError, ValueError):
            pass
        return None

    # 模式1：直接裸 JSON
    if text.startswith('{'):
        result = try_parse(text)
        if result and isinstance(result, dict) and 'phase' in result:
            return result

    # 模式2：markdown 代码块包裹 ```json ... ``` 或 ``` ... ```
    m = re.search(r"```(?:json)?\s*\n(.*?)\n\s*```", text, re.DOTALL)
    if m:
        result = try_parse(m.group(1).strip())
        if result and isinstance(result, dict) and 'phase' in result:
            return result

    # 模式3：查找含有 "phase" 键的 JSON 对象（可能夹杂在其他文字中）
    m = re.search(r'\{\s*"phase"\s*:\s*"(?:ASSESS|RESULT)"[^}]*\}', text)
    if not m:
        # 更宽泛：首尾花括号匹配
        start = text.find('{')
        end = text.rfind('}')
        if start >= 0 and end > start:
            m = re.search(r'\{.*\}', text[start:end+1], re.DOTALL)
    if m:
        result = try_parse(m.group(0))
        if result and isinstance(result, dict) and 'phase' in result:
            return result

    return None


def extract_scene_summary(answer):
    """从 AI 回复中提取场景描述摘要（用于题目去重，JSON 优先）"""
    # 先尝试 JSON 解析（使用增强版 parse_json_answer）
    data = parse_json_answer(answer)
    if data and isinstance(data, dict) and data.get('phase') == 'ASSESS':
        scene = data.get('scene', '')
        if scene:
            return scene[:40].strip()

    return None


def count_questions(history):
    max_q = 0
    for msg in history:
        if msg.get('role') != 'assistant':
            continue
        data = parse_json_answer(msg.get('content', ''))
        if data and isinstance(data, dict) and data.get('q'):
            q = int(data['q'])
            if q > max_q:
                max_q = q
    return max_q


def expected_next_question(history):
    return count_questions(history) + 1


def inject_question_control(system_prompt, expected_q):
    if not expected_q:
        return system_prompt

    control = f"""

## 本地题号控制（最高优先级）
- 本轮必须输出 q={expected_q}。
- 严禁自行推断、重复或跳过题号。
- JSON 字段 q 必须是数字 {expected_q}。

## 输出长度控制（必须遵守！）
- 整个 JSON 回复控制在 400 字以内
- comment ≤ 35 字
- scene ≤ 80 字
- 每个 option ≤ 10 字
- 不要输出多余字段
"""
    return system_prompt + control


def next_dimension_for_question(q):
    dims = ["NB", "BH", "TF", "IP"]
    return dims[(max(q, 1) - 1) % len(dims)]


def normalize_options(value):
    raw = value
    if isinstance(raw, str):
        stripped = raw.strip()
        if stripped.startswith('['):
            try:
                raw = json.loads(stripped)
            except (json.JSONDecodeError, ValueError):
                raw = []
        else:
            raw = [item.strip() for item in stripped.replace('，', ',').replace('、', ',').split(',')]

    if not isinstance(raw, list):
        return []

    flattened = []

    def collect(items):
        for item in items:
            if isinstance(item, list):
                collect(item)
            elif isinstance(item, str):
                text = item.strip()
                if len(text) >= 2 and text[0].upper() in 'ABCD' and text[1] in '.、 ':
                    text = text[2:].strip()
                if text:
                    flattened.append(text)

    collect(raw)
    return flattened[:4]


def normalize_answer_question(answer, expected_q, config=None):
    data = parse_json_answer(answer)
    if not isinstance(data, dict) or data.get('phase') != 'ASSESS':
        if not isinstance(data, dict) or data.get('phase') != 'RESULT':
            logger.warning(f"[NORMALIZE] 无法解析或非 ASSESS 阶段 | expected_q={expected_q} | answer_preview={str(answer)[:100]}...")
        return answer

    if expected_q:
        from nbti.config import load_config
        original_q = data.get('q')
        data['q'] = expected_q
        if original_q != expected_q:
            logger.warning(f"[Q_CONTROL] 覆盖模型题号 | original_q={original_q} | expected_q={expected_q}")

        if config is None:
            config = load_config()
        min_questions = int(config.get("min_questions", 20))
        max_questions = int(config.get("max_questions", 25))
        original_next_dim = data.get('next_dim')
        original_can_conclude = data.get('can_conclude')
        valid_dims = {"NB", "BH", "TF", "IP", "END"}
        next_dim = data.get('next_dim')
        expected_dim = next_dimension_for_question(expected_q)
        should_correct = False
        if next_dim not in valid_dims:
            should_correct = True
        elif next_dim != 'END' and next_dim != expected_dim:
            if expected_q < min_questions:
                should_correct = True
            elif not data.get('can_conclude'):
                should_correct = True
        if should_correct:
            data['next_dim'] = expected_dim
            logger.warning(f"[Q_CONTROL] 修正异常 next_dim | original_next_dim={next_dim} | expected_q={expected_q} | corrected_to={expected_dim}")

        if expected_q < min_questions:
            data['can_conclude'] = False
            if original_next_dim == 'END' or original_can_conclude:
                logger.warning(f"[Q_CONTROL] 拦截过早结束 | q={expected_q} | min_questions={min_questions}")
        elif expected_q >= max_questions:
            data['can_conclude'] = True
            data['next_dim'] = 'END'

    data['options'] = normalize_options(data.get('options'))

    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


def is_complete_assess(answer, expected_q=None):
    data = parse_json_answer(answer)
    if not isinstance(data, dict) or data.get('phase') != 'ASSESS':
        return False
    if expected_q and data.get('q') != expected_q:
        return False
    scene = data.get('scene')
    options = normalize_options(data.get('options'))
    return isinstance(scene, str) and bool(scene.strip()) and 2 <= len(options) <= 4


def parse_answer_meta(answer):
    """从 AI 回复中解析结构化元信息（JSON 优先，利用 parse_json_answer）
    返回: {q, nb, bh, tf, ip, next_dim, can_conclude, phase}
    """
    meta = {
        'q': None, 'nb': None, 'bh': None, 'tf': None, 'ip': None,
        'next_dim': None, 'can_conclude': None, 'phase': None
    }

    # 先尝试 JSON 解析（使用增强版 parse_json_answer）
    data = parse_json_answer(answer)
    if data and isinstance(data, dict):
        meta['phase'] = data.get('phase')
        meta['q'] = data.get('q')
        for dim in ['nb', 'bh', 'tf', 'ip']:
            if dim in data:
                meta[dim] = data[dim]
        meta['next_dim'] = data.get('next_dim')
        cc = data.get('can_conclude')
        if isinstance(cc, bool):
            meta['can_conclude'] = cc
        elif isinstance(cc, str):
            meta['can_conclude'] = cc.lower() == 'true'
        return meta

    return meta


def commit_answer_to_history(conversation_id, message, answer, phase=None):
    with store.lock:
        data = store._read(conversation_id)
        history = data.get('history', [])
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": answer})
        data['history'] = history

        answer_meta = parse_answer_meta(answer)
        answer_phase = phase or answer_meta.get('phase')
        if answer_phase == 'assess' or answer_phase == 'ASSESS':
            scene_summary = extract_scene_summary(answer)
            if scene_summary:
                scenes = data.get('scenes', [])
                if scene_summary not in scenes:
                    scenes.append(scene_summary)
                    data['scenes'] = scenes

        store._write(conversation_id, data)


def check_easter_egg(scores, config):
    """根据四维分数判断是否触发彩蛋人格"""
    if not config.get('easter_egg_enabled', True):
        return None

    eggs = config.get('easter_eggs', {})
    nb = scores.get('nb', 0)
    bh = scores.get('bh', 0)
    tf = scores.get('tf', 0)
    ip = scores.get('ip', 0)

    # 四维度全0 → 薛定谔的打工人
    if nb == 0 and bh == 0 and tf == 0 and ip == 0:
        if random.randint(1, 100) <= eggs.get('schrodinger', 1):
            return 'schrodinger'

    # 四维度都≥+4 → 六边形战士
    if nb >= 4 and bh >= 4 and tf >= 4 and ip >= 4:
        if random.randint(1, 100) <= eggs.get('hexagon', 3):
            return 'hexagon'

    # 四维度都≤-4 → 职场活佛
    if nb <= -4 and bh <= -4 and tf <= -4 and ip <= -4:
        if random.randint(1, 100) <= eggs.get('buddha', 3):
            return 'buddha'

    # 某两维度差≥9 → 职场双面人
    dims = [nb, bh, tf, ip]
    for i in range(len(dims)):
        for j in range(i + 1, len(dims)):
            if abs(dims[i] - dims[j]) >= 9:
                if random.randint(1, 100) <= eggs.get('double', 3):
                    return 'twoface'

    return None
