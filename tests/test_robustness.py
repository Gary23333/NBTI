"""P1 健壮性修复测试：IP 限流 429 与恢复、流式残缺答案不入库、trim_history 生效"""

import json
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nbti.config as nbti_config
import nbti.conversation as nbti_conversation
import nbti.utils as nbti_utils
import nbti.llm as nbti_llm
import nbti.app as nbti_app
from nbti.app import create_app, _rate_limiter
from nbti.conversation import ConversationStore
from conftest import make_minimal_config


class MockStreamResponse:
    """模拟 SSE 流式响应：按 chunk 逐段输出后以 [DONE] 结束"""

    def __init__(self, chunks, status_code=200):
        self.status_code = status_code
        self.text = ''.join(chunks)
        self._chunks = chunks
        self.encoding = None

    def iter_lines(self, decode_unicode=True):
        for c in self._chunks:
            yield f'data: {json.dumps({"choices": [{"delta": {"content": c}}]})}'
        yield 'data: [DONE]'


def make_assess(q, next_dim="NB"):
    return json.dumps({
        "phase": "ASSESS", "q": q, "nb": 0, "bh": 0, "tf": 0, "ip": 0,
        "next_dim": next_dim, "can_conclude": False,
        "comment": "c", "scene": f"scene {q}", "options": ["A", "B", "C"]
    }, ensure_ascii=False)


def make_result():
    return json.dumps({
        "phase": "RESULT", "type": "NBTF", "name": "测试人格", "oneline": "一句话",
        "scene": "s", "adapt": "a", "crash": "c",
        "interpretation": "i" * 90, "pseudo_science": "p" * 90, "closing": "end"
    }, ensure_ascii=False)


def make_history(rounds):
    """构造 rounds 轮完整对话历史（2*rounds 条）"""
    history = []
    for i in range(1, rounds + 1):
        history.append({"role": "user", "content": f"answer {i}"})
        history.append({"role": "assistant", "content": make_assess(i)})
    return history


@pytest.fixture
def env(tmp_path, monkeypatch):
    """隔离环境：tmp config + tmp store（替换各模块 store 引用）+ 重置限流器"""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(make_minimal_config()), encoding='utf-8')
    monkeypatch.setattr(nbti_config, 'CONFIG_FILE', str(config_path))
    new_store = ConversationStore(str(tmp_path / 'conv'))
    monkeypatch.setattr(nbti_conversation, 'store', new_store)
    monkeypatch.setattr(nbti_utils, 'store', new_store)
    monkeypatch.setattr(nbti_llm, 'store', new_store)
    monkeypatch.setattr(nbti_app, 'store', new_store)
    _rate_limiter.reset()
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client(), config_path, new_store


def _set_rate_limit(config_path, limit):
    config = json.loads(config_path.read_text(encoding='utf-8'))
    config['rate_limit_per_minute'] = limit
    config_path.write_text(json.dumps(config), encoding='utf-8')


def _mock_llm_500():
    """非流式请求快速返回 500，避免真实网络调用"""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = 'mock error'
    return mock_resp


