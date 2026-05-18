#!/usr/bin/env python3
"""NBTI LongCat Presets 端到端测试 - 完整版"""
import json
import os
import sys
import time
import random
import requests
import re
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_BASE = "http://localhost:8081/api"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots", "longcat")
PRESETS = ["暴躁老油条", "冷面纪录片", "戏精闺蜜"]
RUNS_PER_PRESET = 1  # 每个预设跑1次（完整流程约需5-8分钟）

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def parse_answer(text):
    text = text.strip()
    if not text:
        return None
    if text.startswith('{'):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    m = re.search(r'\{\s*"phase"\s*:\s*"(?:ASSESS|RESULT)"[^}]*\}', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass
    return None


def set_active_preset(preset_name):
    try:
        resp = requests.get(f"{API_BASE}/config", timeout=5)
        config = resp.json()
        config["active_preset"] = preset_name
        resp = requests.post(f"{API_BASE}/config", json=config, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"  Error setting preset: {e}")
        return False


def run_single_test(preset_name, run_idx):
    test_id = f"{preset_name}_run{run_idx}"
    print(f"\n{'='*60}")
    print(f"测试: {test_id}")
    print(f"{'='*60}")

    result = {
        "test_id": test_id, "preset": preset_name, "run": run_idx,
        "questions": 0, "result_phase": False, "json_errors": 0,
        "in_range": False, "personality_type": "", "personality_name": "",
        "errors": [], "scenes": [], "comment_samples": []
    }

    # Get min/max from server
    try:
        config = requests.get(f"{API_BASE}/config", timeout=5).json()
        min_q = int(config.get("min_questions", 20))
        max_q = int(config.get("max_questions", 25))
    except:
        min_q, max_q = 20, 25

    try:
        # Start test
        print(f"  发送: 开始测试")
        resp = requests.post(f"{API_BASE}/chat", json={"message": "开始测试", "conversation_id": ""}, timeout=120)
        data = resp.json()
        answer = data.get("answer", "")
        conv_id = data.get("conversation_id", "")

        qdata = parse_answer(answer)
        if not qdata:
            result["errors"].append(f"开场 JSON 解析失败: {answer[:100]}")
            result["json_errors"] += 1
            print(f"  ❌ JSON 解析失败")
            return result

        q = qdata.get("q", 1)
        options = qdata.get("options", [])
        scene = qdata.get("scene", "")[:40]
        print(f"  Q{q}: {scene}... | 选项数={len(options)}")

        # Answer questions
        for round_num in range(35):
            can_conclude = qdata.get("can_conclude", False)

            # Handle can_conclude
            if can_conclude:
                print(f"  AI 判断可结束 (Q{q}), 发送 result 请求...")
                resp = requests.post(f"{API_BASE}/chat", json={
                    "message": "[CAN_CONCLUDE:true]",
                    "conversation_id": conv_id
                }, timeout=120)
                data = resp.json()
                answer = data.get("answer", "")
                qdata = parse_answer(answer)

                if qdata and qdata.get("phase") == "RESULT":
                    result["result_phase"] = True
                    result["questions"] = q
                    result["personality_type"] = qdata.get("type", "")
                    result["personality_name"] = qdata.get("name", "")
                    result["in_range"] = min_q <= q <= max_q
                    print(f"  ✅ 结果: Q{q} → {result['personality_type']} {result['personality_name']}")
                    print(f"  {'✅' if result['in_range'] else '❌'} 范围: Q{q} (期望 Q{min_q}-Q{max_q})")

                    # Save result
                    filepath = os.path.join(SCREENSHOT_DIR, f"{test_id}_result.json")
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump({"test_id": test_id, "question_count": q, "result": qdata}, f, ensure_ascii=False, indent=2)
                    break
                else:
                    print(f"  ❌ result 解析失败: {answer[:100]}")
                    result["errors"].append("result 解析失败")
                    break

            # Get options
            options = qdata.get("options", [])
            if not options:
                print(f"  ❌ 无选项")
                result["errors"].append(f"Q{q} 无选项")
                break

            # Random choice
            choice = random.choice(options)
            print(f"  Q{q} 选择: {choice}")

            # Record
            scene = qdata.get("scene", "")[:40]
            comment = qdata.get("comment", "")[:30]
            result["scenes"].append(scene)
            if comment and len(result["comment_samples"]) < 5:
                result["comment_samples"].append(comment)

            # Send choice
            resp = requests.post(f"{API_BASE}/chat", json={
                "message": choice, "conversation_id": conv_id
            }, timeout=120)
            data = resp.json()
            answer = data.get("answer", "")
            qdata = parse_answer(answer)

            if not qdata:
                print(f"  ❌ JSON 解析失败: {answer[:100]}")
                result["errors"].append(f"Q{q} JSON 解析失败")
                result["json_errors"] += 1
                break

            q = qdata.get("q", q + 1)
            scene = qdata.get("scene", "")[:40]
            can_conclude = qdata.get("can_conclude", False)
            print(f"  Q{q}: {scene}... | can_conclude={can_conclude}")

        if not result["result_phase"]:
            result["errors"].append("未在最大轮次内出结果")
            print(f"  ❌ 未出结果")

    except Exception as e:
        result["errors"].append(str(e))
        print(f"  ❌ 异常: {e}")

    return result


def print_report(all_results):
    print(f"\n{'='*80}")
    print("对比报告")
    print(f"{'='*80}")

    # Table header
    print(f"\n{'预设':<12} {'运行':<4} {'题数':<4} {'结果':<4} {'范围':<4} {'人格代码':<8} {'人格名':<10} {'JSON错':<6}")
    print("-" * 60)

    for r in all_results:
        status = "✅" if r["result_phase"] else "❌"
        in_range = "✅" if r["in_range"] else "❌"
        print(f"{r['preset']:<12} {r['run']:<4} {r['questions']:<4} {status:<4} {in_range:<4} {r['personality_type']:<8} {r['personality_name']:<10} {r['json_errors']:<6}")

    # Summary per preset
    print(f"\n{'='*60}")
    by_preset = {}
    for r in all_results:
        by_preset.setdefault(r["preset"], []).append(r)

    for preset in PRESETS:
        runs = by_preset.get(preset, [])
        if not runs:
            continue
        total = len(runs)
        success = sum(1 for r in runs if r["result_phase"])
        in_range = sum(1 for r in runs if r["in_range"])
        avg_q = sum(r["questions"] for r in runs if r["questions"] > 0) / max(success, 1)
        all_comments = []
        for r in runs:
            all_comments.extend(r["comment_samples"])

        print(f"\n  {preset}:")
        print(f"    成功率: {success}/{total}")
        print(f"    范围内: {in_range}/{total}")
        print(f"    平均题数: {avg_q:.1f}")
        if all_comments:
            print(f"    吐槽示例:")
            for c in all_comments[:3]:
                print(f"      - {c}")

    # Save report
    report_path = os.path.join(SCREENSHOT_DIR, "test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": all_results,
            "summary": {
                preset: {
                    "total": len(runs),
                    "success": sum(1 for r in runs if r["result_phase"]),
                    "in_range": sum(1 for r in runs if r["in_range"]),
                    "avg_questions": sum(r["questions"] for r in runs if r["questions"] > 0) / max(sum(1 for r in runs if r["result_phase"]), 1)
                }
                for preset, runs in by_preset.items()
            }
        }, f, ensure_ascii=False, indent=2)
    print(f"\n报告已保存: {report_path}")


