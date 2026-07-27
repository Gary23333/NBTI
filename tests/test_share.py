"""分享快照 API 测试：创建/读取一致性、缺省与截断、scores 兜底、非法 id、限流"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nbti.config as nbti_config
import nbti.app as nbti_app
from nbti.app import create_app
from nbti.conversation import is_valid_conversation_id
from conftest import make_minimal_config


@pytest.fixture
def env(tmp_path, monkeypatch):
    """隔离环境：分享存储目录与 CONFIG_FILE 指向 tmp_path"""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(make_minimal_config()), encoding='utf-8')
    monkeypatch.setattr(nbti_config, 'CONFIG_FILE', str(config_path))
    monkeypatch.setattr(nbti_app, 'share_store', nbti_app.ShareStore(str(tmp_path / 'shares')))
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client(), config_path


def _make_payload():
    return {
        "result": {
            "type": "NBTI", "name": "卷王", "oneline": "不是在卷，就是在去卷的路上",
            "scene": "凌晨三点的钉钉", "adapt": "项目经理", "crash": "团建破冰",
            "interpretation": "你的字典里没有下班", "pseudo_science": "水星逆行导致你加班",
            "closing": "卷就完事了",
        },
        "scores": {"nb": 8, "bh": -5, "tf": 3, "ip": 10},
    }


def _post_share(client, payload):
    return client.post('/api/share', content_type='application/json', data=json.dumps(payload))


class TestShareCreateAndGet:
    def test_create_then_get_roundtrip(self, env):
        """POST 创建 → GET 内容一致（result 全字段 + scores + created_at）"""
        client, _ = env
        payload = _make_payload()
        resp = _post_share(client, payload)
        assert resp.status_code == 200
        share_id = resp.get_json()['id']
        assert isinstance(share_id, str) and len(share_id) == 8
        assert is_valid_conversation_id(share_id)

        resp = client.get(f'/api/share/{share_id}')
        assert resp.status_code == 200
        snap = resp.get_json()
        assert snap['result'] == payload['result']
        assert snap['scores'] == payload['scores']
        assert isinstance(snap['created_at'], int)

    def test_get_not_found(self, env):
        """GET 不存在 id → 404"""
        client, _ = env
        resp = client.get('/api/share/abcd1234')
        assert resp.status_code == 404

    @pytest.mark.parametrize('bad_id', ['../x', 'a/b', 'a' * 65])
    def test_get_invalid_id(self, env, bad_id):
        """GET 非法 id（路径穿越/含斜杠/超长）→ 404/400"""
        client, _ = env
        resp = client.get(f'/api/share/{bad_id}')
        assert resp.status_code in (400, 404)


class TestShareSanitize:
    def test_missing_fields_default_and_truncate(self, env):
        """POST 缺字段 → 缺省空串；超长字段 → 按上限截断；scores 越界 → clamp ±99"""
        client, _ = env
        payload = {
            "result": {
                "type": "N" * 100,
                "oneline": "哦" * 200,
                "interpretation": "长" * 3000,
            },
            "scores": {"nb": 150, "bh": -300},
        }
        resp = _post_share(client, payload)
        assert resp.status_code == 200
        share_id = resp.get_json()['id']

        snap = client.get(f'/api/share/{share_id}').get_json()
        r = snap['result']
        assert r['type'] == 'N' * 16
        assert r['oneline'] == '哦' * 128
        assert r['interpretation'] == '长' * 2000
        # 未提供字段缺省空串
        for key in ['name', 'scene', 'adapt', 'crash', 'pseudo_science', 'closing']:
            assert r[key] == ''
        assert snap['scores'] == {"nb": 99, "bh": -99, "tf": 0, "ip": 0}

    def test_scores_coercion_fallback(self, env):
        """scores 非数字 → 转 int 兜底（字符串数字可转，其余归 0；浮点取整）"""
        client, _ = env
        payload = {"result": {}, "scores": {"nb": "7", "bh": "x", "tf": None, "ip": 3.9}}
        resp = _post_share(client, payload)
        assert resp.status_code == 200
        share_id = resp.get_json()['id']
        snap = client.get(f'/api/share/{share_id}').get_json()
        assert snap['scores'] == {"nb": 7, "bh": 0, "tf": 0, "ip": 3}

    def test_invalid_payload_structure(self, env):
        """result 缺失或非 dict → 400"""
        client, _ = env
        resp = _post_share(client, {"scores": {}})
        assert resp.status_code == 400
        resp = _post_share(client, {"result": "nope", "scores": {}})
        assert resp.status_code == 400


class TestShareRateLimit:
    def test_rate_limit_triggers_429(self, env):
        """限流：小限额下连续 POST 出现 429（限流器由 conftest 每个测试前 reset）"""
        client, config_path = env
        config = make_minimal_config()
        config['rate_limit_per_minute'] = 2
        config_path.write_text(json.dumps(config), encoding='utf-8')

        codes = [_post_share(client, _make_payload()).status_code for _ in range(4)]
        assert codes[:2] == [200, 200]
        assert 429 in codes[2:]
