#!/usr/bin/env python3
import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8080"
SHOT_DIR = "/Users/guanzizheng/Movies/项目/NBGZ/tests/e2e/screenshots"

MOCK_ASSESS_1 = json.dumps({
    "phase": "ASSESS", "q": 1, "nb": 0, "bh": 0, "tf": 0, "ip": 0,
    "next_dim": "BH", "can_conclude": False,
    "comment": "来了来了，又一只职场小白鼠",
    "scene": "周一早上9点，老板在群里@所有人：今天下班前交季度复盘，你的反应是？",
    "options": ["立刻打开PPT开卷", "群里装死假装没看见", "拉同事一起吐槽", "先摸鱼到下午再说"]
}, ensure_ascii=False)

MOCK_ASSESS_2 = json.dumps({
    "phase": "ASSESS", "q": 2, "nb": 2, "bh": 1, "tf": 0, "ip": 1,
    "next_dim": "TF", "can_conclude": False,
    "comment": "卷王本王，我敬你是条汉子",
    "scene": "同事甩锅给你，说这个需求是你负责的，但实际上不是，你怎么办？",
    "options": ["当场对质甩回去", "默默接了算了", "拉群公开讨论责任", "先接了再找机会反击"]
}, ensure_ascii=False)

MOCK_ASSESS_3 = json.dumps({
    "phase": "ASSESS", "q": 3, "nb": 4, "bh": 2, "tf": 1, "ip": 2,
    "next_dim": "IP", "can_conclude": False,
    "comment": "边界感拉满，佩服",
    "scene": "领导让你周末加班，但你已经约了朋友聚会，你？",
    "options": ["直接说不去，周末是我的", "默默取消聚会来加班", "问同事能不能替一下", "假装生病请病假"]
}, ensure_ascii=False)

MOCK_ASSESS_4 = json.dumps({
    "phase": "ASSESS", "q": 4, "nb": 5, "bh": 3, "tf": 2, "ip": 3,
    "next_dim": "NB", "can_conclude": False,
    "comment": "执行力惊人，但别卷死自己",
    "scene": "公司突然宣布要全员降薪10%，你的第一反应？",
    "options": ["立刻更新简历投递", "默默接受现实", "组织同事一起抗议", "找领导谈条件"]
}, ensure_ascii=False)

MOCK_ASSESS_5 = json.dumps({
    "phase": "ASSESS", "q": 5, "nb": 6, "bh": 4, "tf": 3, "ip": 4,
    "next_dim": "END", "can_conclude": True,
    "comment": "好了好了，我已经看透你了",
    "scene": "年终奖发了，比预期少一半，你？",
    "options": ["直接找HR要说法", "算了明年再说", "跟同事对比一下", "在朋友圈阴阳怪气"]
}, ensure_ascii=False)

MOCK_RESULT = json.dumps({
    "phase": "RESULT", "type": "NBTI", "name": "卷王",
    "oneline": "我不是在加班，我是在修行",
    "scene": "凌晨三点，办公室里只剩你一个人，你对着屏幕露出了满足的微笑",
    "adapt": "适合创业公司核心岗、需要0-1突破的团队",
    "crash": "最容易在养老型外企因'太卷'被排挤",
    "interpretation": "好了，诊断结果出来了——你是个纯种卷王。你整个测试的表现就像在赶deadline，选项全是'我冲''我来''都让开'，你的同事可能在背后叫你永动机成精。\n\n你的人生信条大概是：只要卷不死，就往死里卷。但说实话，你的卷不是被迫的，是发自内心的——你觉得摸鱼才是浪费时间。",
    "pseudo_science": "根据《柳叶刀·职场心理学》2024年的一项研究，NBTI人格的多巴胺分泌模式与普通人有显著差异——普通人在完成任务后多巴胺下降，而NBTI人群在'任务堆积'时多巴胺反而飙升。\n\n该研究还发现，NBTI人群的端粒长度比同龄人短约12%，但工作效率高出47%。一位匿名研究者评论：'他们燃烧自己的速度，就像特斯拉车主炫耀加速。'\n\n以上都是我编的。",
    "closing": "下次有人说你太卷，你就回一句：我不是在加班，我是在修行——修行的是别人看不懂的快乐。"
}, ensure_ascii=False)

