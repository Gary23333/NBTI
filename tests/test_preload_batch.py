"""并行预载（/api/chat/preload/batch）、首题预热（/api/chat/warmup）与供应商/健康检查端点测试。

使用 mock LLM（patch nbti.app.http_client.post）避免真实网络调用。
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

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


def make_assess(q, next_dim="NB"):
    return json.dumps({
        "phase": "ASSESS", "q": q, "nb": 0, "bh": 0, "tf": 0, "ip": 0,
        "next_dim": next_dim, "can_conclude": False,
        "comment": "c", "scene": f"scene {q}", "options": ["A", "B", "C"]
    }, ensure_ascii=False)


def _llm_response(answer, tokens=42):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "choices": [{"message": {"content": answer}}],
        "usage": {"total_tokens": tokens},
    }
    return resp


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


class TestPreloadBatch:
    def test_batch_generates_and_persists_each_option(self, env):
        """3 个选项并发返回 3 份草稿且逐分支落库"""
        client, new_store = env
        conv_id = 'batch-conv-1'
        new_store._write(conv_id, {"history": [], "scenes": [], "preloads": {}})
        options = ["选项甲", "选项乙", "选项丙"]

        with patch('nbti.app.http_client.post',
                   side_effect=lambda *a, **k: _llm_response(make_assess(1))) as mock_post:
            resp = client.post('/api/chat/preload/batch',
                               content_type='application/json',
                               data=json.dumps({
                                   "conversation_id": conv_id,
                                   "options": options,
                                   "can_conclude": False
                               }))

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['conversation_id'] == conv_id
        results = data['results']
        assert set(results.keys()) == set(options)
        for opt in options:
            assert results[opt].get('answer')
            assert results[opt].get('tokens_used') == 42
            draft = new_store.get_preload_draft(conv_id, opt)
            assert draft is not None, f"draft missing for {opt}"
            assert json.loads(draft['answer'])['q'] == 1
        assert mock_post.call_count == 3

    def test_batch_can_conclude_prefixes_branch_message(self, env):
        """can_conclude=true 时分支消息带 [CAN_CONCLUDE:true] 前缀，落库键一致"""
        client, new_store = env
        conv_id = 'batch-conv-2'
        new_store._write(conv_id, {"history": [], "scenes": [], "preloads": {}})

        with patch('nbti.app.http_client.post',
                   side_effect=lambda *a, **k: _llm_response(make_assess(1))):
            resp = client.post('/api/chat/preload/batch',
                               content_type='application/json',
                               data=json.dumps({
                                   "conversation_id": conv_id,
                                   "options": ["甲"],
                                   "can_conclude": True
                               }))

        assert resp.status_code == 200
        assert new_store.get_preload_draft(conv_id, "[CAN_CONCLUDE:true] 甲") is not None

    def test_batch_single_option_failure_isolated(self, env):
        """单分支失败不影响其它分支，失败分支返回 error 字段"""
        client, new_store = env
        conv_id = 'batch-conv-3'
        new_store._write(conv_id, {"history": [], "scenes": [], "preloads": {}})

        def side_effect(*a, **k):
            body = k.get('json', {})
            content = body.get('messages', [])[-1].get('content', '')
            if '坏' in content:
                raise RuntimeError('boom')
            return _llm_response(make_assess(1))

        with patch('nbti.app.http_client.post', side_effect=side_effect):
            resp = client.post('/api/chat/preload/batch',
                               content_type='application/json',
                               data=json.dumps({
                                   "conversation_id": conv_id,
                                   "options": ["好A", "坏"]
                               }))

        assert resp.status_code == 200
        results = resp.get_json()['results']
        assert results['好A'].get('answer')
        assert 'error' in results['坏']
        assert new_store.get_preload_draft(conv_id, '好A') is not None
        assert new_store.get_preload_draft(conv_id, '坏') is None

    @pytest.mark.parametrize('cid', ['../../etc/passwd', 'a/b', 'has space'])
    def test_batch_rejects_invalid_id(self, env, cid):
        client, _ = env
        resp = client.post('/api/chat/preload/batch',
                           content_type='application/json',
                           data=json.dumps({"conversation_id": cid, "options": ["x"]}))
        assert resp.status_code == 400

    def test_batch_missing_options_returns_400(self, env):
        client, _ = env
        resp = client.post('/api/chat/preload/batch',
                           content_type='application/json',
                           data=json.dumps({"conversation_id": "batch-conv-4"}))
        assert resp.status_code == 400


class TestWarmup:
    def test_warmup_generates_first_draft_then_chat_hits_it(self, env):
        """warmup 生成首题草稿；随后 /api/chat 传 开始测试 命中草稿直接返回，不再调用 LLM"""
        client, new_store = env

        with patch('nbti.app.http_client.post',
                   side_effect=lambda *a, **k: _llm_response(make_assess(1))) as mock_warmup:
            resp = client.post('/api/chat/warmup',
                               content_type='application/json',
                               data=json.dumps({}))
        assert resp.status_code == 200
        data = resp.get_json()
        conv_id = data['conversation_id']
        assert conv_id
        assert data['answer']
        assert data['tokens_used'] == 42
        draft = new_store.get_preload_draft(conv_id, '开始测试')
        assert draft is not None
        assert mock_warmup.call_count == 1

        with patch('nbti.app.http_client.post',
                   side_effect=lambda *a, **k: _llm_response(make_assess(1))) as mock_chat:
            resp2 = client.post('/api/chat',
                                content_type='application/json',
                                data=json.dumps({"message": "开始测试", "conversation_id": conv_id}))
        assert resp2.status_code == 200
        body = resp2.get_json()
        assert body['answer'] == draft['answer']
        assert body['tokens_used'] == 42
        mock_chat.assert_not_called()          # 命中草稿，跳过重新生成
        history = new_store.get_history(conv_id)
        assert len(history) == 2
        assert json.loads(history[1]['content'])['q'] == 1

    def test_chat_start_without_draft_uses_llm(self, env):
        """无草稿时 /api/chat 行为不变：照常调用 LLM 生成首题"""
        client, new_store = env
        conv_id = 'nodraft-conv-1'
        new_store._write(conv_id, {"history": [], "scenes": [], "preloads": {}})

        with patch('nbti.app.http_client.post',
                   side_effect=lambda *a, **k: _llm_response(make_assess(1))) as mock_post:
            resp = client.post('/api/chat',
                               content_type='application/json',
                               data=json.dumps({"message": "开始测试", "conversation_id": conv_id}))

        assert resp.status_code == 200
        assert resp.get_json()['answer']
        assert mock_post.call_count == 1
        assert len(new_store.get_history(conv_id)) == 2

    def test_warmup_rejects_invalid_id(self, env):
        client, _ = env
        resp = client.post('/api/chat/warmup',
                           content_type='application/json',
                           data=json.dumps({"conversation_id": 'a/b'}))
        assert resp.status_code == 400


class TestProvidersAndHealth:
    def test_providers_metadata_without_secrets(self, env):
        """GET /api/providers 返回供应商元数据，且不含任何密钥"""
        client, _ = env
        resp = client.get('/api/providers')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list) and data
        ids = {p['vendor_id'] for p in data}
        assert 'openai_compatible' in ids
        assert 'doubao' in ids
        for p in data:
            assert p.get('vendor_id') and p.get('label')
            assert 'api_key' not in p
        assert 'sk-test' not in json.dumps(data)

    def test_health_has_old_and_new_fields(self, env):
        """GET /api/health 保留原字段并新增可观测字段"""
        client, _ = env
        resp = client.get('/api/health')
        assert resp.status_code == 200
        data = resp.get_json()
        for key in ['status', 'profiles', 'active_preset', 'themes_count', 'styles_count']:
            assert key in data
        for key in ['version', 'storage_backend', 'cache_enabled', 'fast_mode', 'providers_count']:
            assert key in data
        assert data['status'] == 'ok'
        assert data['providers_count'] >= 1
        assert isinstance(data['cache_enabled'], bool)
        assert isinstance(data['fast_mode'], bool)
        assert data['storage_backend'] in ('file', 'redis')
