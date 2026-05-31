import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MockResponse:
    def __init__(self, status_code, json_data, stream_lines=None):
        self.status_code = status_code
        self._json_data = json_data
        self.text = json.dumps(json_data)
        self._stream_lines = stream_lines

    def json(self):
        return self._json_data

    def iter_lines(self, decode_unicode=True):
        if self._stream_lines:
            for line in self._stream_lines:
                yield line
        else:
            content = self._json_data["choices"][0]["message"]["content"]
            yield f'data: {json.dumps({"choices": [{"delta": {"content": content}}], "usage": self._json_data.get("usage", {})})}\n'
            yield 'data: [DONE]\n'


def make_assess(q, next_dim, nb=0, bh=0, tf=0, ip=0, can_conclude=False):
    return json.dumps({
        "phase": "ASSESS", "q": q, "nb": nb, "bh": bh, "tf": tf, "ip": ip,
        "next_dim": next_dim, "can_conclude": can_conclude,
        "comment": "test comment", "scene": f"scene {q}", "options": ["A", "B", "C"]
    }, ensure_ascii=False)


def make_minimal_config():
    return {
        "llm_profiles": [
            {
                "name": "test",
                "vendor": "openai",
                "model": "gpt-test",
                "api_key": "sk-test",
                "base_url": "https://test.example.com",
                "temperature": 0.7,
                "max_tokens": 2000,
                "json_mode": {"enabled": True}
            }
        ],
        "active_profile": "test",
        "phase_profiles": {"init": "test", "assess": "test", "result": "test"},
        "active_preset": "default",
        "prompt_presets": {
            "default": {
                "prompt_init": "init",
                "prompt_assess": "assess {previous_scenes} {min_questions} {min_questions_minus_1} {max_questions}",
                "prompt_result": "result {easter_schrodinger} {easter_hexagon} {easter_buddha} {easter_double} {easter_mouthpiece}"
            }
        },
        "min_questions": 20,
        "max_questions": 25,
        "easter_eggs": {"schrodinger": 1, "hexagon": 3, "buddha": 3, "double": 3, "mouthpiece": 5},
        "easter_egg_enabled": True,
        "prompt_init": "init",
        "prompt_assess": "assess {previous_scenes} {min_questions} {min_questions_minus_1} {max_questions}",
        "prompt_result": "result {easter_schrodinger} {easter_hexagon} {easter_buddha} {easter_double} {easter_mouthpiece}"
    }


