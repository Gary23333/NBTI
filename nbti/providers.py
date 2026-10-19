"""可扩展的模型供应商（Provider）注册表。

将原先散落在 nbti.llm 中按 vendor 硬编码的分支逻辑，抽象为统一的
Provider 适配协议 + 注册表。新增供应商时只需实现一个 Provider 子类并
注册，无需改动 llm.py 的调用点。

对外 API：
    register_provider(provider)     注册一个供应商适配器
    get_provider(vendor_id)         按 vendor 查找（未知回退 openai_compatible）
    list_provider_metadata()        返回供应商元数据列表（供配置面板渲染下拉）
    normalize_vendor(vendor_id)     将缺失/未知 vendor 规范化为可识别值
    is_supported_vendor(vendor_id)  判断 vendor 是否为已注册供应商
"""

import logging

logger = logging.getLogger(__name__)


# 未知/缺失 vendor 回退到通用 OpenAI 兼容适配器
DEFAULT_VENDOR = "openai_compatible"


# ---------------------------------------------------------------------------
# 供应商适配协议 / 基类
# ---------------------------------------------------------------------------
class Provider:
    """供应商适配基类。

    子类通过覆盖方法实现供应商差异，并通过类属性声明自身能力。
    thinking 的通用规则（缺失或未启用一律返回 {}）在基类集中实现，
    启用时的具体参数由子类覆盖 `_enabled_thinking_params`。
    """

    # ---- 能力声明（子类覆盖） ----
    vendor_id = "base"                 # 供应商唯一标识
    label = "Base"                     # 展示名称（配置面板下拉用）
    supports_streaming = True          # 是否支持流式输出
    supports_json_schema = False       # 是否支持严格的 json_schema response_format
    supports_thinking = False          # 是否支持思考（reasoning）参数
    default_base_url = ""              # 默认端点
    default_model = ""                 # 默认模型名

    # ------------------------------------------------------------------
    # 适配方法
    # ------------------------------------------------------------------
    def chat_completions_url(self, profile):
        """默认实现：base_url.rstrip('/') + '/chat/completions'。"""
        base_url = self._base_url(profile)
        return f"{base_url}/chat/completions"

    def build_thinking_params(self, profile):
        """通用思考参数规则：thinking 缺失或未启用时返回 {}。

        thinking.type == "enabled" 时的实际参数交由子类实现。
        """
        thinking_config = profile.get("thinking", {})
        if not thinking_config:
            return {}
        if thinking_config.get("type", "disabled") != "enabled":
            return {}
        effort = thinking_config.get("reasoning_effort", "low")
        return self._enabled_thinking_params(effort)

    def _enabled_thinking_params(self, effort):
        """思考启用时的参数（默认：仅发送 reasoning_effort）。"""
        return {"reasoning_effort": effort}

    def build_response_format(self, profile, phase):
        """默认：不支持 json_schema，一律返回 {}。"""
        return {}

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    def _base_url(self, profile):
        """取出去尾斜杠的 base_url。"""
        return (profile.get("base_url") or "").rstrip("/")

    def _json_mode_enabled(self, profile):
        """判断 profile 是否开启 json_mode。"""
        jm = profile.get("json_mode", {})
        return bool(jm) and bool(jm.get("enabled"))

    def _schema_for_phase(self, phase):
        """按阶段返回 (name, schema)；不支持的阶段返回 None。

        延迟导入 nbti.llm，避免 nbti.llm <-> nbti.providers 循环导入。
        """
        from nbti.llm import build_assess_schema, build_result_schema
        if phase in ("init", "assess"):
            return "NBTIAssess", build_assess_schema()
        if phase == "result":
            return "NBTIResult", build_result_schema()
        return None

    def _strict_json_schema_response_format(self, profile, phase):
        """构造严格 json_schema 的 response_format；不适用时返回 {}。"""
        if not self._json_mode_enabled(profile):
            return {}
        result = self._schema_for_phase(phase)
        if not result:
            return {}
        name, schema = result
        return {
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": name,
                    "strict": True,
                    "schema": schema
                }
            }
        }

    def metadata(self):
        """返回该供应商的能力元数据（供配置面板渲染下拉）。"""
        return {
            "vendor_id": self.vendor_id,
            "label": self.label,
            "supports_streaming": self.supports_streaming,
            "supports_json_schema": self.supports_json_schema,
            "supports_thinking": self.supports_thinking,
            "default_base_url": self.default_base_url,
            "default_model": self.default_model,
        }


