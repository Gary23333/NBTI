#!/usr/bin/env python3
"""NBTI 前端截图采集脚本：用 Playwright + Chromium 抓 6 张页面截图。

环境假设：
- 后端 Flask: http://127.0.0.1:8081 （/api/* 无 LLM key 时会 401/500，必须用 page.route mock）
- 前端静态: http://127.0.0.1:8080
- 截图输出: /workspace/docs/screenshots/
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, Route, Request, TimeoutError as PWTimeout

OUTPUT_DIR = Path("/workspace/docs/screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FRONTEND = "http://127.0.0.1:8080"
VIEWPORT = {"width": 1440, "height": 900}

# ------------------------------------------------------------------ #
# mock 数据
# ------------------------------------------------------------------ #

# 测试中的 ASSESS（出题）响应 —— q=1 让前端走 renderIntro 分支，出现「开始答题」按钮
ASSESS_ANSWER = {
    "phase": "ASSESS",
    "q": 1,
    "nb": 1, "bh": 0, "tf": 0, "ip": 0,
    "next_dim": "NB",
    "can_conclude": False,
    "comment": "嘿，你这反应挺有意思的",
    "scene": "周一早会，leader 突然宣布本周要连续加班赶项目。你会：",
    "options": [
        "立刻表态：收到，我带头卷",
        "私聊同事建小群吐槽",
        "假装信号不好没听清",
        "默默打开招聘软件",
    ],
}

# 结果页 RESULT 响应
RESULT_ANSWER = {
    "phase": "RESULT",
    "type": "NBTI",
    "name": "卷王",
    "oneline": "我不是在加班，我是在修行",
    "scene": "凌晨两点的工位，咖啡杯摆成阵法，屏幕蓝光映照着他坚定的眼神。",
    "adapt": "高强度创业团队 / 996 项目组 / 急难险重任务",
    "crash": "需要长期主义但短期出活的活 / 模糊不清的KPI",
    "interpretation": (
        "你是一个把「卷」写进 DNA 的人。别人下班是关电脑，你下班是开机重启。"
        "你的日历里没有「休息」这个选项，只有「战略性摸鱼」。"
        "你以为自己在打工，其实你把整条命都焊在了工位上。"
        "老板说「这个需求有点紧」，你的第一反应不是「多紧」，而是「我可以更紧」。"
    ),
    "pseudo_science": (
        "根据最新的「工位依附症」研究表明，长期高强度工作者的大脑前额叶皮层会"
        "发展出一套独特的「加班奖励回路」。每次听到「冲冲冲」三个字，"
        "你的多巴胺分泌量相当于普通人吃三块巧克力。科学家们把这种现象命名为"
        "「卷王悖论」——越累越爽，越爽越累，循环往复，生生不息。"
    ),
    "closing": "愿你的工位永远有光，愿你的 KPI 永远向好。愿世界对你温柔，老板对你宽容。",
}

# 第二个出题响应（preload 用）
ASSESS_NEXT = {
    "phase": "ASSESS",
    "q": 4,
    "nb": 0, "bh": 0, "tf": 0, "ip": 0,
    "next_dim": "TF",
    "can_conclude": False,
    "comment": "风格稳如老狗",
    "scene": "周五下班前 5 分钟，老板又发来新需求。你会：",
    "options": [
        "已读不回假装断网",
        "秒回：周一给您",
        "回个 OK 表情包",
        "打电话给同事吐槽",
    ],
}


def sse_response(answer: dict, conversation_id: str = "demo-conv-001") -> str:
    """生成 SSE 流：first_token + 多 chunk + done。"""
    full_text = json.dumps(answer, ensure_ascii=False)
    # 把整段拆成 ~5 个 chunk，模拟"打字"
    n = 6
    chunks = []
    step = max(len(full_text) // n, 1)
    for i in range(n):
        start = i * step
        end = (i + 1) * step if i < n - 1 else len(full_text)
        chunks.append(full_text[start:end])
    parts = [
        'data: {"event": "first_token", "timestamp": %d}\n\n' % int(time.time() * 1000),
    ]
    for c in chunks:
        parts.append('data: ' + json.dumps({"event": "chunk", "content": c}, ensure_ascii=False) + '\n\n')
    done = {
        "event": "done",
        "answer": full_text,
        "tokens_used": 100,
        "conversation_id": conversation_id,
    }
    parts.append('data: ' + json.dumps(done, ensure_ascii=False) + '\n\n')
    return ''.join(parts)


# ------------------------------------------------------------------ #
# 路由 mock 安装
# ------------------------------------------------------------------ #

def mock_route_for_chat(context, request_log: list, answers: dict, conversation_id: str = "demo-conv-001"):
    """统一拦截 /api/chat*、/api/chat/preload* 返回 mock 数据。

    answers: dict，键可为 'stream'、'preload'、'commit'，值为要返回的答案 dict。
    """
    def handler(route: Route, request: Request):
        url = request.url
        method = request.method
        request_log.append({"url": url, "method": method})
        # 解析 body
        body = {}
        if method == "POST" and request.post_data:
            try:
                body = json.loads(request.post_data)
            except Exception:
                body = {}

        # 决定要返回的答案
        if "/api/chat/preload/commit" in url:
            # commit 通常无草稿可提交，前端会回退到流式；这里让它走 fallback
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"error": "no draft"}, ensure_ascii=False),
            )
            return

        if "/api/chat/preload" in url:
            # preload 返回下一个 ASSESS
            ans = answers.get("preload", ASSESS_NEXT)
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"answer": json.dumps(ans, ensure_ascii=False), "tokens_used": 100},
                                 ensure_ascii=False),
            )
            return

        if "/api/chat/stream" in url or url.endswith("/api/chat/stream") or "/api/chat/stream" in url:
            # chat 流：先看 message 是否包含 [PHASE:RESULT] / [CAN_CONCLUDE:true]
            msg = body.get("message", "")
            if "RESULT" in msg.upper() or "CAN_CONCLUDE" in msg.upper():
                ans = answers.get("result", RESULT_ANSWER)
            else:
                ans = answers.get("stream", ASSESS_ANSWER)
            sse = sse_response(ans, conversation_id=conversation_id)
            # 用 fulfill + 短延迟让客户端能拿到 streaming
            route.fulfill(
                status=200,
                content_type="text/event-stream",
                body=sse,
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )
            return

        if url.endswith("/api/chat") or "/api/chat?" in url:
            ans = answers.get("stream", ASSESS_ANSWER)
            payload = {
                "choices": [{"message": {"content": json.dumps(ans, ensure_ascii=False)}}],
                "answer": json.dumps(ans, ensure_ascii=False),
                "options": ans.get("options", []),
                "conversation_id": conversation_id,
            }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(payload, ensure_ascii=False),
            )
            return

        # 默认放行
        route.continue_()

    context.route("**/api/chat*", handler)


def mock_share_route(context, share_snapshot: dict):
    def handler(route: Route, request: Request):
        if "/api/share/" in request.url and request.method == "GET":
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(share_snapshot, ensure_ascii=False),
            )
            return
        if "/api/share" in request.url and request.method == "POST":
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"id": "demo"}, ensure_ascii=False),
            )
            return
        route.continue_()
    context.route("**/api/share**", handler)


def hide_scrollbars(page):
    page.add_style_tag(content="::-webkit-scrollbar { display: none !important; } body { scrollbar-width: none; }")


# ------------------------------------------------------------------ #
# 截图函数
# ------------------------------------------------------------------ #

def shot_01_theme_selection(p):
    """1. 主题选择页 - 直接打开 /，全页截图。"""
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    context = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
    context.add_init_script("localStorage.setItem('nbti-theme','dark');")
    page = context.new_page()
    page.goto(FRONTEND + "/", wait_until="networkidle", timeout=30000)
    # 等主题卡片渲染
    page.wait_for_selector("#theme-grid .theme-card", timeout=10000)
    page.wait_for_timeout(2000)
    hide_scrollbars(page)
    out = OUTPUT_DIR / "01-theme-selection.png"
    page.screenshot(path=str(out), full_page=True)
    print(f"[1] theme selection -> {out}")
    browser.close()


def shot_02_test_in_progress(p):
    """2. 测试答题中 - mock 流式，逐步显示，截到题目+选项已显示的状态。"""
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    context = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
    context.add_init_script("localStorage.setItem('nbti-theme','dark');")
    request_log = []
    # mock 流式：返回 ASSESS
    mock_route_for_chat(context, request_log, answers={"stream": ASSESS_ANSWER, "preload": ASSESS_NEXT})
    page = context.new_page()
    page.goto(FRONTEND + "/", wait_until="networkidle", timeout=30000)
    page.wait_for_selector("#theme-grid .theme-card", timeout=10000)
    page.wait_for_timeout(800)
    # 点击「职场人格」主题
    page.locator('.theme-card[data-theme-id="workplace"]').click()
    page.wait_for_timeout(600)
    # 应在 style 步骤，点击第一个风格卡
    page.locator('.style-card').first.click()
    page.wait_for_timeout(600)
    # 应在 ready 步骤，点击「开始测试」
    page.locator('.btn-primary:has-text("开始测试")').click()
    # 等流式响应回来渲染出 intro 卡片（含「开始答题」按钮）
    # 注意：初始 streaming shell 里也有同名按钮但被 disabled；等它被替换为可点击的版本
    page.wait_for_function(
        "() => { const btns = document.querySelectorAll('.intro-card button'); for (const b of btns) { if (b.textContent.includes('开始答题') && !b.disabled) return true; } return false; }",
        timeout=20000,
    )
    # 点「开始答题」进入第 1 题
    page.locator('.intro-card button:has-text("开始答题"):not([disabled])').first.click()
    # 等第 1 题渲染
    page.wait_for_selector('.question-card .question-text', timeout=15000)
    # 等选项按钮出现
    page.wait_for_selector('#final-options .option-btn', timeout=15000)
    page.wait_for_timeout(800)
    hide_scrollbars(page)
    out = OUTPUT_DIR / "02-test-in-progress.png"
    page.screenshot(path=str(out), full_page=False)
    print(f"[2] test in progress -> {out}")
    browser.close()


def shot_03_result_page(p):
    """3. 结果页 - 让首次 /api/chat/stream 直接返回 RESULT。"""
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    context = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
    context.add_init_script("localStorage.setItem('nbti-theme','dark');")
    request_log = []
    # 让 init stream 直接返回 RESULT
    mock_route_for_chat(context, request_log, answers={"stream": RESULT_ANSWER, "preload": RESULT_ANSWER})
    page = context.new_page()
    page.goto(FRONTEND + "/", wait_until="networkidle", timeout=30000)
    page.wait_for_selector("#theme-grid .theme-card", timeout=10000)
    page.wait_for_timeout(600)
    page.locator('.theme-card[data-theme-id="workplace"]').click()
    page.wait_for_timeout(400)
    page.locator('.style-card').first.click()
    page.wait_for_timeout(400)
    page.locator('.btn-primary:has-text("开始测试")').click()
    # 等结果页 + 雷达图
    page.wait_for_selector('#page-result.active', timeout=20000)
    page.wait_for_selector('#radar-chart svg', timeout=15000)
    page.wait_for_timeout(1500)
    hide_scrollbars(page)
    out = OUTPUT_DIR / "03-result-page.png"
    page.screenshot(path=str(out), full_page=True)
    print(f"[3] result page -> {out}")
    browser.close()


def shot_04_share_poster(p):
    """4. 分享海报 - 走 share.html + mock /api/share/demo，然后点生成海报，截弹窗。"""
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    context = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
    context.add_init_script("localStorage.setItem('nbti-theme','dark');")

    share_snapshot = {
        "result": RESULT_ANSWER,
        "scores": {"nb": 5, "bh": 2, "tf": 4, "ip": 3},
        "theme": "workplace",
        "theme_info": {"id": "workplace", "name": "职场人格", "icon": "💼"},
        "created_at": int(time.time()),
    }
    mock_share_route(context, share_snapshot)
    # 屏蔽无关的 chat 噪声
    def passthrough(route, request):
        route.continue_()
    context.route("**/api/chat*", passthrough)

    page = context.new_page()
    page.goto(FRONTEND + "/share/demo", wait_until="networkidle", timeout=30000)
    page.wait_for_selector('#share-result .radar-chart svg', timeout=20000)
    page.wait_for_timeout(1500)
    # 点击「📮 生成海报」按钮
    poster_btn = page.locator('button:has-text("生成海报")')
    poster_btn.click()
    # 等待 modal
    page.wait_for_selector('#share-poster-modal.open img', timeout=15000)
    # 等海报画完
    page.wait_for_timeout(1500)
    hide_scrollbars(page)
    out = OUTPUT_DIR / "04-share-poster.png"
    # 直接截整个 modal 区域：使用 locator 截图
    modal = page.locator('#share-poster-modal .poster-modal-inner')
    modal.screenshot(path=str(out))
    print(f"[4] share poster -> {out}")
    browser.close()


def shot_05_cp_compatibility(p):
    """5. CP 合盘页 - share.html，自动选两个 code，点合盘，截图结果区。"""
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    context = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
    context.add_init_script("localStorage.setItem('nbti-theme','dark');")

    share_snapshot = {
        "result": RESULT_ANSWER,
        "scores": {"nb": 5, "bh": 2, "tf": 4, "ip": 3},
        "theme": "workplace",
        "theme_info": {"id": "workplace", "name": "职场人格", "icon": "💼"},
        "created_at": int(time.time()),
    }
    mock_share_route(context, share_snapshot)
    def passthrough(route, request):
        route.continue_()
    context.route("**/api/chat*", passthrough)

    page = context.new_page()
    page.goto(FRONTEND + "/share/demo", wait_until="networkidle", timeout=30000)
    page.wait_for_selector('#share-result .radar-chart svg', timeout=20000)
    # 等 CP 区域
    page.wait_for_selector('.compat-wrap', timeout=15000)
    page.wait_for_timeout(800)
    # 选 SHTP 组合（与 NBTI 互补）
    selects = page.locator('.compat-selects select')
    selects.nth(0).select_option('S')
    selects.nth(1).select_option('H')
    selects.nth(2).select_option('T')
    selects.nth(3).select_option('P')
    # 点合盘
    page.locator('.compat-go').click()
    # 等结果渲染
    page.wait_for_selector('.compat-result:not([hidden]) .compat-ring-wrap svg', timeout=15000)
    page.wait_for_timeout(1200)
    # 滚到合盘结果区
    page.locator('.compat-result').scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    hide_scrollbars(page)
    out = OUTPUT_DIR / "05-cp-compatibility.png"
    # 截整个 viewport
    page.screenshot(path=str(out), full_page=False)
    print(f"[5] cp compatibility -> {out}")
    browser.close()


def shot_06_config_panel(p):
    """6. 配置管理页 - /config.html，全页截图。"""
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    context = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
    context.add_init_script("localStorage.setItem('nbti-theme','dark');")
    page = context.new_page()
    page.goto(FRONTEND + "/config.html", wait_until="networkidle", timeout=30000)
    # 等 profiles 渲染
    page.wait_for_selector('#profiles-container .card', timeout=15000)
    page.wait_for_timeout(2000)
    hide_scrollbars(page)
    out = OUTPUT_DIR / "06-config-panel.png"
    page.screenshot(path=str(out), full_page=True)
    print(f"[6] config panel -> {out}")
    browser.close()


# ------------------------------------------------------------------ #
# main
# ------------------------------------------------------------------ #

def main():
    with sync_playwright() as p:
        shot_01_theme_selection(p)
        shot_02_test_in_progress(p)
        shot_03_result_page(p)
        shot_04_share_poster(p)
        shot_05_cp_compatibility(p)
        shot_06_config_panel(p)


if __name__ == "__main__":
    main()
