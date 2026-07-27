"""系统性 BUG 审查回归测试：
- chat/preload 的 theme_id 合法性（dict/list 等不可哈希类型曾导致 TypeError 500 并毒化会话文件）
- 请求体类型加固（非 dict JSON body、非 str message 曾导致 500）
- 无可用 LLM profile 时返回 JSON 错误而非未捕获异常
- _RateLimiter 过期 key 惰性驱逐（内存随独立 IP 无界增长）
- ConversationStore._read 容忍非法 UTF-8 的损坏会话文件
"""

import json
import os
import sys
import time
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nbti.config as nbti_config
import nbti.conversation as nbti_conversation
import nbti.utils as nbti_utils
import nbti.llm as nbti_llm
import nbti.app as nbti_app
from nbti.app import create_app, _RateLimiter
from nbti.conversation import ConversationStore
from conftest import make_minimal_config


@pytest.fixture
def env(tmp_path, monkeypatch):
    """隔离环境：tmp config + tmp store（替换各模块 store 引用）"""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(make_minimal_config()), encoding='utf-8')
    monkeypatch.setattr(nbti_config, 'CONFIG_FILE', str(config_path))
    new_store = ConversationStore(str(tmp_path / 'conv'))
    monkeypatch.setattr(nbti_conversation, 'store', new_store)
    monkeypatch.setattr(nbti_utils, 'store', new_store)
    monkeypatch.setattr(nbti_llm, 'store', new_store)
    monkeypatch.setattr(nbti_app, 'store', new_store)
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client(), config_path, new_store


def make_assess(q, next_dim="NB"):
    return json.dumps({
        "phase": "ASSESS", "q": q, "nb": 0, "bh": 0, "tf": 0, "ip": 0,
        "next_dim": next_dim, "can_conclude": False,
        "comment": "c", "scene": f"scene {q}", "options": ["A", "B", "C"]
    }, ensure_ascii=False)


def _mock_llm_ok(answer):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": answer}}],
        "usage": {"total_tokens": 10}
    }
    return mock_resp


class TestThemeValidation:
    @pytest.mark.parametrize('bad_theme', [{'evil': 1}, ['x'], 123, 'not-a-theme'])
    def test_chat_invalid_theme_falls_back_to_workplace(self, env, bad_theme):
        """新会话携带非法 theme（不可哈希类型/未知 id）→ 回退 workplace，不 500，且不落库非法值"""
        client, _, new_store = env
        conv_id = 'theme-bad-new'
        with patch('nbti.app.requests.post', return_value=_mock_llm_ok(make_assess(1))):
            resp = client.post('/api/chat', content_type='application/json',
                               data=json.dumps({"message": "开始测试", "conversation_id": conv_id,
                                                "theme": bad_theme}))
        assert resp.status_code == 200
        assert new_store.get_theme(conv_id) == 'workplace'
        # 后续轮次从会话文件读 theme，同样不崩溃
        with patch('nbti.app.requests.post', return_value=_mock_llm_ok(make_assess(2))):
            resp2 = client.post('/api/chat', content_type='application/json',
                                data=json.dumps({"message": "A", "conversation_id": conv_id}))
        assert resp2.status_code == 200

    def test_chat_valid_theme_preserved(self, env):
        """合法 theme 不受影响，正常落库"""
        client, _, new_store = env
        with patch('nbti.app.requests.post', return_value=_mock_llm_ok(make_assess(1))):
            resp = client.post('/api/chat', content_type='application/json',
                               data=json.dumps({"message": "开始测试", "conversation_id": "theme-ok-1",
                                                "theme": "animal"}))
        assert resp.status_code == 200
        assert new_store.get_theme('theme-ok-1') == 'animal'

    def test_chat_poisoned_stored_theme_no_crash(self, env):
        """会话文件中被毒化的 theme（dict）在后续请求读取时回退 workplace，不 500"""
        client, _, new_store = env
        conv_id = 'theme-bad-stored'
        new_store._write(conv_id, {"history": [
            {"role": "user", "content": "开始测试"},
            {"role": "assistant", "content": make_assess(1)}
        ], "theme": {"evil": 1}})
        with patch('nbti.app.requests.post', return_value=_mock_llm_ok(make_assess(2))):
            resp = client.post('/api/chat', content_type='application/json',
                               data=json.dumps({"message": "A", "conversation_id": conv_id}))
        assert resp.status_code == 200

    def test_preload_invalid_theme_in_body_falls_back(self, env):
        """preload 无 conversation_id 时 body 里的非法 theme 回退 workplace，不 500"""
        client, _, _ = env
        with patch('nbti.app.requests.post', return_value=_mock_llm_ok(make_assess(1))):
            resp = client.post('/api/chat/preload', content_type='application/json',
                               data=json.dumps({"message": "A", "conversation_id": "", "theme": ["x"]}))
        assert resp.status_code == 200

    def test_preload_poisoned_stored_theme_no_crash(self, env):
        """preload 读取被毒化的会话 theme 时不 500"""
        client, _, new_store = env
        conv_id = 'theme-bad-preload'
        new_store._write(conv_id, {"history": [], "theme": {"evil": 1}})
        with patch('nbti.app.requests.post', return_value=_mock_llm_ok(make_assess(1))):
            resp = client.post('/api/chat/preload', content_type='application/json',
                               data=json.dumps({"message": "A", "conversation_id": conv_id}))
        assert resp.status_code == 200


