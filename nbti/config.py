import os
import json
import logging
from nbti.prompts import get_prompt_presets

logger = logging.getLogger(__name__)

def get_api_key(profile_name, default=""):
    env_key = f"NBTI_API_KEY_{profile_name.replace(' ', '_').replace('-', '_').upper()}"
    return os.environ.get(env_key, default)


# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'config.json')

# 默认 LLM Profiles 配置
DEFAULT_PROFILES = [
    {
        "name": "豆包 mini 无思考",
        "vendor": "doubao",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-seed-2-0-mini-260428",
        "api_key": "",
        "temperature": 0.9,
        "max_tokens": 2000,
        "thinking": {"type": "disabled"},
        "json_mode": {"enabled": True}
    },
    {
        "name": "豆包 lite 无思考",
        "vendor": "doubao",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-seed-2-0-lite-260428",
        "api_key": "",
        "temperature": 0.9,
        "max_tokens": 2000,
        "thinking": {"type": "disabled"},
        "json_mode": {"enabled": True}
    },
    {
        "name": "LM Studio Gemma E4B",
        "vendor": "lmstudio",
        "base_url": "http://192.168.5.11:1234",
        "model": "google/gemma-4-e4b",
        "api_key": "lm-studio",
        "temperature": 0.55,
        "max_tokens": 1200,
        "thinking": {"type": "disabled"},
        "json_mode": {"enabled": True}
    },
    {
        "name": "LongCat Flash",
        "vendor": "longcat",
        "base_url": "https://api.longcat.chat",
        "model": "LongCat-Flash-Chat",
        "api_key": "",
        "temperature": 0.7,
        "max_tokens": 2000,
        "thinking": {"type": "disabled"},
        "json_mode": {"enabled": True}
    }
]


# 默认配置
DEFAULT_CONFIG = {
    "llm_profiles": DEFAULT_PROFILES,
    "active_profile": "豆包 mini 无思考",
    "phase_profiles": {
        "init": "LM Studio Gemma E4B",
        "assess": "LM Studio Gemma E4B",
        "result": "豆包 lite 无思考"
    },
    "max_questions": 16,
    "min_questions": 12,
    "preload_enabled": True,
    "easter_egg_enabled": True,
    "active_preset": "暴躁老油条",
    "prompt_presets": get_prompt_presets(),
    "easter_eggs": {
        "schrodinger": 1,
        "hexagon": 3,
        "buddha": 3,
        "double": 3,
        "mouthpiece": 5
    },
    "prompt_init": get_prompt_presets()["暴躁老油条"]["prompt_init"],

    "prompt_assess": get_prompt_presets()["暴躁老油条"]["prompt_assess"],

    "prompt_result": get_prompt_presets()["暴躁老油条"]["prompt_result"]
}


def _migrate_old_config(config):
    """将旧格式 config.json 自动迁移为 profile 格式"""
    # 如果已有 llm_profiles，说明已经是新格式，跳过
    if "llm_profiles" in config and isinstance(config.get("llm_profiles"), list):
        return config

    old_models = {
        "init": config.get("model_init", ""),
        "assess": config.get("model_assess", ""),
        "result": config.get("model_result", ""),
    }
    old_api_key = config.get("api_key", "")
    old_endpoint = config.get("endpoint", "")
    old_temp = config.get("temperature", 0.9)
    old_max_tokens = config.get("max_tokens", 2000)
    old_effort = config.get("reasoning_effort", "minimal")

    # 为每个阶段创建独立 profile
    profiles = []
    phase_map = {}

    for phase, model in old_models.items():
        if not model:
            continue
        name = f"旧配置-{phase}"
        profiles.append({
            "name": name,
            "vendor": "doubao",
            "base_url": old_endpoint,
            "model": model,
            "api_key": old_api_key,
            "temperature": old_temp,
            "max_tokens": old_max_tokens,
            "thinking": {
                "type": "disabled" if old_effort == "minimal" else "enabled",
                "reasoning_effort": old_effort if old_effort != "minimal" else "low"
            }
        })
        phase_map[phase] = name

    # 如果只有一个阶段配了模型，都映射到它
    if len(profiles) == 1:
        phase_map = {"init": profiles[0]["name"], "assess": profiles[0]["name"], "result": profiles[0]["name"]}

    config["llm_profiles"] = profiles
    config["active_profile"] = profiles[0]["name"] if profiles else "默认"
    config["phase_profiles"] = phase_map

    # 清理旧字段
    for old_key in ["api_key", "endpoint", "model_init", "model_assess", "model_result",
                     "temperature", "max_tokens", "reasoning_effort", "model"]:
        config.pop(old_key, None)

    # 如果没有 prompt_presets，从当前 prompts 构建并补充其他预设
    if "prompt_presets" not in config:
        all_presets = get_prompt_presets()
        # 用当前 config 中的 prompts 作为"暴躁老油条"（覆盖默认值，保留用户自定义）
        if "prompt_init" in config and "prompt_assess" in config and "prompt_result" in config:
            all_presets["暴躁老油条"] = {
                "prompt_init": config["prompt_init"],
                "prompt_assess": config["prompt_assess"],
                "prompt_result": config["prompt_result"]
            }
        config["prompt_presets"] = all_presets
        if "active_preset" not in config:
            config["active_preset"] = "暴躁老油条"

    return config


def load_config():
    """加载配置，自动迁移旧格式"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # 自动迁移旧格式
            config = _migrate_old_config(config)
            # 合并默认值
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            # 确保所有 profile 有 json_mode
            for p in config.get("llm_profiles", []):
                if "json_mode" not in p:
                    p["json_mode"] = {"enabled": True}
            for p in config.get("llm_profiles", []):
                if not p.get("api_key"):
                    p["api_key"] = get_api_key(p.get("name", ""))
            # Sync prompts from active_preset
            active_preset = config.get("active_preset", "暴躁老油条")
            presets = config.get("prompt_presets", {})
            if active_preset in presets:
                preset = presets[active_preset]
                config["prompt_init"] = preset.get("prompt_init", config.get("prompt_init", ""))
                config["prompt_assess"] = preset.get("prompt_assess", config.get("prompt_assess", ""))
                config["prompt_result"] = preset.get("prompt_result", config.get("prompt_result", ""))
            return config
    except Exception as e:
        print(f"⚠️ 配置加载失败: {e}")
    return DEFAULT_CONFIG


def save_config(config):
    """保存配置（原子写入）"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    tmp_path = CONFIG_FILE + ".tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, CONFIG_FILE)


def find_profile(config, profile_name):
    """根据名称查找 LLM Profile，找不到返回 None"""
    profiles = config.get("llm_profiles", [])
    for p in profiles:
        if p.get("name") == profile_name:
            return p
    return None


def find_profile_for_phase(config, phase):
    """根据阶段查找对应的 LLM Profile，找不到返回 default"""
    phase_name = config.get("phase_profiles", {}).get(phase)
    if phase_name:
        profile = find_profile(config, phase_name)
        if profile:
            return profile
    # fallback: active_profile
    active = config.get("active_profile")
    if active:
        profile = find_profile(config, active)
        if profile:
            return profile
    # last resort: 第一个 profile
    profiles = config.get("llm_profiles", [])
    return profiles[0] if profiles else None


def get_model_for_phase(config, phase):
    """根据阶段获取对应模型名（兼容旧代码）"""
    profile = find_profile_for_phase(config, phase)
    if profile:
        return profile.get("model", "")
    return "doubao-seed-2-0-lite-260428"
