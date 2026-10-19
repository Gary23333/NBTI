"""配置兼容性测试（nbti/config.py）。

覆盖旧格式 config.json（model_init/assess/result）的自动迁移、含未知 vendor 的
llm_profiles 的 vendor 规范化，以及 load_config 补齐新键且不破坏既有键。
"""

import os
import sys
import json

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import nbti.config as config_mod
from nbti.config import _migrate_old_config, load_config, DEFAULT_CONFIG


LEGACY_KEYS = [
    "api_key", "endpoint", "model_init", "model_assess", "model_result",
    "temperature", "max_tokens", "reasoning_effort", "model",
]


def write_config(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')


# ---------------------------------------------------------------------------
# 旧格式 → profile 格式迁移
# ---------------------------------------------------------------------------
class TestOldFormatMigration:
    def test_legacy_models_migrated_to_profiles(self):
        old = {
            "api_key": "old-key",
            "endpoint": "https://old.example.com/api/v3",
            "model_init": "m-init",
            "model_assess": "m-assess",
            "model_result": "m-result",
            "temperature": 0.5,
            "max_tokens": 1500,
            "reasoning_effort": "medium",
        }
        migrated = _migrate_old_config(old.copy())

        assert "llm_profiles" in migrated
        assert len(migrated["llm_profiles"]) == 3
        for p in migrated["llm_profiles"]:
            # 旧格式迁移默认 vendor=doubao（已注册供应商，不应被规范化改写）
            assert p["vendor"] == "doubao"
            assert p["api_key"] == "old-key"
            assert p["base_url"] == "https://old.example.com/api/v3"
            assert p["thinking"]["type"] == "enabled"
            assert p["thinking"]["reasoning_effort"] == "medium"
        assert migrated["phase_profiles"]["init"] == "旧配置-init"
        assert migrated["phase_profiles"]["result"] == "旧配置-result"

        for key in LEGACY_KEYS:
            assert key not in migrated

    def test_legacy_minimal_migrates_to_disabled_thinking(self):
        old = {
            "api_key": "k", "endpoint": "e",
            "model_init": "m", "reasoning_effort": "minimal",
        }
        migrated = _migrate_old_config(old.copy())
        assert migrated["llm_profiles"][0]["thinking"]["type"] == "disabled"
        assert migrated["llm_profiles"][0]["thinking"]["reasoning_effort"] == "low"

    def test_unknown_vendor_normalized(self):
        cfg = {
            "llm_profiles": [
                {"name": "unknown", "vendor": "totally-unknown", "model": "m"},
                {"name": "ds", "vendor": "deepseek", "model": "m"},
                {"name": "missing", "model": "m"},
            ]
        }
        out = _migrate_old_config(cfg.copy())
        vendors = [p["vendor"] for p in out["llm_profiles"]]
        assert vendors == ["openai_compatible", "deepseek", "openai_compatible"]


# ---------------------------------------------------------------------------
# load_config：补齐新键 + 不破坏既有键
# ---------------------------------------------------------------------------
class TestLoadConfigCompat:
    def test_load_old_format_config_migrates_and_fills_new_keys(self, tmp_path, monkeypatch):
        old = {
            "api_key": "old-key",
            "endpoint": "https://old.example.com/api/v3",
            "model_init": "m-init",
            "model_assess": "m-assess",
            "model_result": "m-result",
        }
        path = tmp_path / "config.json"
        write_config(path, old)
        monkeypatch.setattr(config_mod, "CONFIG_FILE", str(path))

        cfg = load_config()

        # 旧格式已迁移为 llm_profiles
        assert "llm_profiles" in cfg and len(cfg["llm_profiles"]) == 3
        assert all(p["vendor"] == "doubao" for p in cfg["llm_profiles"])
        # 新键被补齐
        for key in ("cache_enabled", "storage_backend", "redis_url", "fast_mode", "phase_max_tokens"):
            assert key in cfg
        assert cfg["cache_enabled"] is True
        assert cfg["storage_backend"] == "file"
        assert cfg["fast_mode"] is False
        assert cfg["phase_max_tokens"] == {}
        # 既有键保留（active_preset / prompt_presets 等）
        assert "active_preset" in cfg
        assert "prompt_presets" in cfg

    def test_load_config_preserves_existing_values_over_defaults(self, tmp_path, monkeypatch):
        """既有键不被 DEFAULT_CONFIG 默认值覆盖；缺失新键才补齐。"""
        incoming = {
            "llm_profiles": [{"name": "p", "vendor": "unknown-vendor", "model": "m"}],
            "min_questions": 5,
            "max_questions": 9,
            "cache_enabled": False,
            "storage_backend": "redis",
            "redis_url": "redis://example/0",
        }
        path = tmp_path / "config.json"
        write_config(path, incoming)
        monkeypatch.setattr(config_mod, "CONFIG_FILE", str(path))

        cfg = load_config()

        assert cfg["min_questions"] == 5
        assert cfg["max_questions"] == 9
        assert cfg["cache_enabled"] is False           # 既有值保留
        assert cfg["storage_backend"] == "redis"
        assert cfg["redis_url"] == "redis://example/0"
        # 缺失新键补齐
        assert "fast_mode" in cfg and "phase_max_tokens" in cfg and "preload_enabled" in cfg
        # 未知 vendor 被规范化
        assert cfg["llm_profiles"][0]["vendor"] == "openai_compatible"

    def test_load_config_missing_file_returns_defaults(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config_mod, "CONFIG_FILE", str(tmp_path / "does-not-exist.json"))
        cfg = load_config()
        for key in DEFAULT_CONFIG:
            # 默认配置的键都应存在（这里只校验新增键可被安全获取）
            assert key in cfg
        assert cfg["cache_enabled"] is True
        assert cfg["storage_backend"] == "file"
