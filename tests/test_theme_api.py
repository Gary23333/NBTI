"""主题 API 集成测试：
- GET /api/themes 返回 9 个主题且字段完整（id/name/description/icon）
- 9 主题 × 2 关键风格（暴躁老油条/官方MBTI）init（开始测试）流程冒烟（mock LLM），
  并断言发往 LLM 的 system prompt 确实注入了对应主题人格与风格人设
- workplace/animal/mbti 三个代表主题的 answer（作答）流程正常推进
"""

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
from nbti.app import create_app
from nbti.conversation import ConversationStore
from conftest import make_minimal_config

EXPECTED_THEMES = [
    "workplace", "animal", "color", "love", "social",
    "mbti", "brainhol", "money", "spirit",
]

# init 冒烟覆盖的关键风格：经典默认风格 + MBTI 官方风格
KEY_STYLES = ["暴躁老油条", "官方MBTI"]

# 每个主题的人格速查表中独有的标志词，用于验证 system prompt 注入了正确主题
THEME_MARKERS = {
    "workplace": "卷王",
    "animal": "东北虎",
    "color": "中国红",
    "love": "海王本王",
    "social": "社交悍匪",
    "mbti": "建筑师",
    "brainhol": "星际病院院长",
    "money": "风口赌徒",
    "spirit": "永动机卷王",
}

# 每种风格的 persona 标志词，用于验证 system prompt 注入了正确风格
STYLE_MARKERS = {
    "暴躁老油条": "脱口秀演员",
    "官方MBTI": "资深MBTI认证施测师",
}

# answer 流程中用于验证 assess prompt 注入主题出题方向的场景标志词
THEME_SCENE_MARKERS = {
    "workplace": "加班修罗场",
    "animal": "丛林法则",
    "mbti": "能量来源",
}


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


def _last_system_prompt(mock_post):
    """从 mock 的 requests.post 调用中取出最后一次发往 LLM 的 system prompt"""
    return mock_post.call_args.kwargs['json']['messages'][0]['content']


class TestThemesEndpoint:
    def test_returns_nine_themes(self, env):
        client, _, _ = env
        resp = client.get('/api/themes')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list) and len(data) == 9
        assert {t['id'] for t in data} == set(EXPECTED_THEMES)

    def test_theme_fields_complete(self, env):
        client, _, _ = env
        data = client.get('/api/themes').get_json()
        for item in data:
            assert set(item.keys()) == {"id", "name", "description", "icon"}
            for field in ("id", "name", "description", "icon"):
                assert isinstance(item[field], str) and item[field].strip()

    def test_matches_get_themes(self, env):
        """API 返回与 nbti.themes.get_themes() 一致"""
        client, _, _ = env
        from nbti.themes import get_themes
        assert client.get('/api/themes').get_json() == get_themes()


class TestThemeInitFlow:
    """9 主题 × 2 关键风格：init（开始测试）流程返回第一题，
    主题/风格正确落库，且发往 LLM 的 init system prompt 注入了对应主题与风格"""

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    @pytest.mark.parametrize("style", KEY_STYLES)
    def test_init_returns_first_question(self, env, theme_id, style):
        client, _, new_store = env
        conv_id = f"init-{theme_id}-{KEY_STYLES.index(style)}"
        with patch('nbti.app.requests.post',
                   return_value=_mock_llm_ok(make_assess(1))) as mock_post:
            resp = client.post('/api/chat', content_type='application/json',
                               data=json.dumps({"message": "开始测试",
                                                "conversation_id": conv_id,
                                                "theme": theme_id,
                                                "style": style}))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["conversation_id"] == conv_id
        answer = json.loads(data["answer"])
        assert answer["phase"] == "ASSESS"
        assert answer["q"] == 1

        # 主题与风格落库
        assert new_store.get_theme(conv_id) == theme_id
        assert new_store.get_style(conv_id) == style

        # 发往 LLM 的 init prompt 注入了正确主题人格、风格人设与主题出题方向
        system_prompt = _last_system_prompt(mock_post)
        assert THEME_MARKERS[theme_id] in system_prompt
        assert STYLE_MARKERS[style] in system_prompt
        assert "本主题出题方向" in system_prompt


class TestThemeAnswerFlow:
    """代表主题：init 后 answer（作答）流程正常推进到第二题，
    且 assess prompt 持续注入该主题的出题方向"""

    @pytest.mark.parametrize("theme_id", ["workplace", "animal", "mbti"])
    def test_answer_advances_to_next_question(self, env, theme_id):
        client, _, new_store = env
        conv_id = f"answer-{theme_id}"
        with patch('nbti.app.requests.post',
                   return_value=_mock_llm_ok(make_assess(1))):
            resp1 = client.post('/api/chat', content_type='application/json',
                                data=json.dumps({"message": "开始测试",
                                                 "conversation_id": conv_id,
                                                 "theme": theme_id}))
        assert resp1.status_code == 200

        with patch('nbti.app.requests.post',
                   return_value=_mock_llm_ok(make_assess(2, "BH"))) as mock_post:
            resp2 = client.post('/api/chat', content_type='application/json',
                                data=json.dumps({"message": "A",
                                                 "conversation_id": conv_id}))
        assert resp2.status_code == 200
        answer2 = json.loads(resp2.get_json()["answer"])
        assert answer2["phase"] == "ASSESS"
        assert answer2["q"] == 2

        # 作答轮使用 assess prompt：注入了该主题出题方向
        system_prompt = _last_system_prompt(mock_post)
        assert "本主题出题方向" in system_prompt
        assert THEME_SCENE_MARKERS[theme_id] in system_prompt

        # 历史推进：用户首条消息 + Q1 + 作答 + Q2；主题在会话中保持
        history = new_store.get_history(conv_id)
        assert len(history) == 4
        assistant_msgs = [m for m in history if m['role'] == 'assistant']
        assert json.loads(assistant_msgs[0]['content'])['q'] == 1
        assert json.loads(assistant_msgs[1]['content'])['q'] == 2
        assert new_store.get_theme(conv_id) == theme_id
