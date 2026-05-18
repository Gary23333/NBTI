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
        "presets": {"current": "default"},
        "min_questions": 20,
        "max_questions": 25,
        "easter_eggs": {"schrodinger": 1, "hexagon": 3, "buddha": 3, "double": 3, "mouthpiece": 5},
        "prompt_init": "init",
        "prompt_assess": "assess {previous_scenes} {min_questions} {min_questions_minus_1} {max_questions}",
        "prompt_result": "result {easter_schrodinger} {easter_hexagon} {easter_buddha} {easter_double} {easter_mouthpiece}"
    }


class TestApiIntegration:
    @classmethod
    def setup_class(cls):
        import server
        cls.tmpdir = tempfile.mkdtemp()
        cls.orig_store = server.store
        cls.orig_config_file = server.CONFIG_FILE
        server.store = server.ConversationStore(cls.tmpdir)
        cls.config_path = os.path.join(cls.tmpdir, "config.json")
        server.CONFIG_FILE = cls.config_path
        with open(cls.config_path, 'w', encoding='utf-8') as f:
            json.dump(make_minimal_config(), f, ensure_ascii=False)
        server.app.config['TESTING'] = True
        cls.client = server.app.test_client()

    @classmethod
    def teardown_class(cls):
        import server
        import shutil
        server.store = cls.orig_store
        server.CONFIG_FILE = cls.orig_config_file
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    @patch('server.requests.post')
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

    @patch('server.requests.post')
    def test_stream_commits_next_dim_correctly(self, mock_post):
        mock_post.return_value = MockResponse(200, {
            "choices": [{"message": {"content": make_assess(1, "NB")}}],
            "usage": {"total_tokens": 100}
        })
        self.client.post('/api/chat?stream=1',
            content_type='application/json',
            data=json.dumps({"message": "开始测试", "conversation_id": ""}))
        import server
        # Find the conversation that was just created
        files = [f for f in os.listdir(self.tmpdir) if f.endswith('.json') and f != 'config.json']
        assert files, "No conversation file created"
        conv_id = files[0].replace('.json', '')
        history = server.store.get_history(conv_id)
        assistant_msgs = [m for m in history if m['role'] == 'assistant']
        assert len(assistant_msgs) >= 1
        data = json.loads(assistant_msgs[0]['content'])
        assert data['next_dim'] == 'NB'

    @patch('server.requests.post')
    def test_preload_generates_draft(self, mock_post):
        mock_post.return_value = MockResponse(200, {
            "choices": [{"message": {"content": make_assess(1, "NB")}}],
            "usage": {"total_tokens": 100}
        })
        import server
        conv_id = "intg-test-prel-1"
        server.store._write(conv_id, {"history": [], "scenes": [], "preloads": {}})
        resp = self.client.post('/api/chat/preload',
            content_type='application/json',
            data=json.dumps({"message": "pick A", "conversation_id": conv_id}))
        assert resp.status_code == 200
        data = json.loads(resp.get_data(as_text=True))
        assert data.get("answer") is not None
        draft = server.store.get_preload_draft(conv_id, "pick A")
        assert draft is not None, "Preload draft was not saved"
        parsed = json.loads(draft["answer"])
        assert parsed["q"] == 1, f"Expected q=1 (normalized from empty history), got {parsed['q']}"
        assert parsed["next_dim"] == "NB"

    @patch('server.requests.post')
    def test_preload_commit_rejects_wrong_q(self, mock_post):
        import server
        conv_id = "intg-test-prel-2"
        # Pre-create a draft with q that won't match expected
        server.store._write(conv_id, {"history": [], "preloads": {
            "pick A": {"answer": make_assess(5, "NB"), "tokens_used": 100, "created_at": 0}
        }})
        resp = self.client.post('/api/chat/preload/commit',
            content_type='application/json',
            data=json.dumps({"message": "pick A", "conversation_id": conv_id}))
        assert resp.status_code == 409, f"Expected 409, got {resp.status_code}"

    @patch('server.requests.post')
    def test_next_dim_rotation_across_questions(self, mock_post):
        import server
        conv_id = "intg-test-rot-1"
        server.store._write(conv_id, {"history": [], "scenes": [], "preloads": {}})

        def side_effect(*args, **kwargs):
            body = kwargs.get('json', {})
            msgs = body.get('messages', [])
            q_count = sum(1 for m in msgs if m.get('role') == 'assistant')
            dims_cycle = ["NB", "BH", "TF", "IP"]
            next_dim = dims_cycle[q_count % 4]
            # Return a response for q = q_count + 1
            return MockResponse(200, {
                "choices": [{"message": {"content": make_assess(q_count + 1, next_dim)}}],
                "usage": {"total_tokens": 100}
            })

        mock_post.side_effect = side_effect

        # Q1: init
        resp = self.client.post('/api/chat?stream=1',
            content_type='application/json',
            data=json.dumps({"message": "start", "conversation_id": conv_id}))
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        # Debug: check for errors in response
        if 'error' in body[:200]:
            raise AssertionError(f"Stream response contained error: {body[:500]}")

        # Verify history was saved immediately
        history_check = server.store.get_history(conv_id)
        assert len(history_check) >= 2, f"History should have >= 2 msgs after Q1, got {len(history_check)}"

        # Q2-Q5: continue
        for i in range(2, 6):
            resp = self.client.post('/api/chat?stream=1',
                content_type='application/json',
                data=json.dumps({"message": f"pick{i}", "conversation_id": conv_id}))
            assert resp.status_code == 200
            body = resp.get_data(as_text=True)
            if 'error' in body[:200]:
                raise AssertionError(f"Q{i} response had error: {body[:300]}")
            history_check = server.store.get_history(conv_id)
            assert len(history_check) == 2 * i, f"After Q{i}: expected {2*i} msgs, got {len(history_check)}"

        history = server.store.get_history(conv_id)
        assistant_msgs = [json.loads(m['content']) for m in history if m['role'] == 'assistant']
        dims = [m.get('next_dim') for m in assistant_msgs]
        expected = ["NB", "BH", "TF", "IP", "NB"]
        assert dims == expected, f"Expected {expected}, got {dims}"
