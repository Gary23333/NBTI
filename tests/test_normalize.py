import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import patch
from conftest import make_minimal_config


def make_answer(q, next_dim, nb=0, bh=0, tf=0, ip=0, can_conclude=False, phase="ASSESS"):
    return json.dumps({
        "phase": phase, "q": q, "nb": nb, "bh": bh, "tf": tf, "ip": ip,
        "next_dim": next_dim, "can_conclude": can_conclude,
        "comment": "test comment", "scene": "test scene", "options": ["A", "B"]
    }, ensure_ascii=False)


class TestNextDimForQuestion:
    def test_rotation_q1_through_q12(self):
        import server
        expected = ["NB", "BH", "TF", "IP", "NB", "BH", "TF", "IP", "NB", "BH", "TF", "IP"]
        for i, exp in enumerate(expected, 1):
            result = server.next_dimension_for_question(i)
            assert result == exp, f"Q{i}: expected {exp}, got {result}"


class TestNormalizeAnswerQuestion:
    def setup_method(self):
        import server
        self.orig_load_config = server.load_config
        server.load_config = lambda: make_minimal_config()

    def teardown_method(self):
        import server
        server.load_config = self.orig_load_config

    def call_normalize(self, answer, expected_q):
        import server
        return server.normalize_answer_question(answer, expected_q)

    def test_fixes_wrong_q(self):
        result = self.call_normalize(make_answer(5, "BH"), 6)
        assert json.loads(result)["q"] == 6

    def test_corrects_invalid_next_dim(self):
        result = self.call_normalize(make_answer(6, "XYZ"), 6)
        assert json.loads(result)["next_dim"] == "BH"

    def test_corrects_wrong_rotation_before_min(self):
        result = self.call_normalize(make_answer(6, "NB"), 6)
        assert json.loads(result)["next_dim"] == "BH"

    def test_corrects_wrong_rotation_at_min_when_not_concluding(self):
        result = self.call_normalize(make_answer(20, "NB", can_conclude=False), 20)
        data = json.loads(result)
        assert data["next_dim"] == "IP", f"Q20 should be IP, got {data['next_dim']}"

    def test_keeps_end_when_concluding_at_min(self):
        answer = make_answer(20, "END", can_conclude=True)
        result = self.call_normalize(answer, 20)
        assert json.loads(result)["next_dim"] == "END"

    def test_forces_end_at_max(self):
        cfg = make_minimal_config(max_q=25)
        import server
        orig = server.load_config
        server.load_config = lambda: cfg
        try:
            result = self.call_normalize(make_answer(25, "NB"), 25)
            data = json.loads(result)
            assert data["next_dim"] == "END"
            assert data["can_conclude"] == True
        finally:
            server.load_config = orig

    def test_keeps_valid_next_dim_when_correct(self):
        result = self.call_normalize(make_answer(3, "TF"), 3)
        assert json.loads(result)["next_dim"] == "TF"

    def test_returns_original_on_unparseable(self):
        result = self.call_normalize("not json at all", 5)
        assert result == "not json at all"

    def test_returns_original_on_result_phase(self):
        answer = make_answer(1, "END", phase="RESULT")
        result = self.call_normalize(answer, 1)
        assert json.loads(result)["phase"] == "RESULT"

    def test_forces_can_conclude_false_before_min(self):
        answer = make_answer(3, "TF", can_conclude=True)
        result = self.call_normalize(answer, 3)
        assert json.loads(result)["can_conclude"] == False

    def test_keeps_end_at_min_when_concluding_and_next_dim_end(self):
        cfg = make_minimal_config(min_q=20)
        import server
        orig = server.load_config
        server.load_config = lambda: cfg
        try:
            answer = make_answer(21, "END", can_conclude=True)
            result = self.call_normalize(answer, 21)
            data = json.loads(result)
            assert data["next_dim"] == "END"
        finally:
            server.load_config = orig
