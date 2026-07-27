"""P0 安全修复回归测试：配置脱敏、管理鉴权、SSRF 防护、conversation_id 路径穿越防护"""

import json
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nbti.config as nbti_config
from nbti.app import create_app
from nbti.conversation import is_valid_conversation_id
from conftest import make_minimal_config


@pytest.fixture
def env(tmp_path, monkeypatch):
    """隔离环境：CONFIG_FILE 指向 tmp_path，默认清除 NBTI_ADMIN_TOKEN"""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(make_minimal_config()), encoding='utf-8')
    monkeypatch.setattr(nbti_config, 'CONFIG_FILE', str(config_path))
    monkeypatch.delenv('NBTI_ADMIN_TOKEN', raising=False)
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client(), config_path


def _post_config(client, headers=None):
    return client.post('/api/config',
                       content_type='application/json',
                       data=json.dumps(make_minimal_config()),
                       headers=headers or {})


class TestConfigMasking:
    def test_get_config_masks_api_key_for_non_admin(self, env, monkeypatch):
        """非管理员 GET /api/config：api_key 被掩码，不泄露明文"""
        client, _ = env
        monkeypatch.setenv('NBTI_ADMIN_TOKEN', 'secret-token')
        resp = client.get('/api/config')
        assert resp.status_code == 200
        data = resp.get_json()
        key = data['llm_profiles'][0]['api_key']
        assert key == '***test'  # sk-test 仅保留后 4 位
        assert 'sk-test' not in json.dumps(data)

    def test_get_config_returns_full_for_admin(self, env, monkeypatch):
        """管理员（正确 token）GET /api/config：返回完整配置"""
        client, _ = env
        monkeypatch.setenv('NBTI_ADMIN_TOKEN', 'secret-token')
        resp = client.get('/api/config', headers={'X-Admin-Token': 'secret-token'})
        assert resp.status_code == 200
        assert resp.get_json()['llm_profiles'][0]['api_key'] == 'sk-test'

    def test_masking_rules(self, env, monkeypatch):
        """掩码规则：空串保持空串，长度≤4 全掩码，否则保留后 4 位"""
        client, config_path = env
        monkeypatch.setenv('NBTI_ADMIN_TOKEN', 'secret-token')
        config = make_minimal_config()
        config['llm_profiles'] = [
            {"name": "empty", "vendor": "openai", "model": "m", "api_key": "", "base_url": "https://x.example.com"},
            {"name": "short", "vendor": "openai", "model": "m", "api_key": "abc", "base_url": "https://x.example.com"},
            {"name": "four", "vendor": "openai", "model": "m", "api_key": "abcd", "base_url": "https://x.example.com"},
        ]
        config_path.write_text(json.dumps(config), encoding='utf-8')
        data = client.get('/api/config').get_json()
        keys = {p['name']: p['api_key'] for p in data['llm_profiles']}
        assert keys['empty'] == ''
        assert keys['short'] == '***'
        assert keys['four'] == '***'