class TestRateLimit:
    def test_exceed_returns_429(self, env):
        """超过 rate_limit_per_minute 后返回 429 + retry_after"""
        client, config_path, _ = env
        _set_rate_limit(config_path, 2)
        body = json.dumps({"message": "hi", "conversation_id": "rl-test-1"})
        with patch('nbti.app.requests.post', return_value=_mock_llm_500()):
            r1 = client.post('/api/chat', content_type='application/json', data=body)
            r2 = client.post('/api/chat', content_type='application/json', data=body)
            r3 = client.post('/api/chat', content_type='application/json', data=body)
        assert r1.status_code == 500 and r2.status_code == 500  # 前两次放行（LLM mock 失败但非限流）
        assert r3.status_code == 429
        data = r3.get_json()
        assert data['error'] == 'rate_limited'
        assert 0 < data['retry_after'] <= 60

    def test_reset_restores_access(self, env):
        """_rate_limiter.reset() 后立即恢复访问"""
        client, config_path, _ = env
        _set_rate_limit(config_path, 1)
        body = json.dumps({"message": "hi", "conversation_id": "rl-test-2"})
        with patch('nbti.app.requests.post', return_value=_mock_llm_500()):
            assert client.post('/api/chat', content_type='application/json', data=body).status_code == 500
            assert client.post('/api/chat', content_type='application/json', data=body).status_code == 429
            _rate_limiter.reset()
            assert client.post('/api/chat', content_type='application/json', data=body).status_code == 500

    def test_window_expiry_recovers(self, env):
        """滑动窗口过期（最早记录超过 60s）后自动恢复"""
        client, config_path, _ = env
        _set_rate_limit(config_path, 1)
        body = json.dumps({"message": "hi", "conversation_id": "rl-test-3"})
        with patch('nbti.app.requests.post', return_value=_mock_llm_500()):
            assert client.post('/api/chat', content_type='application/json', data=body).status_code == 500
            assert client.post('/api/chat', content_type='application/json', data=body).status_code == 429
            # 将窗口内记录回拨 61s，模拟窗口过期
            with _rate_limiter._lock:
                for key in _rate_limiter._hits:
                    _rate_limiter._hits[key] = [t - 61 for t in _rate_limiter._hits[key]]
            assert client.post('/api/chat', content_type='application/json', data=body).status_code == 500

    def test_zero_limit_means_unlimited(self, env):
        """rate_limit_per_minute=0 时不限流"""
        client, config_path, _ = env
        _set_rate_limit(config_path, 0)
        body = json.dumps({"message": "hi", "conversation_id": "rl-test-4"})
        with patch('nbti.app.requests.post', return_value=_mock_llm_500()):
            for _ in range(40):
                resp = client.post('/api/chat', content_type='application/json', data=body)
                assert resp.status_code == 500

    def test_limit_is_per_ip(self, env):
        """不同 IP（经可信代理 XFF）独立计数"""
        client, config_path, _ = env
        _set_rate_limit(config_path, 1)
        body = json.dumps({"message": "hi", "conversation_id": "rl-test-5"})
        with patch('nbti.app.requests.post', return_value=_mock_llm_500()):
            assert client.post('/api/chat', content_type='application/json', data=body,
                               headers={'X-Forwarded-For': '1.2.3.4'}).status_code == 500
            assert client.post('/api/chat', content_type='application/json', data=body,
                               headers={'X-Forwarded-For': '1.2.3.4'}).status_code == 429
            # 另一个 IP 不受 1.2.3.4 限流影响
            assert client.post('/api/chat', content_type='application/json', data=body,
                               headers={'X-Forwarded-For': '5.6.7.8'}).status_code == 500

    def test_preload_commit_also_limited(self, env):
        """preload/commit 端点同样被限流覆盖"""
        client, config_path, _ = env
        _set_rate_limit(config_path, 1)
        body = json.dumps({"message": "hi", "conversation_id": "rl-test-6"})
        r1 = client.post('/api/chat/preload/commit', content_type='application/json', data=body)
        r2 = client.post('/api/chat/preload/commit', content_type='application/json', data=body)
        assert r1.status_code == 404  # 无 draft，但已消耗配额
        assert r2.status_code == 429


