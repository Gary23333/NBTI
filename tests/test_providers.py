"""供应商注册表（nbti/providers.py）测试。

覆盖五个内置适配器（doubao / longcat / deepseek / lmstudio / openai_compatible）的
URL / thinking / response_format 行为，以及 register_provider / get_provider /
list_provider_metadata / normalize_vendor 的注册表语义与未知 vendor 兜底。

统一通过 nbti.llm 的薄封装调用（它们委托给注册表），既验证适配器也验证调用点委托。
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import nbti.providers as providers
import nbti.llm as llm
from nbti.providers import (
    Provider, register_provider, get_provider, is_supported_vendor,
    normalize_vendor, list_provider_metadata, DEFAULT_VENDOR,
    DoubaoProvider, LongCatProvider, DeepSeekProvider,
    LMStudioProvider, OpenAICompatibleProvider,
)

JSON_MODE = {"enabled": True}


@pytest.fixture
def restore_registry():
    """注册表为模块级全局可变状态：用例内注册自定义 provider 后恢复快照，避免跨用例污染。"""
    snapshot = dict(providers._PROVIDERS)
    yield
    providers._PROVIDERS.clear()
    providers._PROVIDERS.update(snapshot)


# ---------- 端点 URL ----------

class TestProviderUrls:
    def test_doubao_url(self):
        url = llm.get_chat_completions_url(
            {"vendor": "doubao", "base_url": "https://ark.cn-beijing.volces.com/api/v3"}
        )
        assert url == "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    def test_longcat_url_has_openai_v1_prefix(self):
        url = llm.get_chat_completions_url(
            {"vendor": "longcat", "base_url": "https://api.longcat.chat"}
        )
        assert url == "https://api.longcat.chat/openai/v1/chat/completions"

    def test_deepseek_url(self):
        url = llm.get_chat_completions_url(
            {"vendor": "deepseek", "base_url": "https://api.deepseek.com"}
        )
        assert url == "https://api.deepseek.com/chat/completions"

    def test_lmstudio_appends_v1(self):
        url = llm.get_chat_completions_url(
            {"vendor": "lmstudio", "base_url": "http://localhost:1234"}
        )
        assert url == "http://localhost:1234/v1/chat/completions"

    def test_lmstudio_does_not_double_v1(self):
        """base_url 已以 /v1 结尾时不应重复追加。"""
        url = llm.get_chat_completions_url(
            {"vendor": "lmstudio", "base_url": "http://localhost:1234/v1/"}
        )
        assert url == "http://localhost:1234/v1/chat/completions"

    def test_openai_compatible_url(self):
        url = llm.get_chat_completions_url(
            {"vendor": "openai_compatible", "base_url": "https://api.openai.com/v1"}
        )
        assert url == "https://api.openai.com/v1/chat/completions"

    def test_base_url_trailing_slash_stripped(self):
        url = llm.get_chat_completions_url(
            {"vendor": "doubao", "base_url": "https://example.com/v3/"}
        )
        assert url == "https://example.com/v3/chat/completions"


# ---------- thinking 参数 ----------

class TestProviderThinking:
    def test_doubao_missing_thinking_returns_empty(self):
        assert llm.build_thinking_params({"vendor": "doubao"}) == {}

    def test_doubao_disabled_returns_empty(self):
        assert llm.build_thinking_params(
            {"vendor": "doubao", "thinking": {"type": "disabled"}}
        ) == {}

    def test_doubao_enabled_sends_reasoning_effort(self):
        assert llm.build_thinking_params(
            {"vendor": "doubao", "thinking": {"type": "enabled", "reasoning_effort": "high"}}
        ) == {"reasoning_effort": "high"}

    def test_thinking_without_type_treated_as_disabled(self):
        assert llm.build_thinking_params(
            {"vendor": "doubao", "thinking": {"reasoning_effort": "high"}}
        ) == {}

    def test_longcat_never_sends_thinking(self):
        # LongCat 思考能力内置（靠模型名区分），无论开关都不发送 thinking 参数
        assert llm.build_thinking_params(
            {"vendor": "longcat", "thinking": {"type": "enabled", "reasoning_effort": "high"}}
        ) == {}
        assert llm.build_thinking_params(
            {"vendor": "longcat", "thinking": {"type": "disabled"}}
        ) == {}

    def test_deepseek_enabled_sends_type_and_effort(self):
        params = llm.build_thinking_params(
            {"vendor": "deepseek", "thinking": {"type": "enabled", "reasoning_effort": "max"}}
        )
        assert params == {"thinking": {"type": "enabled"}, "reasoning_effort": "max"}

    def test_deepseek_disabled_returns_empty(self):
        assert llm.build_thinking_params(
            {"vendor": "deepseek", "thinking": {"type": "disabled"}}
        ) == {}

    def test_lmstudio_enabled_uses_generic_rule(self):
        # LM Studio 未覆盖思考启用逻辑，走基类实现：仅发送 reasoning_effort
        assert llm.build_thinking_params(
            {"vendor": "lmstudio", "thinking": {"type": "enabled", "reasoning_effort": "low"}}
        ) == {"reasoning_effort": "low"}

    def test_openai_compatible_enabled_uses_generic_rule(self):
        assert llm.build_thinking_params(
            {"vendor": "openai_compatible", "thinking": {"type": "enabled", "reasoning_effort": "medium"}}
        ) == {"reasoning_effort": "medium"}


# ---------- response_format ----------

class TestProviderResponseFormat:
    def test_doubao_always_empty(self):
        for phase in ("init", "assess", "result"):
            assert llm.build_response_format(
                {"vendor": "doubao", "json_mode": JSON_MODE}, phase
            ) == {}

    def test_longcat_always_empty(self):
        for phase in ("init", "assess", "result"):
            assert llm.build_response_format(
                {"vendor": "longcat", "json_mode": JSON_MODE}, phase
            ) == {}

    def test_deepseek_json_object(self):
        for phase in ("init", "assess", "result"):
            assert llm.build_response_format(
                {"vendor": "deepseek", "json_mode": JSON_MODE}, phase
            ) == {"response_format": {"type": "json_object"}}

    def test_deepseek_without_json_mode_empty(self):
        assert llm.build_response_format({"vendor": "deepseek"}, "assess") == {}

    def test_lmstudio_strict_json_schema_assess(self):
        rf = llm.build_response_format({"vendor": "lmstudio", "json_mode": JSON_MODE}, "init")
        assert rf["response_format"]["type"] == "json_schema"
        inner = rf["response_format"]["json_schema"]
        assert inner["name"] == "NBTIAssess"
        assert inner["strict"] is True
        assert isinstance(inner["schema"], dict)

    def test_openai_compatible_strict_json_schema_result(self):
        rf = llm.build_response_format(
            {"vendor": "openai_compatible", "json_mode": JSON_MODE}, "result"
        )
        assert rf["response_format"]["json_schema"]["name"] == "NBTIResult"

    def test_json_schema_empty_without_json_mode(self):
        assert llm.build_response_format({"vendor": "lmstudio"}, "init") == {}

    def test_json_schema_empty_for_unsupported_phase(self):
        assert llm.build_response_format(
            {"vendor": "openai_compatible", "json_mode": JSON_MODE}, "unknown"
        ) == {}

    def test_unknown_vendor_falls_back_to_openai_compatible(self):
        rf = llm.build_response_format({"vendor": "who-knows", "json_mode": JSON_MODE}, "init")
        assert rf["response_format"]["type"] == "json_schema"
        assert rf["response_format"]["json_schema"]["name"] == "NBTIAssess"


# ---------- 注册表语义 ----------

class TestRegistry:
    def test_get_provider_known_vendors(self):
        assert isinstance(get_provider("doubao"), DoubaoProvider)
        assert isinstance(get_provider("longcat"), LongCatProvider)
        assert isinstance(get_provider("deepseek"), DeepSeekProvider)
        assert isinstance(get_provider("lmstudio"), LMStudioProvider)
        assert isinstance(get_provider("openai_compatible"), OpenAICompatibleProvider)

    def test_get_provider_unknown_falls_back(self):
        assert isinstance(get_provider("no-such-vendor"), OpenAICompatibleProvider)
        assert isinstance(get_provider(None), OpenAICompatibleProvider)
        assert isinstance(get_provider(""), OpenAICompatibleProvider)

    def test_normalize_vendor(self):
        assert normalize_vendor("doubao") == "doubao"
        assert normalize_vendor("deepseek") == "deepseek"
        assert normalize_vendor("totally-unknown") == DEFAULT_VENDOR
        assert normalize_vendor(None) == DEFAULT_VENDOR
        assert normalize_vendor("") == DEFAULT_VENDOR

    def test_is_supported_vendor(self):
        assert is_supported_vendor("doubao")
        assert not is_supported_vendor("unknown")
        assert not is_supported_vendor(None)
        assert not is_supported_vendor("")

    def test_list_provider_metadata_shape(self):
        meta = list_provider_metadata()
        assert isinstance(meta, list)
        ids = {m["vendor_id"] for m in meta}
        assert {"doubao", "longcat", "deepseek", "lmstudio", "openai_compatible"} <= ids
        for m in meta:
            for key in (
                "vendor_id", "label", "supports_streaming", "supports_json_schema",
                "supports_thinking", "default_base_url", "default_model",
            ):
                assert key in m

    def test_register_custom_provider(self, restore_registry):
        class MyVendorProvider(Provider):
            vendor_id = "my-vendor"
            label = "My Vendor"

        instance = MyVendorProvider()
        assert register_provider(instance) is instance
        assert get_provider("my-vendor") is instance
        assert is_supported_vendor("my-vendor")
        assert normalize_vendor("my-vendor") == "my-vendor"
        assert any(m["vendor_id"] == "my-vendor" for m in list_provider_metadata())

    def test_register_same_id_overrides_previous(self, restore_registry):
        class First(Provider):
            vendor_id = "dup-vendor"
            label = "First"

        class Second(Provider):
            vendor_id = "dup-vendor"
            label = "Second"

        register_provider(First())
        register_provider(Second())
        assert get_provider("dup-vendor").label == "Second"

    def test_register_none_or_missing_id_ignored(self, restore_registry):
        assert register_provider(None) is None
        assert register_provider(object()) is None  # 缺少 vendor_id
        assert not is_supported_vendor(None)
