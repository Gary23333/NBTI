#!/usr/bin/env python3
"""验证 server.py 的 LLM Profile 配置系统"""
import sys
import json
import os

# 确保能找到 server.py
sys.path.insert(0, '/Users/guanzizheng/Movies/项目/NBGZ')
import server

print("=" * 60)
print("1. 测试默认配置结构")
print("=" * 60)
dc = server.DEFAULT_CONFIG
assert "llm_profiles" in dc, "缺少 llm_profiles"
assert isinstance(dc["llm_profiles"], list), "llm_profiles 应为数组"
assert len(dc["llm_profiles"]) >= 2, "至少 2 个默认 profile"
assert "phase_profiles" in dc, "缺少 phase_profiles"
assert dc["phase_profiles"]["init"] == "豆包 mini 无思考"
assert dc["phase_profiles"]["assess"] == "豆包 mini 无思考"
assert dc["phase_profiles"]["result"] == "豆包 lite 无思考"
print("✅ 默认配置结构正确")

print("\n" + "=" * 60)
print("2. 测试旧格式配置自动迁移")
print("=" * 60)
old_config = {
    "api_key": "old-key-123",
    "endpoint": "https://old.volces.com/api/v3",
    "model_init": "doubao-seed-old-init",
    "model_assess": "doubao-seed-old-assess",
    "model_result": "doubao-seed-old-result",
    "temperature": 0.5,
    "max_tokens": 1500,
    "reasoning_effort": "medium",
    "prompt_init": "old prompt",
}

migrated = server._migrate_old_config(old_config.copy())
assert "llm_profiles" in migrated, "迁移后缺少 llm_profiles"
assert len(migrated["llm_profiles"]) == 3, f"应有 3 个 profile，实际 {len(migrated['llm_profiles'])}"
assert migrated["phase_profiles"]["init"] != migrated["phase_profiles"]["result"], "不同阶段应有不同 profile"
assert "api_key" not in migrated, "旧字段 api_key 应被清理"
assert "endpoint" not in migrated, "旧字段 endpoint 应被清理"

# 验证每个 profile 内容
for p in migrated["llm_profiles"]:
    assert p["vendor"] == "doubao", f"迁移后 vendor 应为 doubao"
    assert p["api_key"] == "old-key-123", f"api_key 未正确迁移"
    assert p["base_url"] == "https://old.volces.com/api/v3", f"base_url 未正确迁移"
    assert p["thinking"]["type"] == "enabled", f"reasoning_effort=medium 应向 thinking.type=enabled"
    assert p["thinking"]["reasoning_effort"] == "medium", f"reasoning_effort 未正确迁移"
print("✅ 旧格式 → 新格式迁移正确")
print(f"   生成 profile 数: {len(migrated['llm_profiles'])}")
for p in migrated["llm_profiles"]:
    print(f"   - {p['name']}: {p['model']} (vendor={p['vendor']})")

print("\n" + "=" * 60)
print("3. 测试旧格式（minimal=不思考）迁移")
print("=" * 60)
old_minimal = {"api_key": "k", "endpoint": "e", "model_init": "m", "reasoning_effort": "minimal"}
m2 = server._migrate_old_config(old_minimal.copy())
assert m2["llm_profiles"][0]["thinking"]["type"] == "disabled"
assert m2["llm_profiles"][0]["thinking"]["reasoning_effort"] == "low"
print("✅ minimal → thinking.type=disabled")

print("\n" + "=" * 60)
print("4. 测试 find_profile / find_profile_for_phase")
print("=" * 60)
config = server.DEFAULT_CONFIG.copy()
# 使用默认配置查找
p = server.find_profile(config, "豆包 mini 无思考")
assert p is not None
assert p["model"] == "doubao-seed-2-0-mini-260428"
print(f"✅ find_profile('豆包 mini 无思考') → model={p['model']}")

p2 = server.find_profile_for_phase(config, "init")
assert p2 is not None
assert p2["model"] == "doubao-seed-2-0-mini-260428"
print(f"✅ find_profile_for_phase('init') → {p2['name']}")

p3 = server.find_profile_for_phase(config, "result")
assert p3["model"] == "doubao-seed-2-0-lite-260428"
print(f"✅ find_profile_for_phase('result') → {p3['name']}")

# 不存在的 profile fallback
p4 = server.find_profile(config, "不存在的")
assert p4 is None
p5 = server.find_profile_for_phase({"phase_profiles": {}, "llm_profiles": config["llm_profiles"]}, "init")
assert p5 is not None  # fallback to first profile
print(f"✅ 找不到时 fallback 到第一个 profile: {p5['name']}")

print("\n" + "=" * 60)
print("5. 测试 build_thinking_params — 豆包")
print("=" * 60)

# 豆包 - 关闭思考
profile_doubao_off = {
    "vendor": "doubao",
    "thinking": {"type": "disabled"}
}
params = server.build_thinking_params(profile_doubao_off)
assert params == {}, f"豆包关闭思考应返回空，实际: {params}"
print("✅ 豆包 thinking.type=disabled → {}")

# 豆包 - 开启思考
profile_doubao_on = {
    "vendor": "doubao",
    "thinking": {"type": "enabled", "reasoning_effort": "high"}
}
params = server.build_thinking_params(profile_doubao_on)
assert params == {"reasoning_effort": "high"}, f"豆包开启思考参数错误: {params}"
print("✅ 豆包 thinking.type=enabled → {reasoning_effort: 'high'}")

print("\n" + "=" * 60)
print("6. 测试 build_thinking_params — DeepSeek")
print("=" * 60)

# DeepSeek - 关闭思考
profile_ds_off = {
    "vendor": "deepseek",
    "thinking": {"type": "disabled"}
}
params = server.build_thinking_params(profile_ds_off)
assert params == {}, f"DeepSeek 关闭思考应返回空，实际: {params}"
print("✅ DeepSeek thinking.type=disabled → {}")

# DeepSeek - 开启思考 high
profile_ds_high = {
    "vendor": "deepseek",
    "thinking": {"type": "enabled", "reasoning_effort": "high"}
}
params = server.build_thinking_params(profile_ds_high)
assert params["thinking"] == {"type": "enabled"}, f"DeepSeek 缺少 thinking.type: {params}"
assert params["reasoning_effort"] == "high", f"DeepSeek reasoning_effort 错误: {params}"
print("✅ DeepSeek thinking.type=enabled + reasoning_effort=high")

# DeepSeek - 开启思考 max
profile_ds_max = {
    "vendor": "deepseek",
    "thinking": {"type": "enabled", "reasoning_effort": "max"}
}
params = server.build_thinking_params(profile_ds_max)
assert params["reasoning_effort"] == "max", f"DeepSeek max 模式错误: {params}"
print("✅ DeepSeek thinking.type=enabled + reasoning_effort=max")

print("\n" + "=" * 60)
print("7. 测试 config.json 文件迁移（如有旧文件）")
print("=" * 60)
config_path = os.path.join(os.path.dirname(__file__), 'data', 'config.json')
if os.path.exists(config_path):
    config = server.load_config()
    assert "llm_profiles" in config, "加载后缺少 llm_profiles"
    assert isinstance(config["llm_profiles"], list), "llm_profiles 格式错误"
    print(f"✅ config.json 加载成功，{len(config['llm_profiles'])} 个 profile")
    for p in config["llm_profiles"]:
        print(f"   - {p['name']} ({p.get('vendor','?')}): {p['model']}")
else:
    print("⚠️  config.json 不存在，跳过文件迁移测试")

print("\n" + "=" * 60)
print("✅ 全部测试通过！")
print("=" * 60)
