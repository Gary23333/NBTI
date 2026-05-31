"""Tests for JSON parsing utilities"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nbti.utils import parse_json_answer, parse_answer_meta, normalize_options


class TestParseJsonAnswer:
    def test_direct_json(self):
        raw = '{"phase":"ASSESS","q":1,"comment":"test","scene":"test scene","options":["a","b"],"nb":1,"bh":0,"tf":0,"ip":0,"next_dim":"BH","can_conclude":false}'
        result = parse_json_answer(raw)
        assert result is not None
        assert result['phase'] == 'ASSESS'
        assert result['q'] == 1

    def test_markdown_wrapped_json(self):
        raw = '```json\n{"phase":"ASSESS","q":1,"comment":"test","scene":"test","options":["a","b"],"nb":1,"bh":0,"tf":0,"ip":0,"next_dim":"BH","can_conclude":false}\n```'
        result = parse_json_answer(raw)
        assert result is not None
        assert result['phase'] == 'ASSESS'

    def test_json_with_preamble(self):
        raw = 'Here is the answer: {"phase":"ASSESS","q":1,"comment":"test","scene":"test","options":["a","b"],"nb":1,"bh":0,"tf":0,"ip":0,"next_dim":"BH","can_conclude":false}'
        result = parse_json_answer(raw)
        assert result is not None
        assert result['phase'] == 'ASSESS'

    def test_empty_string(self):
        assert parse_json_answer('') is None

    def test_no_json(self):
        assert parse_json_answer('no json here') is None

    def test_result_phase(self):
        raw = '{"phase":"RESULT","type":"NBTI","name":"test","oneline":"test","scene":"test","adapt":"test","crash":"test","interpretation":"test"*80,"pseudo_science":"test"*80,"closing":"test"}'
        # This will fail due to invalid JSON, but test the pattern
        result = parse_json_answer('{"phase":"RESULT","type":"NBTI","name":"test"}')
        assert result is not None
        assert result['phase'] == 'RESULT'


class TestParseAnswerMeta:
    def test_assess_meta(self):
        raw = '{"phase":"ASSESS","q":3,"comment":"test","scene":"test","options":["a","b"],"nb":2,"bh":-1,"tf":0,"ip":1,"next_dim":"TF","can_conclude":false}'
        meta = parse_answer_meta(raw)
        assert meta['phase'] == 'ASSESS'
        assert meta['q'] == 3
        assert meta['nb'] == 2
        assert meta['next_dim'] == 'TF'
        assert meta['can_conclude'] is False

    def test_empty_answer(self):
        meta = parse_answer_meta('')
        assert meta['phase'] is None


class TestNormalizeOptions:
    def test_string_array(self):
        result = normalize_options('["opt1","opt2","opt3"]')
        assert result == ['opt1', 'opt2', 'opt3']

    def test_comma_separated(self):
        result = normalize_options('opt1, opt2, opt3')
        assert len(result) == 3

    def test_strip_prefix(self):
        result = normalize_options(['A. option1', 'B. option2', 'C. option3'])
        assert result == ['option1', 'option2', 'option3']

    def test_max_four(self):
        result = normalize_options(['a', 'b', 'c', 'd', 'e'])
        assert len(result) == 4

    def test_empty(self):
        assert normalize_options([]) == []
        assert normalize_options('') == []