class TestStreamCommit:
    def test_incomplete_assess_not_committed(self, env):
        """流式输出残缺 JSON 时跳过入库，done 事件照常发送"""
        client, _, new_store = env
        conv_id = 'stream-bad-1'
        new_store.save_history(conv_id, [])
        with patch('nbti.llm.requests.post',
                   return_value=MockStreamResponse(['{"phase": "ASSESS", "q": 1, "com'])):
            resp = client.post('/api/chat?stream=1', content_type='application/json',
                               data=json.dumps({"message": "开始测试", "conversation_id": conv_id}))
        assert resp.status_code == 200
        assert '"event": "done"' in resp.get_data(as_text=True)
        assert new_store.get_history(conv_id) == []

    def test_complete_assess_committed(self, env):
        """流式输出完整 ASSESS JSON 时正常入库"""
        client, _, new_store = env
        conv_id = 'stream-ok-1'
        new_store.save_history(conv_id, [])
        answer = make_assess(1)
        with patch('nbti.llm.requests.post',
                   return_value=MockStreamResponse([answer[:30], answer[30:]])):
            resp = client.post('/api/chat?stream=1', content_type='application/json',
                               data=json.dumps({"message": "开始测试", "conversation_id": conv_id}))
        assert resp.status_code == 200
        assert '"event": "done"' in resp.get_data(as_text=True)
        history = new_store.get_history(conv_id)
        assert len(history) == 2
        assert json.loads(history[1]['content'])['q'] == 1

    def test_incomplete_result_not_committed(self, env):
        """result 阶段残缺输出不入库"""
        client, _, new_store = env
        conv_id = 'stream-res-1'
        new_store.save_history(conv_id, make_history(1))
        with patch('nbti.llm.requests.post',
                   return_value=MockStreamResponse(['{"phase": "RESULT", "type": "NB'])):
            resp = client.post('/api/chat?stream=1', content_type='application/json',
                               data=json.dumps({"message": "[PHASE:RESULT]", "conversation_id": conv_id}))
        assert resp.status_code == 200
        assert '"event": "done"' in resp.get_data(as_text=True)
        assert len(new_store.get_history(conv_id)) == 2  # 仅预置历史，未新增

    def test_complete_result_committed(self, env):
        """result 阶段完整 RESULT JSON 正常入库"""
        client, _, new_store = env
        conv_id = 'stream-res-2'
        new_store.save_history(conv_id, make_history(1))
        result = make_result()
        with patch('nbti.llm.requests.post',
                   return_value=MockStreamResponse([result[:40], result[40:]])):
            resp = client.post('/api/chat?stream=1', content_type='application/json',
                               data=json.dumps({"message": "[PHASE:RESULT]", "conversation_id": conv_id}))
        assert resp.status_code == 200
        assert '"event": "done"' in resp.get_data(as_text=True)
        history = new_store.get_history(conv_id)
        assert len(history) == 4
        assert json.loads(history[3]['content'])['phase'] == 'RESULT'


class TestTrimHistory:
    def test_chat_trims_history_to_12(self, env):
        """/api/chat 发给 LLM 的 messages = system + 最近12条 + 当前消息；落库仍是完整历史"""
        client, _, new_store = env
        conv_id = 'trim-chat-1'
        full = make_history(15)  # 30 条
        new_store.save_history(conv_id, full)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": make_assess(1)}}],  # 故意给错 q，验证题号纠正
            "usage": {"total_tokens": 10}
        }
        with patch('nbti.app.requests.post', return_value=mock_resp) as mock_post:
            resp = client.post('/api/chat', content_type='application/json',
                               data=json.dumps({"message": "pick A", "conversation_id": conv_id}))
        assert resp.status_code == 200
        sent = mock_post.call_args.kwargs['json']
        msgs = sent['messages']
        assert len(msgs) == 1 + 12 + 1  # system + 最近12条历史 + 当前 user message
        assert msgs[0]['role'] == 'system'
        assert msgs[1] == full[-12]  # 保留的是最近 12 条
        assert msgs[-1] == {"role": "user", "content": "pick A"}
        # expected_q 基于完整历史（15 轮 → 第 16 题）：normalize 强制 q=16
        assert json.loads(resp.get_json()['answer'])['q'] == 16
        # store 中保存完整历史 + 本轮新增
        assert len(new_store.get_history(conv_id)) == 30 + 2

    def test_preload_trims_history_to_12(self, env):
        """/api/chat/preload 同样裁剪 messages"""
        client, _, new_store = env
        conv_id = 'trim-preload-1'
        full = make_history(15)
        new_store.save_history(conv_id, full)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": make_assess(16)}}],
            "usage": {"total_tokens": 10}
        }
        with patch('nbti.app.requests.post', return_value=mock_resp) as mock_post:
            resp = client.post('/api/chat/preload', content_type='application/json',
                               data=json.dumps({"message": "pick A", "conversation_id": conv_id}))
        assert resp.status_code == 200
        sent = mock_post.call_args.kwargs['json']
        msgs = sent['messages']
        assert len(msgs) == 1 + 12 + 1
        assert msgs[1] == full[-12]
        # 完整历史不受影响（draft 不落 history）
        assert len(new_store.get_history(conv_id)) == 30
