#!/usr/bin/env python3
"""前端资产测试：通过 subprocess 调 node 校验 JS 语法与纯逻辑功能。

JS 文件均为 IIFE，顶层不碰 document（仅在函数内引用），因此注入
`global.window = {}` 后即可被 node require，直接测试其纯逻辑接口。
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

NODE = shutil.which("node")
if NODE is None:
    pytest.skip("node 不可用，跳过前端资产测试", allow_module_level=True)

ROOT = Path(__file__).resolve().parent.parent
NODE_TIMEOUT = 15  # 每次 node 调用的超时秒数

JS_FILES = [
    "app.js",
    "avatar-generator.js",
    "radar-chart.js",
    "share-poster.js",
    "compat-data.js",
    "sw.js",
]


def run_node(args):
    """运行 node 并返回 CompletedProcess；失败信息带 stderr；超时按失败处理。"""
    try:
        return subprocess.run(
            [NODE] + args,
            capture_output=True,
            text=True,
            timeout=NODE_TIMEOUT,
            cwd=str(ROOT),
        )
    except subprocess.TimeoutExpired as e:
        pytest.fail(f"node 调用超时（{NODE_TIMEOUT}s）: {args}\nstderr:\n{e.stderr}")


def run_node_or_fail(args):
    proc = run_node(args)
    assert proc.returncode == 0, (
        f"node 退出码 {proc.returncode}: {args}\nstderr:\n{proc.stderr}"
    )
    return proc


def js_harness(filename, body):
    """构造 node -e 脚本：window 垫片 + require 目标文件 + 测试体。"""
    target = json.dumps((ROOT / filename).as_posix())
    return (
        "const assert = require('assert');\n"
        "global.window = {};\n"
        f"require({target});\n"
        f"{body}"
    )


def run_js_or_fail(filename, body):
    return run_node_or_fail(["-e", js_harness(filename, body)])


# ---------- 语法检查：node --check ----------

@pytest.mark.parametrize("filename", JS_FILES)
def test_js_syntax_node_check(filename):
    proc = run_node(["--check", str(ROOT / filename)])
    assert proc.returncode == 0, (
        f"node --check 失败: {filename}\nstderr:\n{proc.stderr}"
    )


# ---------- compat-data.js 功能 ----------

def test_compat_same_type_title():
    run_js_or_fail("compat-data.js", """
const r = window.NBTICompat.getCompat('NBTI', 'NBTI');
assert.ok(r, 'getCompat(NBTI, NBTI) 返回 null');
assert.strictEqual(r.title, '世另我', '相同类型 title 应为 世另我');
""")


def test_compat_opposite_title():
    run_js_or_fail("compat-data.js", """
const r = window.NBTICompat.getCompat('NBTI', 'SHFP');
assert.ok(r, 'getCompat(NBTI, SHFP) 返回 null');
assert.strictEqual(r.title, '欢喜冤家', '完全相反类型 title 应为 欢喜冤家');
""")


def test_compat_score_range_and_dims():
    run_js_or_fail("compat-data.js", """
const pairs = [['NBTI', 'NBTI'], ['NBTI', 'SHFP'], ['NBTP', 'SHFI'], ['SBTI', 'NHFP']];
for (const [a, b] of pairs) {
  const r = window.NBTICompat.getCompat(a, b);
  assert.ok(r, `getCompat(${a}, ${b}) 返回 null`);
  assert.ok(typeof r.score === 'number' && r.score >= 0 && r.score <= 100,
    `score 超出 0-100: ${a}/${b} -> ${r.score}`);
  assert.strictEqual(r.dims.length, 4, `dims 长度应为 4: ${a}/${b}`);
}
""")


def test_compat_deterministic():
    run_js_or_fail("compat-data.js", """
const a = window.NBTICompat.getCompat('NBTP', 'SHFI');
const b = window.NBTICompat.getCompat('NBTP', 'SHFI');
assert.deepStrictEqual(a, b, '同输入两次调用结果必须深等（确定性）');
""")


def test_compat_easter_egg_score_null():
    run_js_or_fail("compat-data.js", """
for (const egg of window.NBTICompat.EASTER_EGGS) {
  const r = window.NBTICompat.getCompat(egg, 'NBTI');
  assert.ok(r, `getCompat(${egg}, NBTI) 返回 null`);
  assert.strictEqual(r.score, null, `彩蛋类型 score 应为 null: ${egg}`);
}
const r2 = window.NBTICompat.getCompat('NBTI', 'buddha');
assert.ok(r2 && r2.score === null, '彩蛋在第二参数时 score 也应为 null');
""")


def test_compat_invalid_input_returns_null():
    run_js_or_fail("compat-data.js", """
assert.strictEqual(window.NBTICompat.getCompat('XXXX', 'NBTI'), null, '非法类型码应返回 null');
assert.strictEqual(window.NBTICompat.getCompat('NBTI', 'not-a-type'), null, '非法类型码应返回 null');
assert.strictEqual(window.NBTICompat.getCompat('', 'NBTI'), null, '空字符串应返回 null');
assert.strictEqual(window.NBTICompat.getCompat(null, undefined), null, '非字符串应返回 null');
""")


def test_compat_full_matrix_no_exception():
    run_js_or_fail("compat-data.js", """
const types = Object.keys(window.NBTICompat.TYPES);
assert.strictEqual(types.length, 16, '应为 16 种类型');
for (const a of types) {
  for (const b of types) {
    const r = window.NBTICompat.getCompat(a, b);
    assert.ok(r, `getCompat(${a}, ${b}) 返回 null`);
    assert.ok(typeof r.score === 'number' && r.score >= 0 && r.score <= 100,
      `score 超出 0-100: ${a}/${b} -> ${r.score}`);
    assert.strictEqual(r.dims.length, 4, `dims 长度应为 4: ${a}/${b}`);
    assert.ok(r.title, `缺少 title: ${a}/${b}`);
  }
}
""")


# ---------- radar-chart.js 功能 ----------

def test_radar_svg_contains_svg_tag():
    run_js_or_fail("radar-chart.js", """
const svg = window.NBTIRadar.getRadarSvg({ nb: 5, bh: -3, tf: 0, ip: 8 });
assert.ok(typeof svg === 'string' && svg.includes('<svg'), '输出应包含 <svg');
""")


def test_radar_extreme_inputs_no_throw():
    run_js_or_fail("radar-chart.js", """
window.NBTIRadar.getRadarSvg({ nb: 0, bh: 0, tf: 0, ip: 0 });
window.NBTIRadar.getRadarSvg({ nb: 10, bh: 10, tf: 10, ip: 10 });
window.NBTIRadar.getRadarSvg({ nb: -10, bh: -10, tf: -10, ip: -10 });
window.NBTIRadar.getRadarSvg({});
window.NBTIRadar.getRadarSvg(null);
""")


def test_radar_size_option_applied():
    run_js_or_fail("radar-chart.js", """
const svg = window.NBTIRadar.getRadarSvg({ nb: 1, bh: 2, tf: 3, ip: 4 }, { size: 480 });
assert.ok(svg.includes('width="480"'), 'opts.size 未生效，预期 width="480"');
""")


# ---------- share-poster.js 静态检查 ----------

def test_share_poster_static_source():
    src = (ROOT / "share-poster.js").read_text(encoding="utf-8")
    for token in ("NBTIPoster", "generateCompat", "750", "1200"):
        assert token in src, f"share-poster.js 缺少关键内容: {token!r}"
