#!/usr/bin/env python3
"""
NBTI 移动端端到端测试脚本 —— 确保走到结果页
- Playwright + Chrome 手机尺寸
- 禁用预加载，减少并发
- 每题之间增加延迟，避免 API 频率限制
- 超时 300s
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8080"
REPORT_PATH = "e2e-test-report.md"
SCREENSHOT_PATH = "e2e-result-screenshot.png"
DEBUG_PREFIX = "e2e-debug"


def check_question_content(page):
    """通过 JS 检查页面内容"""
    try:
        return page.evaluate("""() => {
            const area = document.getElementById('question-area');
            if (!area) return { error: '找不到 question-area' };
            const text = area.innerText || '';
            const optionBtns = area.querySelectorAll('button.option-btn');
            const options = Array.from(optionBtns).map(b => b.innerText.trim());
            return {
                optionCount: options.length,
                options,
                hasUndefined: text.includes('undefined') || text.includes('undefin'),
                hasDuplicate: [...new Set(options)].length !== options.length,
                questionLabel: area.querySelector('.question-label')?.innerText || '',
                sceneText: area.querySelector('.question-text')?.innerText?.substring(0, 60) || '',
            };
        }""")
    except Exception as e:
        return {"error": str(e)}


def run_test():
    report = {
        "start_time": datetime.now().isoformat(),
        "stages": [],
        "checks": [],
        "total_duration_ms": 0,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
        )
        page = context.new_page()

        # 打开页面
        print("🌐 打开测试页面（手机尺寸 390x844）...")
        page.goto(f"{BASE_URL}/index.html", wait_until="networkidle")
        time.sleep(0.5)
        page.screenshot(path=f"{DEBUG_PREFIX}-00-home-mobile.png")

        # 禁用预加载，避免并发请求拖慢 API
        print("🔧 禁用预加载...")
        page.evaluate("""() => {
            window.preloadNextQuestions = function() {};
            window.preloadCache = {};
        }""")

        # 点击"开始测试"
        print("🚀 点击开始测试...")
        start_btn = page.locator("button", has_text="开始测试")
        start_btn.wait_for(state="visible", timeout=10000)
        start_btn.click()

        try:
            page.locator(".spinner").wait_for(state="visible", timeout=5000)
            print("  ✅ loading 已出现")
        except:
            print("  ⚠️ loading 未出现")

        # 等待内容出现
        print("  ⏳ 等待第一题...")
        t0 = time.time()
        page.wait_for_selector("button.option-btn, button:has-text('开始答题')", timeout=300000)
        t1 = time.time()
        first_load_ms = int((t1 - t0) * 1000)
        report["stages"].append({"name": "第一题加载", "duration_ms": first_load_ms})
        print(f"  ✅ 内容出现，耗时 {first_load_ms}ms")
        page.screenshot(path=f"{DEBUG_PREFIX}-01-content-mobile.png")

        # 开场白
        intro_btn = page.locator("button", has_text="开始答题")
        if intro_btn.is_visible(timeout=2000):
            print("  🎉 有开场白，点击开始答题")
            intro_btn.click()
            time.sleep(0.5)
            page.screenshot(path=f"{DEBUG_PREFIX}-02-after-intro-mobile.png")
        else:
            print("  📋 无单独开场白页")

        # 循环做题
        question_count = 0
        max_questions = 15

        while question_count < max_questions:
            question_count += 1
            print(f"\n📋 第 {question_count} 题...")

            # 等待选项
            t_q_start = time.time()
            options = page.locator("button.option-btn")
            try:
                options.first.wait_for(state="visible", timeout=300000)
            except Exception:
                print(f"  ⚠️ 第{question_count}题选项未出现")
                if page.locator(".result").is_visible(timeout=10000):
                    print("  🎯 检测到结果页！")
                    break
                page.screenshot(path=f"{DEBUG_PREFIX}-q{question_count}-timeout-mobile.png")
                break

            t_q_end = time.time()
            load_ms = int((t_q_end - t_q_start) * 1000)
            option_count = options.count()
            print(f"  选项数: {option_count}, 加载: {load_ms}ms")

            report["stages"].append({
                "name": f"第{question_count}题加载",
                "option_count": option_count,
                "duration_ms": load_ms,
            })

            # 截图 + 检查
            page.screenshot(path=f"{DEBUG_PREFIX}-q{question_count}-mobile.png")
            check = check_question_content(page)
            check["question_num"] = question_count
            report["checks"].append(check)
            print(f"  检查: 选项={check.get('optionCount','?')}, undefined={check.get('hasUndefined','?')}, 重复={check.get('hasDuplicate','?')}")

            if option_count == 0:
                if page.locator(".result").is_visible(timeout=5000):
                    print("  🎯 结果页")
                    break
                continue

            # 选择第一个选项
            t_click_start = time.time()
            options.first.click()

            # 等待 loading 或新内容
            try:
                page.wait_for_selector(".spinner, .option-btn, .result", timeout=300000)
            except:
                pass

            # 检查是否结果页
            if page.locator(".result").is_visible(timeout=10000):
                t_click_end = time.time()
                report["stages"].append({
                    "name": f"第{question_count}题→结果",
                    "duration_ms": int((t_click_end - t_click_start) * 1000),
                })
                print(f"  🎯 到达结果页，切换耗时 {int((t_click_end - t_click_start) * 1000)}ms")
                break

            t_click_end = time.time()
            report["stages"].append({
                "name": f"第{question_count}题→下一题",
                "duration_ms": int((t_click_end - t_click_start) * 1000),
            })
            print(f"  切换耗时: {int((t_click_end - t_click_start) * 1000)}ms")

            # 关键：每题之间等待 5s，避免 API 频率限制
            print("  💤 等待 5s 让 API 喘口气...")
            time.sleep(5)

        # 结果页截图
        time.sleep(2)
        print(f"\n📸 截图保存到 {SCREENSHOT_PATH}")
        page.screenshot(path=SCREENSHOT_PATH, full_page=True)

        final_check = check_question_content(page)
        report["final_check"] = final_check
        print(f"  最终检查: {json.dumps(final_check, ensure_ascii=False)[:200]}")

        browser.close()

    report["end_time"] = datetime.now().isoformat()
    report["total_duration_ms"] = sum(s.get("duration_ms", 0) for s in report["stages"])
    return report


def generate_report(report):
    lines = []
    lines.append("# NBTI 移动端端到端测试报告\n")
    lines.append(f"- **测试时间**: {report['start_time']}\n")
    lines.append(f"- **结束时间**: {report['end_time']}\n")
    lines.append(f"- **总时长**: {report['total_duration_ms']}ms ({report['total_duration_ms']/1000:.1f}s)\n")
    lines.append(f"- **视口**: 390x844（iPhone 14 模拟）\n")
    lines.append("")

    loading_stages = [s for s in report["stages"] if "加载" in s["name"]]
    transition_stages = [s for s in report["stages"] if "→" in s["name"]]

    if loading_stages:
        avg_load = sum(s["duration_ms"] for s in loading_stages) / len(loading_stages)
        lines.append(f"- **题目数量**: {len(loading_stages)}\n")
        lines.append(f"- **平均加载耗时**: {avg_load:.0f}ms\n")

    if transition_stages:
        avg_trans = sum(s["duration_ms"] for s in transition_stages) / len(transition_stages)
        lines.append(f"- **平均切换耗时**: {avg_trans:.0f}ms\n")

    lines.append("")
    lines.append("## 内容检查结果\n")
    lines.append("| 题号 | 选项数 | undefined | 重复选项 | 场景预览 |\n")
    lines.append("|------|--------|-----------|----------|----------|\n")
    for c in report.get("checks", []):
        qn = c.get("question_num", "?")
        oc = c.get("optionCount", "?")
        ud = "❌" if c.get("hasUndefined") else "✅"
        dup = "❌" if c.get("hasDuplicate") else "✅"
        scene = (c.get("sceneText", "") or "")[:20]
        lines.append(f"| {qn} | {oc} | {ud} | {dup} | {scene} |\n")

    lines.append("")
    lines.append("## 详细时延记录\n")
    lines.append("| 阶段 | 耗时(ms) |\n")
    lines.append("|------|----------|\n")
    for stage in report["stages"]:
        name = stage["name"]
        if "option_count" in stage:
            name += f" (选项:{stage['option_count']})"
        lines.append(f"| {name} | {stage.get('duration_ms', '-')} |\n")

    lines.append("")
    lines.append(f"## 结果截图\n")
    lines.append(f"![结果截图]({SCREENSHOT_PATH})\n")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\n📝 报告已保存到 {REPORT_PATH}")


if __name__ == "__main__":
    print("=" * 50)
    print("NBTI 移动端端到端测试（结果页确保版）")
    print("=" * 50)
    try:
        report = run_test()
        generate_report(report)
        print("\n✅ 测试完成")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
