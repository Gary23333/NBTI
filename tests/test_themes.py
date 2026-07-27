"""主题 schema 完整性与 prompts 联动测试"""
import sys
import os
import re

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nbti.themes import THEMES, get_theme, get_themes
from nbti.prompts import (
    ALL_STYLES,
    build_init_prompt,
    build_assess_prompt,
    build_result_prompt,
    get_personality_quick,
)

EXPECTED_THEMES = [
    "workplace", "animal", "color", "love", "social",
    "mbti", "brainhol", "money", "spirit",
]
EGG_KEYS = {"schrodinger", "hexagon", "buddha", "double", "mouthpiece"}
DIM_KEYS = ["nb", "bh", "tf", "ip"]

ASSESS_KW = {
    "previous_scenes": "（暂无，你是第一题）",
    "min_questions": "12",
    "min_questions_minus_1": "11",
    "max_questions": "16",
}
RESULT_KW = {f"easter_{k}": "1" for k in sorted(EGG_KEYS)}


def _dim_letter_pairs(theme):
    """每个维度的 (正极字母, 负极字母)，用于校验人格代号合法性"""
    return [(d["positive"][0], d["negative"][0]) for d in theme["dimensions"]]


class TestThemeSchema:
    def test_all_expected_themes_exist(self):
        assert set(EXPECTED_THEMES) == set(THEMES.keys())

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    def test_basic_fields(self, theme_id):
        theme = THEMES[theme_id]
        assert theme["id"] == theme_id
        for field in ("name", "description", "icon"):
            assert isinstance(theme.get(field), str) and theme[field].strip()

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    def test_dimensions(self, theme_id):
        dims = THEMES[theme_id]["dimensions"]
        assert len(dims) == 4
        assert [d["key"] for d in dims] == DIM_KEYS
        for d in dims:
            assert d["positive"].strip() and d["negative"].strip()

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    def test_personality_count(self, theme_id):
        assert len(THEMES[theme_id]["personality_types"]) >= 12

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    def test_personality_fields(self, theme_id):
        for t in THEMES[theme_id]["personality_types"]:
            for field in ("code", "name", "oneline"):
                assert isinstance(t.get(field), str) and t[field].strip()

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    def test_personality_codes_unique(self, theme_id):
        codes = [t["code"] for t in THEMES[theme_id]["personality_types"]]
        assert len(codes) == len(set(codes))

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    def test_personality_code_letters_legal(self, theme_id):
        """代号 4 位字母，每位必须来自对应维度的正/负极字母"""
        theme = THEMES[theme_id]
        pairs = _dim_letter_pairs(theme)
        for t in theme["personality_types"]:
            code = t["code"]
            assert len(code) == 4, f"{theme_id}:{code} 不是4位代号"
            for i, ch in enumerate(code):
                assert ch in pairs[i], f"{theme_id}:{code} 第{i+1}位 {ch} 不合法"

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    def test_easter_eggs(self, theme_id):
        eggs = THEMES[theme_id]["easter_eggs"]
        assert set(eggs.keys()) == EGG_KEYS
        for name in eggs.values():
            assert isinstance(name, str) and name.strip()

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    def test_colors(self, theme_id):
        colors = THEMES[theme_id]["colors"]
        for key in ("primary", "secondary", "accent"):
            value = colors.get(key, "")
            assert re.fullmatch(r"#[0-9a-fA-F]{6}", value), f"{theme_id}.colors.{key} 非法"

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    def test_scenes(self, theme_id):
        scenes = THEMES[theme_id]["scenes"]
        assert isinstance(scenes, list) and len(scenes) >= 4
        for s in scenes:
            assert isinstance(s, str) and s.strip()


class TestGetThemes:
    def test_count(self):
        assert len(get_themes()) == len(EXPECTED_THEMES)

    def test_summary_fields(self):
        for item in get_themes():
            assert set(item.keys()) == {"id", "name", "description", "icon"}

    def test_get_theme_fallback(self):
        assert get_theme("nonexistent-theme")["id"] == "workplace"


class TestPromptsIntegration:
    """每个主题 × 每种风格：prompt 构建不抛异常，人格列表与主题内容正确注入"""

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    @pytest.mark.parametrize("style", ALL_STYLES)
    def test_init_prompt(self, theme_id, style):
        prompt = build_init_prompt(theme_id, style)
        theme = get_theme(theme_id)
        for t in theme["personality_types"]:
            assert t["name"] in prompt
        # 判定规则字母与主题维度一致
        first_dim_pos = theme["dimensions"][0]["positive"][0]
        assert f"NB>0→{first_dim_pos}" in prompt
        # 主题出题方向已注入
        assert "本主题出题方向" in prompt

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    @pytest.mark.parametrize("style", ALL_STYLES)
    def test_assess_prompt(self, theme_id, style):
        prompt = build_assess_prompt(theme_id, style, **ASSESS_KW)
        theme = get_theme(theme_id)
        for t in theme["personality_types"]:
            assert t["name"] in prompt
        # 模板占位符全部渲染
        for placeholder in ASSESS_KW:
            assert "{" + placeholder + "}" not in prompt
        assert "本主题出题方向" in prompt

    @pytest.mark.parametrize("theme_id", EXPECTED_THEMES)
    @pytest.mark.parametrize("style", ALL_STYLES)
    def test_result_prompt(self, theme_id, style):
        prompt = build_result_prompt(theme_id, style, **RESULT_KW)
        theme = get_theme(theme_id)
        for t in theme["personality_types"]:
            assert t["name"] in prompt
        # 彩蛋人格名与概率占位符全部注入
        for egg_name in theme["easter_eggs"].values():
            assert egg_name in prompt
        assert "{easter_" not in prompt

    def test_quick_generated_from_theme(self):
        quick = get_personality_quick("mbti")
        assert "INTJ" in quick and "建筑师" in quick
        quick = get_personality_quick("money")
        assert "风口赌徒" in quick