def main():
    print("NBTI LongCat Presets 端到端测试")
    print(f"预设: {PRESETS}")
    print(f"每预设运行: {RUNS_PER_PRESET} 次")

    # Check server
    try:
        resp = requests.get(f"{API_BASE}/config", timeout=5)
        if resp.status_code != 200:
            print("❌ 服务器未运行")
            sys.exit(1)
        config = resp.json()
        min_q = config.get("min_questions", 20)
        max_q = config.get("max_questions", 25)
        print(f"✅ 服务器已连接 | min={min_q}, max={max_q}")
    except Exception as e:
        print(f"❌ 无法连接服务器: {e}")
        sys.exit(1)

    all_results = []

    for preset in PRESETS:
        print(f"\n切换预设: {preset}")
        if not set_active_preset(preset):
            print(f"❌ 设置预设失败")
            continue

        for run_idx in range(1, RUNS_PER_PRESET + 1):
            result = run_single_test(preset, run_idx)
            all_results.append(result)
            time.sleep(2)

    print_report(all_results)

    total = len(all_results)
    success = sum(1 for r in all_results if r["result_phase"])
    in_range = sum(1 for r in all_results if r["in_range"])
    print(f"\n总结: {success}/{total} 成功, {in_range}/{total} 在范围内")
    return 0 if success == total and in_range == total else 1


if __name__ == "__main__":
    sys.exit(main())
