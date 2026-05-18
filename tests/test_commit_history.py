import json
import os
import sys
import tempfile
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestCommitAnswerToHistory:
    def setup_method(self):
        import server
        self.tmpdir = tempfile.mkdtemp()
        self.orig_store = server.store
        server.store = server.ConversationStore(self.tmpdir)

    def teardown_method(self):
        import server
        import shutil
        server.store = self.orig_store
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _commit(self, conv_id, message, answer, phase=None):
        import server
        server.commit_answer_to_history(conv_id, message, answer, phase)

    def _read_data(self, conv_id):
        import server
        return server.store._read(conv_id)

    def test_appends_user_and_assistant(self):
        conv_id = "test-conv-1"
        self._commit(conv_id, "pick A", '{"q":1,"phase":"ASSESS"}')
        history = self._read_data(conv_id).get("history", [])
        assert len(history) == 2
        assert history[0] == {"role": "user", "content": "pick A"}
        assert history[1] == {"role": "assistant", "content": '{"q":1,"phase":"ASSESS"}'}

    def test_multiple_commits_accumulate(self):
        conv_id = "test-conv-2"
        self._commit(conv_id, "msg1", '{"q":1,"phase":"ASSESS"}')
        self._commit(conv_id, "msg2", '{"q":2,"phase":"ASSESS"}')
        self._commit(conv_id, "msg3", '{"q":3,"phase":"ASSESS"}')
        history = self._read_data(conv_id).get("history", [])
        assert len(history) == 6

    def test_no_lost_update_with_concurrent_writes(self):
        conv_id = "test-conv-3"
        errors = []

        def write_answer(i):
            try:
                self._commit(conv_id, f"pick{i}", f'{{"q":{i},"phase":"ASSESS"}}')
            except Exception as e:
                errors.append(f"writer {i}: {e}")

        threads = [threading.Thread(target=write_answer, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"concurrent write errors: {errors}"
        history = self._read_data(conv_id).get("history", [])
        assert len(history) == 100, f"expected 100, got {len(history)}"

    def test_saves_scene(self):
        conv_id = "test-conv-4"
        answer = json.dumps({
            "phase": "ASSESS", "q": 1,
            "scene": "boss suddenly appears",
            "options": ["A", "B"],
            "nb": 0, "bh": 0, "tf": 0, "ip": 0,
            "next_dim": "NB", "can_conclude": False
        }, ensure_ascii=False)
        self._commit(conv_id, "pick A", answer, "assess")
        scenes = self._read_data(conv_id).get("scenes", [])
        assert "boss suddenly appears" in scenes

    def test_scene_no_duplicate(self):
        conv_id = "test-conv-5"
        answer = json.dumps({
            "phase": "ASSESS", "q": 1,
            "scene": "same scene",
            "options": ["A", "B"],
            "nb": 0, "bh": 0, "tf": 0, "ip": 0,
            "next_dim": "NB", "can_conclude": False
        }, ensure_ascii=False)
        self._commit(conv_id, "pick A", answer, "assess")
        self._commit(conv_id, "pick B", answer, "assess")
        scenes = self._read_data(conv_id).get("scenes", [])
        assert len(scenes) == 1

    def test_result_phase_does_not_save_scene(self):
        conv_id = "test-conv-6"
        answer = json.dumps({
            "phase": "RESULT", "type": "NBTI", "name": "test",
            "scene": "midnight office"
        }, ensure_ascii=False)
        self._commit(conv_id, "end", answer, "result")
        scenes = self._read_data(conv_id).get("scenes", [])
        assert len(scenes) == 0
