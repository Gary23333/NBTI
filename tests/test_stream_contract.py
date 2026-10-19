"""SSE 流式契约测试（nbti/llm.py stream_generator + /api/chat?stream=1）。

用 mock（patch nbti.http_client.post）断言事件序列含 first_token/chunk/done，
字段与既有约定一致（first_token.timestamp、chunk.content、done.answer/conversation_id/tokens_used），
并验证残缺答案不入库、完整答案入库。
"""

import json
import os
import sys
from unittest.mock import patch

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
    """模拟 httpx 流式响应：逐 chunk 输出 data 行，以 [DONE] 结束。"""

    def __init__(self, chunks, status_code=200, usage=None):
        self.status_code = status_code
        self._chunks = chunks
        self._usage = usage
        self.encoding = 'utf-8'
        self.text = ''.join(chunks)

    def iter_lines(self, decode_unicode=True):
        for i, chunk in enumerate(self._chunks):
            payload = {"choices": [{"delta": {"content": chunk}}]}
            if self._usage is not None and i == len(self._chunks) - 1:
                payload["usage"] = self._usage
            yield f'data: {json.dumps(payload, ensure_ascii=False)}'
        yield 'data: [DONE]'


def make_assess(q, next_dim="NB"):
    return json.dumps({
        "phase": "ASSESS", "q": q, "nb": 0, "bh": 0, "tf": 0, "ip": 0,
        "next_dim": next_dim, "can_conclude": False,
        "comment": "c", "scene": f"scene {q}", "options": ["A", "B", "C"]
    }, ensure_ascii=False)


def parse_sse(text):
    """把 SSE 文本解析为事件 dict 列表。"""
    events = []
    for block in text.split("\n\n"):
        block = block.strip()
        if block.startswith("data: "):
            events.append(json.loads(block[6:]))
    return events


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
    return app.test_client(), new_store


class TestStreamEventContract:
    def test_event_sequence_and_fields(self, env):
        """完整答案：事件序列为 first_token → chunk* → done，字段符合既有约定。"""
        client, new_store = env
        conv_id = "stream-contract-1"
        new_store.save_history(conv_id, [])
        answer = make_assess(1)

        with patch('nbti.http_client.post',
                   return_value=MockStreamResponse([answer[:20], answer[20:]])):
            resp = client.post('/api/chat?stream=1', content_type='application/json',
                               data=json.dumps({"message": "开始测试", "conversation_id": conv_id}))

        assert resp.status_code == 200
        assert resp.mimetype == 'text/event-stream'

        events = parse_sse(resp.get_data(as_text=True))
        kinds = [e["event"] for e in events]
        assert kinds[0] == "first_token"
        assert "chunk" in kinds
        assert kinds[-1] == "done"
        assert kinds.count("first_token") == 1                 # 首个内容 chunk 只发一次

        # first_token：timestamp 为毫秒整数
        assert isinstance(events[0]["timestamp"], int)

        # chunk：content 拼接还原完整答案（chunk 为上游原始增量）
        chunks = [e for e in events if e["event"] == "chunk"]
        assert "".join(c["content"] for c in chunks) == answer

        # done：answer / conversation_id / tokens_used
        done = events[-1]
        # done.answer 经 normalize_answer_question 规范化（紧凑 JSON），语义应与原始答案等价
        assert json.loads(done["answer"]) == json.loads(answer)
        assert done["conversation_id"] == conv_id
        assert isinstance(done["tokens_used"], int)

    def test_tokens_used_propagated_from_usage(self, env):
        """最后一个 chunk 携带 usage.total_tokens 时透传到 done 事件。"""
        client, new_store = env
        conv_id = "stream-contract-2"
        new_store.save_history(conv_id, [])
        answer = make_assess(1)

        with patch('nbti.http_client.post',
                   return_value=MockStreamResponse([answer], usage={"total_tokens": 99})):
            resp = client.post('/api/chat?stream=1', content_type='application/json',
                               data=json.dumps({"message": "开始测试", "conversation_id": conv_id}))

        done = parse_sse(resp.get_data(as_text=True))[-1]
        assert done["event"] == "done"
        assert done["tokens_used"] == 99

    def test_incomplete_answer_not_persisted(self, env):
        """残缺答案：done 事件照常发送，但历史不入库。"""
        client, new_store = env
        conv_id = "stream-contract-bad"
        new_store.save_history(conv_id, [])

        with patch('nbti.http_client.post',
                   return_value=MockStreamResponse(['{"phase": "ASSESS", "q": 1, "com'])):
            resp = client.post('/api/chat?stream=1', content_type='application/json',
                               data=json.dumps({"message": "开始测试", "conversation_id": conv_id}))

        events = parse_sse(resp.get_data(as_text=True))
        assert events[-1]["event"] == "done"
        assert new_store.get_history(conv_id) == []

    def test_complete_answer_persisted(self, env):
        """完整答案：done 事件前已落库，历史新增 user + assistant 两条。"""
        client, new_store = env
        conv_id = "stream-contract-ok"
        new_store.save_history(conv_id, [])
        answer = make_assess(1)

        with patch('nbti.http_client.post',
                   return_value=MockStreamResponse([answer[:30], answer[30:]])):
            resp = client.post('/api/chat?stream=1', content_type='application/json',
                               data=json.dumps({"message": "开始测试", "conversation_id": conv_id}))

        assert parse_sse(resp.get_data(as_text=True))[-1]["event"] == "done"
        history = new_store.get_history(conv_id)
        assert len(history) == 2
        assert history[0] == {"role": "user", "content": "开始测试"}
        assert json.loads(history[1]["content"])["q"] == 1

    def test_error_event_on_non_200(self, env):
        """上游非 200：发出 error 事件（含 error 字段），不发 done。"""
        client, new_store = env
        conv_id = "stream-contract-err"
        new_store.save_history(conv_id, [])

        with patch('nbti.http_client.post',
                   return_value=MockStreamResponse([], status_code=500)):
            resp = client.post('/api/chat?stream=1', content_type='application/json',
                               data=json.dumps({"message": "开始测试", "conversation_id": conv_id}))

        events = parse_sse(resp.get_data(as_text=True))
        assert events[0]["event"] == "error"
        assert "error" in events[0]
        assert all(e["event"] != "done" for e in events)
        assert new_store.get_history(conv_id) == []