class TestAdminAuth:
    def test_post_config_unauthorized_without_token(self, env, monkeypatch):
        """设置 NBTI_ADMIN_TOKEN 后：无 token POST /api/config → 401"""
        client, _ = env
        monkeypatch.setenv('NBTI_ADMIN_TOKEN', 'secret-token')
        resp = _post_config(client)
        assert resp.status_code == 401
        assert resp.get_json() == {"error": "unauthorized"}

    def test_post_config_with_correct_token(self, env, monkeypatch):
        """带正确 token → 200"""
        client, _ = env
        monkeypatch.setenv('NBTI_ADMIN_TOKEN', 'secret-token')
        resp = _post_config(client, headers={'X-Admin-Token': 'secret-token'})
        assert resp.status_code == 200
        assert resp.get_json()['success'] is True

    def test_post_config_with_wrong_token(self, env, monkeypatch):
        """带错误 token → 401"""
        client, _ = env
        monkeypatch.setenv('NBTI_ADMIN_TOKEN', 'secret-token')
        resp = _post_config(client, headers={'X-Admin-Token': 'wrong-token'})
        assert resp.status_code == 401
        assert resp.get_json() == {"error": "unauthorized"}

    def test_reset_requires_admin(self, env, monkeypatch):
        client, _ = env
        monkeypatch.setenv('NBTI_ADMIN_TOKEN', 'secret-token')
        resp = client.post('/api/config/reset')
        assert resp.status_code == 401
        assert resp.get_json() == {"error": "unauthorized"}

    def test_test_connection_requires_admin(self, env, monkeypatch):
        client, _ = env
        monkeypatch.setenv('NBTI_ADMIN_TOKEN', 'secret-token')
        resp = client.post('/api/config/test-connection',
                           content_type='application/json',
                           data=json.dumps({"base_url": "https://x.example.com", "api_key": "k", "model": "m"}))
        assert resp.status_code == 401
        assert resp.get_json() == {"error": "unauthorized"}

    def test_localhost_write_allowed_when_token_unset(self, env):
        """未设置 NBTI_ADMIN_TOKEN 时，本机请求（test_client 默认 127.0.0.1）写配置仍可用"""
        client, _ = env
        resp = _post_config(client)
        assert resp.status_code == 200
        assert resp.get_json()['success'] is True

    def test_spoofed_xff_public_ip_is_not_admin(self, env):
        """伪造 X-Forwarded-For 为公网 IP → 不再视为本机管理员"""
        client, _ = env
        resp = _post_config(client, headers={'X-Forwarded-For': '8.8.8.8'})
        assert resp.status_code == 401
        resp = client.get('/api/config', headers={'X-Forwarded-For': '8.8.8.8'})
        assert resp.get_json()['llm_profiles'][0]['api_key'] == '***test'


class TestConversationIdValidation:
    def test_is_valid_conversation_id(self):
        assert is_valid_conversation_id('abc-DEF_123') is True
        for bad in ['', '../x', 'a/b', 'a\\b', 'a b', '..', 'x' * 65, None, 123]:
            assert is_valid_conversation_id(bad) is False

    @pytest.mark.parametrize('cid', ['../../etc/passwd', 'a/b', 'has space', 'a\\b', '..', 'x' * 65])
    def test_chat_rejects_invalid_id(self, env, cid):
        client, _ = env
        resp = client.post('/api/chat',
                           content_type='application/json',
                           data=json.dumps({"message": "hi", "conversation_id": cid}))
        assert resp.status_code == 400

    @pytest.mark.parametrize('cid', ['../../etc/passwd', 'a/b', 'has space'])
    def test_preload_rejects_invalid_id(self, env, cid):
        client, _ = env
        resp = client.post('/api/chat/preload',
                           content_type='application/json',
                           data=json.dumps({"message": "hi", "conversation_id": cid}))
        assert resp.status_code == 400

    @pytest.mark.parametrize('cid', ['../../etc/passwd', 'a/b', 'has space'])
    def test_preload_commit_rejects_invalid_id(self, env, cid):
        client, _ = env
        resp = client.post('/api/chat/preload/commit',
                           content_type='application/json',
                           data=json.dumps({"message": "hi", "conversation_id": cid}))
        assert resp.status_code == 400


class TestTestConnectionSSRF:
    @pytest.mark.parametrize('url', ['file:///etc/passwd', 'gopher://x', 'ftp://example.com', 'not-a-url'])
    def test_rejects_invalid_base_url(self, env, url):
        """非 http/https scheme 或无 hostname → 400"""
        client, _ = env
        resp = client.post('/api/config/test-connection',
                           content_type='application/json',
                           data=json.dumps({"base_url": url, "api_key": "k", "model": "m"}))
        assert resp.status_code == 400

    def test_allows_lan_http_url(self, env):
        """局域网 http 地址（LM Studio 合法用途）不被误杀"""
        client, _ = env
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"model": "gemma"}
        with patch('nbti.app.requests.post', return_value=mock_resp) as mock_post:
            resp = client.post('/api/config/test-connection',
                               content_type='application/json',
                               data=json.dumps({"base_url": "http://192.168.5.22:1234", "api_key": "lm-studio", "model": "gemma"}))
        assert resp.status_code == 200
        assert resp.get_json()['success'] is True
        assert mock_post.called