# ---------------------------------------------------------------------------
# 内置供应商适配器（逐字等价迁移 llm.py 原有的 vendor 分支逻辑）
# ---------------------------------------------------------------------------
class DoubaoProvider(Provider):
    """豆包（火山方舟）：接口不支持 response_format=json_schema，依赖提示词。"""

    vendor_id = "doubao"
    label = "豆包 (Doubao)"
    supports_streaming = True
    supports_json_schema = False
    supports_thinking = True
    default_base_url = "https://ark.cn-beijing.volces.com/api/v3"
    default_model = "doubao-seed-2-0-lite-260428"

    def build_response_format(self, profile, phase):
        # 豆包当前接口不支持 response_format=json_schema，一律返回 {}
        return {}


class LongCatProvider(Provider):
    """LongCat：思考能力内置（靠模型名区分），路径含 /openai/v1 前缀。"""

    vendor_id = "longcat"
    label = "LongCat"
    supports_streaming = True
    supports_json_schema = False
    supports_thinking = True
    default_base_url = "https://api.longcat.chat"
    default_model = "LongCat-Flash-Chat"

    def chat_completions_url(self, profile):
        return f"{self._base_url(profile)}/openai/v1/chat/completions"

    def build_thinking_params(self, profile):
        # LongCat 思考模型内置思考能力，不发送 thinking 参数
        return {}

    def build_response_format(self, profile, phase):
        # LongCat 当前接口不支持 response_format=json_schema，依赖提示词
        return {}


class DeepSeekProvider(Provider):
    """DeepSeek：需 thinking.type 开关 + reasoning_effort；json 模式走 json_object。"""

    vendor_id = "deepseek"
    label = "DeepSeek"
    supports_streaming = True
    supports_json_schema = False
    supports_thinking = True
    default_base_url = "https://api.deepseek.com"
    default_model = "deepseek-chat"

    def _enabled_thinking_params(self, effort):
        # DeepSeek: low/medium 会被映射为 high, xhigh → max
        return {
            "thinking": {"type": "enabled"},
            "reasoning_effort": effort
        }

    def build_response_format(self, profile, phase):
        # DeepSeek chat 兼容 JSON object；严格 schema 兼容性因模型/端点不同，先走保守格式
        if not self._json_mode_enabled(profile):
            return {}
        if phase in ("init", "assess", "result"):
            return {"response_format": {"type": "json_object"}}
        return {}


class LMStudioProvider(Provider):
    """LM Studio：本地端点，base_url 需以 /v1 结尾；支持严格 json_schema。"""

    vendor_id = "lmstudio"
    label = "LM Studio"
    supports_streaming = True
    supports_json_schema = True
    supports_thinking = True
    default_base_url = "http://localhost:1234"
    default_model = ""

    def chat_completions_url(self, profile):
        base_url = self._base_url(profile)
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"
        return f"{base_url}/chat/completions"

    def build_response_format(self, profile, phase):
        return self._strict_json_schema_response_format(profile, phase)


class OpenAICompatibleProvider(Provider):
    """通用 OpenAI 兼容适配器（新增，作为未知 vendor 的兜底）。"""

    vendor_id = "openai_compatible"
    label = "OpenAI 兼容 (通用)"
    supports_streaming = True
    supports_json_schema = True
    supports_thinking = True
    default_base_url = "https://api.openai.com/v1"
    default_model = ""

    def build_response_format(self, profile, phase):
        return self._strict_json_schema_response_format(profile, phase)


# ---------------------------------------------------------------------------
# 注册表
# ---------------------------------------------------------------------------
# 按注册顺序保存（Python dict 保序），openai_compatible 放最后作兜底
_PROVIDERS = {}


def register_provider(provider):
    """注册一个供应商适配器（同 vendor_id 后注册覆盖先注册）。"""
    if provider is None:
        return None
    vendor_id = getattr(provider, "vendor_id", None)
    if not vendor_id:
        logger.warning("[PROVIDERS] 跳过缺少 vendor_id 的 provider: %r", provider)
        return None
    _PROVIDERS[vendor_id] = provider
    return provider


def get_provider(vendor_id):
    """按 vendor_id 查找适配器；未知/缺失回退 openai_compatible。"""
    if vendor_id and vendor_id in _PROVIDERS:
        return _PROVIDERS[vendor_id]
    return _PROVIDERS.get(DEFAULT_VENDOR)


def is_supported_vendor(vendor_id):
    """判断 vendor_id 是否为已注册供应商。"""
    return bool(vendor_id) and vendor_id in _PROVIDERS


def normalize_vendor(vendor_id):
    """将缺失/未知 vendor 规范化为注册表可识别的值（未知 → openai_compatible）。"""
    return vendor_id if is_supported_vendor(vendor_id) else DEFAULT_VENDOR


def list_provider_metadata():
    """返回全部已注册供应商的能力元数据列表（供配置面板动态渲染下拉）。"""
    return [p.metadata() for p in _PROVIDERS.values()]


# 注册内置供应商
register_provider(DoubaoProvider())
register_provider(LongCatProvider())
register_provider(DeepSeekProvider())
register_provider(LMStudioProvider())
register_provider(OpenAICompatibleProvider())
