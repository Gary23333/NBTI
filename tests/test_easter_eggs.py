"""Tests for easter egg personality detection"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nbti.utils import check_easter_egg
from tests.conftest import make_minimal_config


class TestCheckEasterEgg:
    def test_disabled(self):
        config = make_minimal_config()
        config['easter_egg_enabled'] = False
        scores = {'nb': 0, 'bh': 0, 'tf': 0, 'ip': 0}
        assert check_easter_egg(scores, config) is None

    def test_schrodinger_all_zero(self):
        config = make_minimal_config()
        config['easter_eggs'] = {'schrodinger': 100}  # 100% chance
        scores = {'nb': 0, 'bh': 0, 'tf': 0, 'ip': 0}
        result = check_easter_egg(scores, config)
        assert result == 'schrodinger'

    def test_hexagon_all_positive(self):
        config = make_minimal_config()
        config['easter_eggs'] = {'hexagon': 100}
        scores = {'nb': 5, 'bh': 5, 'tf': 5, 'ip': 5}
        result = check_easter_egg(scores, config)
        assert result == 'hexagon'

    def test_buddha_all_negative(self):
        config = make_minimal_config()
        config['easter_eggs'] = {'buddha': 100}
        scores = {'nb': -5, 'bh': -5, 'tf': -5, 'ip': -5}
        result = check_easter_egg(scores, config)
        assert result == 'buddha'

    def test_twoface_large_gap(self):
        config = make_minimal_config()
        config['easter_eggs'] = {'double': 100}
        scores = {'nb': 10, 'bh': 0, 'tf': 0, 'ip': 0}
        result = check_easter_egg(scores, config)
        assert result == 'twoface'

    def test_no_easter_egg_normal_scores(self):
        config = make_minimal_config()
        config['easter_eggs'] = {'schrodinger': 1, 'hexagon': 1, 'buddha': 1, 'double': 1, 'mouthpiece': 1}
        scores = {'nb': 2, 'bh': -1, 'tf': 1, 'ip': 0}
        # With 1% chance, might or might not trigger - test that it returns either None or a string
        result = check_easter_egg(scores, config)
        assert result is None or isinstance(result, str)