class TestApiIntegration:
    @classmethod
    def setup_class(cls):
        import server
        from nbti import conversation, config as nbti_config
        import nbti.utils
        import nbti.app as nbti_app_mod
        cls.tmpdir = tempfile.mkdtemp()
        cls.orig_store = conversation.store
        cls.orig_config_file = nbti_config.CONFIG_FILE
        new_store = server.ConversationStore(cls.tmpdir)
        conversation.store = new_store
        nbti.utils.store = new_store
        nbti_app_mod.store = new_store
        cls.config_path = os.path.join(cls.tmpdir, "config.json")
        nbti_config.CONFIG_FILE = cls.config_path
        with open(cls.config_path, 'w', encoding='utf-8') as f:
            json.dump(make_minimal_config(), f, ensure_ascii=False)
        server.app.config['TESTING'] = True
        cls.client = server.app.test_client()

    @classmethod
    def teardown_class(cls):
        from nbti import conversation, config as nbti_config
        import nbti.utils
        import nbti.app as nbti_app_mod
        import shutil
        conversation.store = cls.orig_store
        nbti.utils.store = cls.orig_store
        nbti_app_mod.store = cls.orig_store
        nbti_config.CONFIG_FILE = cls.orig_config_file
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    @patch('nbti.llm.requests.post')
    def test_stream_chat_saves_history(self, mock_post):
        mock_post.return_value = MockResponse(200, {
            "choices": [{"message": {"content": make_assess(1, "NB")}}],
            "usage": {"total_tokens": 100}
        })
        resp = self.client.post('/api/chat?stream=1',
            content_type='application/json',
            data=json.dumps({"message": "开始测试", "conversation_id": ""}))
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        assert 'event' in body and 'done' in body, f"Response body: {body[:200]}"

    @patch('nbti.llm.requests.post')
    def test_stream_commits_next_dim_correctly(self, mock_post):
        mock_post.return_value = MockResponse(200, {
            "choices": [{"message": {"content": make_assess(1, "NB")}}],
            "usage": {"total_tokens": 100}
        })
        conv_id = "intg-stream-dim-1"
        resp = self.client.post('/api/chat?stream=1',
            content_type='application/json',
            data=json.dumps({"message": "开始测试", "conversation_id": conv_id}))
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        assert 'done' in body, f"Missing done event: {body[:200]}"
        from nbti import conversation
        history = conversation.store.get_history(conv_id)
        assert len(history) >= 2, f"Expected history >= 2, got {len(history)}: files={os.listdir(self.tmpdir)}"
        assistant_msgs = [m for m in history if m['role'] == 'assistant']
        assert len(assistant_msgs) >= 1
        data = json.loads(assistant_msgs[0]['content'])
        assert data['next_dim'] == 'NB'

    @patch('nbti.app.requests.post')
    @patch('nbti.llm.requests.post')
    def test_preload_generates_draft(self, mock_llm_post, mock_app_post):
        mock_app_post.return_value = MockResponse(200, {
            "choices": [{"message": {"content": make_assess(1, "NB")}}],
            "usage": {"total_tokens": 100}
        })
        from nbti import conversation
        conv_id = "intg-test-prel-1"
        conversation.store._write(conv_id, {"history": [], "scenes": [], "preloads": {}})
        resp = self.client.post('/api/chat/preload',
            content_type='application/json',
            data=json.dumps({"message": "pick A", "conversation_id": conv_id}))
        assert resp.status_code == 200
        data = json.loads(resp.get_data(as_text=True))
        assert data.get("answer") is not None
        draft = conversation.store.get_preload_draft(conv_id, "pick A")
        assert draft is not None, "Preload draft was not saved"
        parsed = json.loads(draft["answer"])
        assert parsed["q"] == 1, f"Expected q=1 (normalized from empty history), got {parsed['q']}"
        assert parsed["next_dim"] == "NB"

    @patch('nbti.app.requests.post')
    @patch('nbti.llm.requests.post')
    def test_preload_commit_rejects_wrong_q(self, mock_llm_post, mock_app_post):
        from nbti import conversation
        conv_id = "intg-test-prel-2"
        conversation.store._write(conv_id, {"history": [], "preloads": {
            "pick A": {"answer": make_assess(5, "NB"), "tokens_used": 100, "created_at": 0}
        }})
        resp = self.client.post('/api/chat/preload/commit',
            content_type='application/json',
            data=json.dumps({"message": "pick A", "conversation_id": conv_id}))
        assert resp.status_code == 409, f"Expected 409, got {resp.status_code}"

    @patch('nbti.app.requests.post')
    @patch('nbti.llm.requests.post')
    def test_next_dim_rotation_across_questions(self, mock_llm_post, mock_app_post):
        from nbti import conversation
        conv_id = "intg-test-rot-1"
        conversation.store._write(conv_id, {"history": [], "scenes": [], "preloads": {}})

        def side_effect(*args, **kwargs):
            body = kwargs.get('json', {})
            msgs = body.get('messages', [])
            q_count = sum(1 for m in msgs if m.get('role') == 'assistant')
            dims_cycle = ["NB", "BH", "TF", "IP"]
            next_dim = dims_cycle[q_count % 4]
            return MockResponse(200, {
                "choices": [{"message": {"content": make_assess(q_count + 1, next_dim)}}],
                "usage": {"total_tokens": 100}
            })

        mock_llm_post.side_effect = side_effect
        mock_app_post.side_effect = side_effect

        resp = self.client.post('/api/chat?stream=1',
            content_type='application/json',
            data=json.dumps({"message": "start", "conversation_id": conv_id}))
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        assert 'done' in body, f"First call failed: {body[:200]}"

        resp2 = self.client.post('/api/chat?stream=1',
            content_type='application/json',
            data=json.dumps({"message": "pick A", "conversation_id": conv_id}))
        assert resp2.status_code == 200
        body2 = resp2.get_data(as_text=True)
        assert 'done' in body2, f"Second call failed: {body2[:200]}"

        history = conversation.store.get_history(conv_id)
        assistant_msgs = [m for m in history if m['role'] == 'assistant']
        assert len(assistant_msgs) >= 2
        d1 = json.loads(assistant_msgs[0]['content'])
        d2 = json.loads(assistant_msgs[1]['content'])
        assert d1['next_dim'] == 'NB'
        assert d2['next_dim'] == 'BH'