class TestRequestBodyHardening:
    @pytest.mark.parametrize('body', ['null', '[1, 2]', '"str"', '42'])
    def test_chat_rejects_non_dict_json_body(self, env, body):
        """非 JSON object 的请求体 → 400，而不是 AttributeError 500"""
        client, _, _ = env
        resp = client.post('/api/chat', content_type='application/json', data=body)
        assert resp.status_code == 400
        assert resp.get_json()['error'] == 'Invalid JSON body'

    @pytest.mark.parametrize('body', ['null', '[1, 2]'])
    def test_preload_rejects_non_dict_json_body(self, env, body):
        client, _, _ = env
        resp = client.post('/api/chat/preload', content_type='application/json', data=body)
        assert resp.status_code == 400
        assert resp.get_json()['error'] == 'Invalid JSON body'

    def test_preload_commit_rejects_non_dict_json_body(self, env):
        client, _, _ = env
        resp = client.post('/api/chat/preload/commit', content_type='application/json', data='null')
        assert resp.status_code == 400
        assert resp.get_json()['error'] == 'Invalid JSON body'

    def test_chat_coerces_non_string_message(self, env):
        """message 为数字时强制转 str，正常走流程（曾因地日志切片 message[:50] 抛 TypeError）"""
        client, _, new_store = env
        with patch('nbti.app.requests.post', return_value=_mock_llm_ok(make_assess(1))):
            resp = client.post('/api/chat', content_type='application/json',
                               data=json.dumps({"message": 123, "conversation_id": "msg-type-1"}))
        assert resp.status_code == 200
        history = new_store.get_history('msg-type-1')
        assert history[0]['content'] == '123'

    def test_preload_commit_coerces_unhashable_message(self, env):
        """message 为 dict（不可哈希）时不再在 preloads.get 处抛 TypeError，按草稿不存在 404"""
        client, _, _ = env
        resp = client.post('/api/chat/preload/commit', content_type='application/json',
                           data=json.dumps({"message": {"x": 1}, "conversation_id": "msg-type-2"}))
        assert resp.status_code == 404


class TestNoLlmProfile:
    def _empty_profiles(self, config_path):
        config = json.loads(config_path.read_text(encoding='utf-8'))
        config['llm_profiles'] = []
        config_path.write_text(json.dumps(config), encoding='utf-8')

    def test_chat_returns_json_error(self, env):
        """llm_profiles 为空时 find_profile_for_phase 返回 None：返回 JSON 500 而非未捕获 TypeError"""
        client, config_path, _ = env
        self._empty_profiles(config_path)
        resp = client.post('/api/chat', content_type='application/json',
                           data=json.dumps({"message": "开始测试", "conversation_id": "noprof-1"}))
        assert resp.status_code == 500
        assert resp.get_json()['error'] == 'No LLM profile configured'

    def test_preload_returns_json_error(self, env):
        client, config_path, _ = env
        self._empty_profiles(config_path)
        resp = client.post('/api/chat/preload', content_type='application/json',
                           data=json.dumps({"message": "A", "conversation_id": "noprof-2"}))
        assert resp.status_code == 500
        assert resp.get_json()['error'] == 'No LLM profile configured'


class TestRateLimiterEviction:
    def test_stale_keys_evicted_when_growing(self):
        """_hits 超过 1000 个 key 时，惰性全量驱逐窗口外记录，防止内存无界增长"""
        limiter = _RateLimiter()
        now = time.time()
        with limiter._lock:
            for i in range(1001):
                limiter._hits[f'stale-{i}'] = [now - 120]  # 均已滑出 60s 窗口
        allowed, _ = limiter.check('new-ip', 1)
        assert allowed
        with limiter._lock:
            assert set(limiter._hits.keys()) == {'new-ip'}

    def test_fresh_keys_survive_eviction(self):
        """驱逐只清窗口外记录，仍在窗口内的 key 计数不受影响"""
        limiter = _RateLimiter()
        now = time.time()
        with limiter._lock:
            for i in range(1001):
                limiter._hits[f'stale-{i}'] = [now - 120]
            limiter._hits['active-ip'] = [now]  # 窗口内
        allowed, _ = limiter.check('active-ip', 1)
        assert not allowed  # 窗口内已有一次 → 触发限流，证明记录未被误清
        with limiter._lock:
            assert 'active-ip' in limiter._hits
            assert not any(k.startswith('stale-') for k in limiter._hits)


class TestStoreReadRobustness:
    def test_read_tolerates_invalid_utf8(self, tmp_path):
        """会话文件含非法 UTF-8（如崩溃截断写入）时按空数据处理，不抛 UnicodeDecodeError"""
        store = ConversationStore(str(tmp_path))
        (tmp_path / 'bad-utf8.json').write_bytes(b'\xff\xfe not json \xe4\xb8')
        assert store.get_history('bad-utf8') == []
        assert store.get_theme('bad-utf8') == 'workplace'

    def test_read_tolerates_truncated_json(self, tmp_path):
        """JSON 语法损坏（截断）仍按空数据处理（原有行为，防回归）"""
        store = ConversationStore(str(tmp_path))
        (tmp_path / 'truncated.json').write_text('{"history": [', encoding='utf-8')
        assert store.get_history('truncated') == []