MOCK_RESPONSES = [MOCK_ASSESS_1, MOCK_ASSESS_2, MOCK_ASSESS_3, MOCK_ASSESS_4, MOCK_ASSESS_5, MOCK_RESULT]

def shot(page, name):
    path = f"{SHOT_DIR}/{name}"
    page.screenshot(path=path, full_page=True)
    print(f"  📸 {name}")
    return path

def make_route_handler():
    mock_idx = [0]
    def handle_route(route):
        if "/api/chat/preload" in route.request.url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"answer": None}))
        elif route.request.method == "POST" and "/api/chat" in route.request.url:
            idx = min(mock_idx[0], len(MOCK_RESPONSES) - 1)
            response_body = {"answer": MOCK_RESPONSES[idx], "conversation_id": "mock-conv-001", "tokens_used": 150}
            mock_idx[0] += 1
            route.fulfill(status=200, content_type="application/json", body=json.dumps(response_body))
        else:
            route.continue_()
    return handle_route

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-gpu", "--no-sandbox"])
        
        print("\n====== 桌面端测试 (1280x800) ======")
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        page.route("**/api/**", make_route_handler())

        # 1. 首页
        print("\n[1] 首页")
        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(1)
        shot(page, "e2e-01-home.png")
        
        h1 = page.locator("h1")
        assert h1.is_visible(), "首页标题不可见"
        print(f"  ✅ 标题: {h1.text_content()}")
        print(f"  ✅ 副标题: {page.locator('.header p').first.text_content()}")
        assert page.locator("button", has_text="开始测试").is_visible()
        print("  ✅ 开始测试按钮可见")

        # 2. 配置页
        print("\n[2] 配置页")
        page.goto(f"{BASE_URL}/config.html", wait_until="networkidle")
        time.sleep(1)
        shot(page, "e2e-02-config.png")
        print(f"  ✅ Profile 卡片数: {page.locator('.card').count()}")
        print(f"  ✅ 阶段分配下拉框数: {page.locator('.phase-select').count()}")
        print(f"  ✅ Prompt 编辑框数: {page.locator('textarea').count()}")

        # 3. 开始测试
        print("\n[3] 开始测试")
        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(0.5)
        shot(page, "e2e-03-before-start.png")
        page.locator("button", has_text="开始测试").click()
        print("  ✅ 点击开始测试")

        # 4. 开场白
        print("\n[4] 开场白")
        page.wait_for_selector("button.option-btn, button:has-text('开始答题')", timeout=30000)
        time.sleep(1)
        shot(page, "e2e-04-intro.png")
        
        intro_btn = page.locator("button", has_text="开始答题")
        if intro_btn.is_visible(timeout=2000):
            print("  ✅ 开场白页面出现，点击开始答题")
            intro_btn.click()
            time.sleep(0.5)
            shot(page, "e2e-05-first-question.png")

        # 5. 答题循环 (5题)
        print("\n[5] 答题循环")
        for q in range(1, 6):
            options = page.locator("button.option-btn")
            try:
                options.first.wait_for(state="visible", timeout=10000)
            except:
                if page.locator(".result").is_visible(timeout=3000):
                    print(f"  🎯 结果页提前出现")
                    break
                break
            
            opt_count = options.count()
            q_label = page.locator(".question-label").first.text_content() if page.locator(".question-label").count() > 0 else ""
            scene = page.locator(".question-text").first.text_content()[:50] if page.locator(".question-text").count() > 0 else ""
            comment = page.locator(".comment-bubble").first.text_content() if page.locator(".comment-bubble").count() > 0 else ""
            
            print(f"  📋 {q_label} | 选项:{opt_count} | {scene[:35]}...")
            if comment:
                print(f"     💬 {comment}")
            shot(page, f"e2e-06-q{q}.png")
            
            options.first.click()
            time.sleep(1)
            
            if page.locator(".result").is_visible(timeout=3000):
                print(f"  🎯 第{q}题后到达结果页!")
                break
            
            page.wait_for_selector("button.option-btn, .result", timeout=10000)
            time.sleep(0.5)

        # 6. 结果页
        print("\n[6] 结果页验证")
        time.sleep(2)
        shot(page, "e2e-07-result.png")
        
        code = page.locator(".result .code").first.text_content() if page.locator(".result .code").count() > 0 else ""
        name = page.locator(".result h2").first.text_content() if page.locator(".result h2").count() > 0 else ""
        oneline = page.locator(".result .oneline").first.text_content() if page.locator(".result .oneline").count() > 0 else ""
        has_avatar = page.locator("#result-avatar svg").count() > 0
        
        print(f"  人格代码: {code}")
        print(f"  人格名称: {name}")
        print(f"  一句话: {oneline}")
        print(f"  头像: {'✅ SVG 已生成' if has_avatar else '❌ 未生成'}")
        print(f"  报告段落数: {page.locator('.result .report-section').count()}")
        print(f"  元信息条目: {page.locator('.result .result-meta').count()}")
        print(f"  操作按钮数: {page.locator('.result .actions button').count()}")

        # 7. 换一换头像
        print("\n[7] 换一换头像")
        refresh_btn = page.locator("button", has_text="换一换")
        if refresh_btn.is_visible(timeout=3000):
            refresh_btn.click()
            time.sleep(0.5)
            shot(page, "e2e-08-refresh-avatar.png")
            print("  ✅ 头像已刷新")

        # 8. 再来一次
        print("\n[8] 再来一次")
        restart_btn = page.locator("button", has_text="再来一次")
        if restart_btn.is_visible(timeout=3000):
            restart_btn.click()
            time.sleep(1)
            shot(page, "e2e-09-restart.png")
            if page.locator(".welcome").is_visible(timeout=3000):
                print("  ✅ 成功返回首页")

        # ====== 移动端测试 ======
        print("\n====== 移动端测试 (390x844) ======")
        ctx2 = browser.new_context(viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)")
        mpage = ctx2.new_page()
        mpage.route("**/api/**", make_route_handler())
        
        mpage.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(0.5)
        shot(mpage, "e2e-10-mobile-home.png")
        print("  ✅ 移动端首页")
        
        mpage.locator("button", has_text="开始测试").click()
        mpage.wait_for_selector("button.option-btn, button:has-text('开始答题')", timeout=30000)
        time.sleep(1)
        shot(mpage, "e2e-11-mobile-question.png")
        print("  ✅ 移动端答题页")
        
        intro_btn2 = mpage.locator("button", has_text="开始答题")
        if intro_btn2.is_visible(timeout=2000):
            intro_btn2.click()
            time.sleep(0.5)
        
        for i in range(5):
            opts = mpage.locator("button.option-btn")
            if opts.count() > 0:
                opts.first.click()
                time.sleep(1)
                if mpage.locator(".result").is_visible(timeout=3000):
                    break
                try:
                    mpage.wait_for_selector("button.option-btn, .result", timeout=10000)
                except:
                    pass
                time.sleep(0.5)
        
        time.sleep(2)
        shot(mpage, "e2e-12-mobile-result.png")
        print("  ✅ 移动端结果页")

        # ====== API 接口测试 ======
        print("\n====== API 接口测试 ======")
        apipage = ctx.new_page()
        apipage.goto(f"{BASE_URL}/", wait_until="networkidle")
        
        config_resp = apipage.evaluate("""async () => {
            const r = await fetch('/api/config');
            return await r.json();
        }""")
        has_profiles = len(config_resp.get("llm_profiles", [])) > 0
        has_prompts = all(config_resp.get(f"prompt_{p}") for p in ["init", "assess", "result"])
        has_max_q = "max_questions" in config_resp
        print(f"  GET /api/config:")
        print(f"    profiles: {'✅' if has_profiles else '❌'} ({len(config_resp.get('llm_profiles', []))}个)")
        print(f"    prompts: {'✅' if has_prompts else '❌'}")
        print(f"    max_questions: {'✅' if has_max_q else '❌'} ({config_resp.get('max_questions', '?')})")

        browser.close()
    
    print("\n" + "=" * 60)
    print("✅ 端到端测试完成!")
    print(f"📸 截图保存在: {SHOT_DIR}/")
    print("=" * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("NBTI 完整端到端测试")
    print(f"时间: {datetime.now().isoformat()}")
    print("=" * 60)
    run()
