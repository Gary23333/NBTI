<p align="center">
  <img src="https://img.shields.io/badge/v3.0-终极升级版-ff69b4?style=for-the-badge" />
  <img src="https://img.shields.io/badge/7-测试主题-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/7-吐槽风格-FFD700?style=for-the-badge" />
  <img src="https://img.shields.io/badge/41-程序化头像-00C853?style=for-the-badge" />
  <img src="https://img.shields.io/badge/AI-Powered-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LLMs-4%20Vendors-ff69b4?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Streaming-SSE-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/PWA-Ready-5A0FC8?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-Flask-000?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/Frontend-Vanilla%20JS-F7DF1E?style=for-the-badge&logo=javascript" />
  <img src="https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

<h1 align="center">
  NBTI · 牛比体 v3.0
  <br/>
  <sub>🎊 终极升级版 🎊</sub>
  <br/>
  <sub>Your Personality, Roasted by AI × 7 Themes</sub>
  <br/>
  <sub>专治各种不服 · 7大主题任你选</sub>
</h1>

<p align="center">
  <i>Not another personality test. This one has attitude. And 7 themes. And animal CP compatibility.</i>
  <br/>
  <i>不是又一个山寨测试。这个有脾气，有7大主题，还有动物CP合盘。</i>
</p>

<p align="center">
  <a href="#v30-新亮点--whats-new-in-v30">v3.0 新亮点</a> ·
  <a href="#quick-start--快速开始">Quick Start</a> ·
  <a href="#the-flex--功能特性">Features</a> ·
  <a href="#tech-stack--技术栈">Tech Stack</a> ·
  <a href="#configuration">Configuration</a> ·
  <a href="#development">Development</a> ·
  <a href="#contributing">Contributing</a> ·
  <a href="#license">License</a>
</p>

---

## 🎉 v3.0 新亮点 / What's New in v3.0

> **EN** — The Ultimate Upgrade is here! 7 test themes, 7 roast styles, 41 procedural avatars, brand-new 2026 UI, themed share posters, and animal CP compatibility readings.

> **CN** — 终极升级版来了！7大测试主题、7种吐槽风格、41种程序化头像、2026全新UI、多主题海报、动物CP合盘。

<table>
<tr>
<td width="50%">

### 🎯 7 大测试主题
- **💼 职场人格** — 经典16种职场角色（核心）
- **🐾 动物系人格** — 你是哪种动物？揭秘野性人格（核心）
- **🎨 色彩人格** — 你的灵魂是什么颜色？色彩心理学（核心）
- **💕 恋爱人格** — 你的爱情模式是什么？*更多主题持续更新*
- **👥 社交人格** — 社牛还是社恐？*更多主题持续更新*
- **🧠 官方MBTI** — 经典16型心理学视角 *更多主题持续更新*
- **🤯 脑洞人格** — 你的脑回路有多清奇？*更多主题持续更新*

### 🎭 7 种吐槽风格
- 🔥 暴躁老油条（经典损友）
- 🎬 冷面纪录片（BBC旁白）
- 💅 戏精闺蜜（八卦连续剧）
- 👑 霸总文学（霸道宠溺）
- 🔮 玄学算命（半仙附体）
- 🌸 二次元萌系（JK软妹）
- 📊 官方MBTI（专业中立）

### 🖼️ 多主题海报 & 动物CP合盘
- 每种主题专属配色海报
- 动物CP配对合盘，专属默契指数
- 一键分享，朋友圈炫图神器

</td>
<td width="50%">

### 🤖 41 种程序化头像
- **16** 种职场人格头像（随机SVG生成）
- **5** 种彩蛋人格特效头像
- **12** 种动物系专属头像（狮子/狐狸/猫头鹰/海豚/鹿/猫/狼/企鹅/章鱼/树懒/蝴蝶/熊）
- **8** 种色彩系光影头像
- 每次刷新都是全新面孔，零图片素材纯代码生成

### ✨ 2026 全新UI
- 全新视觉设计，主题切换流畅动画
- 主题选择页精美卡片式布局
- 响应式设计，移动端体验拉满
- 暗黑/亮色主题自动适配
- 更丝滑的交互动效

### 🚀 其他升级
- 主题+风格任意组合，49种玩法
- 题目选项数量智能调整（2-4个）
- 更丰富的场景出题逻辑
- 分享海报自动适配主题配色
- 合盘海报支持跨主题CP计算

</td>
</tr>
</table>

---

## Quick Start / 快速开始

### Docker (Recommended / 推荐)

```bash
git clone https://github.com/Gary23333/NBTI.git
cd NBTI

# 复制配置模板，填入你的 API Key
cp data/config.json.example data/config.json
# 编辑 data/config.json 填入 API Key

# 一键启动
docker-compose up -d

# 打开浏览器访问
open http://localhost:8080
```

### Manual / 手动启动

```bash
git clone https://github.com/Gary23333/NBTI.git
cd NBTI
pip install -r requirements.txt

# 复制配置模板，填入你的 API Key
cp data/config.json.example data/config.json
# 编辑 data/config.json

# 终端 1：启动后端 API（仅本地，持有 API 密钥）
python server.py

# 终端 2：启动前端代理（公网可访问）
python frontend_server.py 8080

# 打开浏览器
open http://localhost:8080          # 首页（主题选择）
open http://localhost:8080/config.html  # 配置管理页
```

### Production / 生产部署

```bash
# 使用 Gunicorn（已在 requirements.txt 中）
gunicorn -c gunicorn.conf.py server:app

# 或直接 Docker
docker-compose up -d
```

---

## The Flex / 功能特性

<table>
<tr>
<td width="50%">

### 🎯 Multi-Theme Engine (NEW!)
7 test themes at launch: Workplace, Animal, Color as core themes; Love, Social, MBTI, Brainhol as work-in-progress (more themes coming soon). Each theme has unique dimensions, 16 personalities, easter eggs, and visual styling.

### 🎭 7 Roast Styles (NEW!)
Switch between 7 prompt personas at runtime — from sarcastic homie to overbearing CEO, from fortune teller to anime moe. 49 unique theme×style combinations.

### Real AI, Not a Spreadsheet
No hardcoded branching logic. Every question is **improvised by an LLM** based on your previous answers. Options are 2-4 per question, intelligently matched to scene complexity.

### Multi-LLM Profiles Engine
Hot-swap between **4 vendors** at runtime. Assign different models to different phases (init/assess/result). Test connectivity with one click. JSON mode per profile.

### Streaming + Preloading Pipeline
SSE streaming renders responses in real-time. While you're staring at a question, the next one is **already being generated** for all answer branches. Instant transitions.

### 41 Procedural Avatars (NEW!)
Each personality type across all themes gets a **randomly generated SVG avatar** — unique every time. 16 workplace + 5 easter eggs + 12 animals + 8 colors = 41 type definitions. Zero image assets, pure math.

</td>
<td width="50%">

### 🎯 多主题引擎（全新！）
首发7大测试主题：职场、动物、色彩为核心主题；恋爱、社交、MBTI、脑洞持续更新中。每个主题有独立维度定义、16种人格、彩蛋人格和视觉风格。

### 🎭 7种吐槽风格（全新！）
运行时切换7种提示词人设——从暴躁损友到霸道总裁，从玄学大师到二次元萌妹。49种主题×风格组合任你玩。

### 真 AI，不是 Excel
没有硬编码的题目分支。每一道题都是大模型根据你的历史回答**即兴生成的**。每道题2-4个选项，智能匹配场景复杂度。

### 多模型热插拔引擎
运行时在 4 个供应商之间**任意切换**。不同阶段（开场/出题/结果）可分配不同模型。连通性一键测试。JSON 模式独立开关。

### 流式渲染 + 预加载流水线
SSE 实时渲染每个字。你还在看题，下一题的 4 个分支答案**已经生成好了**。秒级切题，体验丝滑。

### 41种程序化头像（全新！）
所有主题的每种人格都有**随机生成的SVG头像**——每次都不一样。16职场+5彩蛋+12动物+8色彩=41种类型定义。零图片素材，纯数学生成。

</td>
</tr>
<tr>
<td width="50%">

### 4-Layer JSON Parsing
LLMs love to wrap JSON in markdown blocks, add preambles, or cut off mid-response. Our parser eats all of that for breakfast.

### Hidden Easter Egg Types
Schrödinger's Employee (translucent), Hexagon Warrior (golden glow), Workplace Buddha (aura), Two-Face (split-color), Meme Lord (barrage). 5 hidden types per theme with special avatar effects.

### 🖼️ Multi-Theme Posters (NEW!)
Share posters automatically adapt to the selected theme's color palette. One-click **750×1200 Canvas share poster** (avatar + type + one-liner + radar + branding). Theme-matched visual style every time.

### 🐾 Animal CP Compatibility (NEW!)
Two personality codes in, one CP verdict out. Local rule engine computes a **match score, combo name, per-dimension reading** — with easter-egg combos as fallback. Generates its own themed compat poster. Works across themes! Zero LLM calls, pure spice.

### Shareable Everything
30-day read-only share links (`/share/<id>`). Roast your friends without giving them your API key. Result page ships with a **4-dimension radar chart**.

### PWA + Resume Anywhere
Installable to home screen (manifest + service worker + icon). Test progress persists to localStorage — refresh, close, come back tomorrow, pick up exactly where the roast left off.

</td>
<td width="50%">

### 四层 JSON 解析兜底
大模型喜欢给 JSON 套 markdown 代码块、加前缀废话、或者中途截断。我们的解析器四层递进，吃一切吐一切。

### 彩蛋人格
薛定谔的打工人（半透明）、六边形战士（金色光环）、职场活佛（佛光）、职场双面人（分色）、互联网嘴替（弹幕）。每个主题5种隐藏人格+专属头像特效。

### 🖼️ 多主题海报（全新！）
分享海报自动适配所选主题的配色方案。一键生成 **750×1200 Canvas 分享海报**（头像+人格+一句话锐评+雷达+品牌位）。每次都是匹配主题的视觉风格。

### 🐾 动物CP合盘（全新！）
两个人格代码进去，一个CP审判结果出来。本地规则引擎给出**合拍指数、CP组合名、逐维度解读**，彩蛋组合兜底。生成专属主题合盘海报。支持跨主题CP计算！零 LLM 调用，纯干货。

### 万物皆可分享
30天只读分享链接（`/share/<id>`）。毒舌好友，用不着交出你的 API Key。结果页自带**四维雷达图**。

### PWA + 断点续测
可添加到主屏（manifest + service worker + icon）。答题进度写入 localStorage——刷新、关掉、明天再来，接着上次被毒舌的地方继续。

</td>
</tr>
</table>

---

## Test Themes / 测试主题一览

| Theme | Icon | Status | Description |
|-------|------|--------|-------------|
| 职场人格 | 💼 | ✅ 核心主题 | 16种经典职场角色定位 |
| 动物系人格 | 🐾 | ✅ 核心主题 | 16种动物人格，12种专属动物头像 |
| 色彩人格 | 🎨 | ✅ 核心主题 | 色彩心理学，8种光影特效头像 |
| 恋爱人格 | 💕 | 🚧 持续更新 | 揭秘你的爱情模式 |
| 社交人格 | 👥 | 🚧 持续更新 | 社牛社恐真实鉴定 |
| 官方MBTI | 🧠 | 🚧 持续更新 | 经典心理学16型 |
| 脑洞人格 | 🤯 | 🚧 持续更新 | 奇葩脑回路大测试 |

> More themes coming soon! 更多主题持续更新中...

---

## AI-Generated Avatars / 程序化头像家族

Each personality type gets a **procedurally generated, one-of-a-kind SVG avatar** — no two are ever the same. Every result page is a visual surprise. Total: **41 unique type definitions** across all themes.

**Workplace (16 + 5 easter eggs):**
<p align="center">
  <img src="docs/avatars/NBTI.svg" width="80" title="卷王 NBTI" />
  <img src="docs/avatars/NBTP.svg" width="80" title="棋手 NBTP" />
  <img src="docs/avatars/NHTI.svg" width="80" title="霸总 NHTI" />
  <img src="docs/avatars/NHFP.svg" width="80" title="气氛组 NHFP" />
  <img src="docs/avatars/SBTI.svg" width="80" title="工蚁 SBTI" />
  <img src="docs/avatars/SBFP.svg" width="80" title="扫地僧 SBFP" />
  <img src="docs/avatars/SHTI.svg" width="80" title="大管家 SHTI" />
  <img src="docs/avatars/SHFP.svg" width="80" title="职场空气 SHFP" />
</p>

**Easter Eggs (5):**
<p align="center">
  <img src="docs/avatars/schrodinger.svg" width="80" title="薛定谔的打工人" />
  <img src="docs/avatars/hexagon.svg" width="80" title="六边形战士" />
  <img src="docs/avatars/buddha.svg" width="80" title="职场活佛" />
  <img src="docs/avatars/twoface.svg" width="80" title="职场双面人" />
  <img src="docs/avatars/meme_lord.svg" width="80" title="互联网嘴替" />
</p>

| Generation System | Types Count | Features |
|-------------------|-------------|----------|
| Workplace Human Avatars | 21 (16+5) | Procedural face, hair, eyes, accessories, effects |
| Animal Head Avatars | 12 | Hand-drawn animal heads (lion, fox, owl, dolphin, deer, cat, wolf, penguin, octopus, sloth, butterfly, bear) |
| Color Light Avatars | 8 | Rainbow glow, glitch, special color effects |

> **Zero external assets.** No PNGs. No icon fonts. Pure `<svg>` math.

---

## Architecture / 架构

```
┌──────────────────────────────────────────────────────┐
│                  Public (IPv4/IPv6)                  │
│  http://[your-ip]:8080                               │
└────────────────────────┬─────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────┐
│            Frontend Server (:8080)                    │
│  • Static files only (HTML/CSS/JS)                   │
│  • Proxies /api/* → backend                          │
│  • ZERO API keys                                     │
│  • Listens on :: (all interfaces)                    │
└────────────────────────┬─────────────────────────────┘
                         │  API proxy
┌────────────────────────▼─────────────────────────────┐
│            Backend API (:8081)                        │
│  ┌─────────────────────────────────────────────┐     │
│  │  nbti/                                      │     │
│  │    app.py          Flask app + routes       │     │
│  │    config.py       Config + LLM profiles    │     │
│  │    themes.py       7 multi-theme definitions│     │
│  │    prompts.py      7 style prompt templates │     │
│  │    llm.py          LLM client + streaming   │     │
│  │    conversation.py Thread-safe storage      │     │
│  │    utils.py        Parsing + normalization  │     │
│  └─────────────────────────────────────────────┘     │
│  • API keys (never exposed to frontend)              │
│  • Listens on 127.0.0.1 ONLY                         │
└──────────────────────────────────────────────────────┘
```

### Security Model / 安全模型

- **Key isolation** — API keys live only in the backend on `127.0.0.1`; the frontend server holds zero secrets and proxies `/api/*` with trusted `X-Forwarded-For`.
- **Admin token** — Config writes (`POST /api/config`, reset, test-connection) and the full `GET /api/config` require an `X-Admin-Token` header matching env `NBTI_ADMIN_TOKEN`. If the env var is unset, only localhost requests count as admin. `config.html` has a token input and degrades to read-only mode without it.
- **Key masking** — Non-admin `GET /api/config` responses mask every `api_key` (`***` + last 4 chars).
- **Rate limiting** — `/api/chat*` and `POST /api/share` are IP-limited (`rate_limit_per_minute`, default 30, 0 = unlimited); abuse gets `429` + `retry_after`.
- **Hardening** — `conversation_id` whitelist validation (no path traversal), `base_url` scheme validation on test-connection (no SSRF), no wide-open CORS, all LLM output escaped before rendering (no XSS), truncated streams never persisted.
- **Data hygiene** — Conversations expire after 24h, share snapshots after 30 days (periodic cleanup).

---

## Tech Stack / 技术栈

| Layer | Tech | v3.0 Updates |
|-------|------|--------------|
| Frontend | Vanilla HTML/CSS/JS | 🆕 2026全新UI，主题切换动画，卡片式主题选择 |
| Backend | Python Flask + SSE streaming | 🆕 多主题引擎，7种风格prompt系统 |
| Themes System | `nbti/themes.py` | 🆕 7大测试主题定义（3核心+4开发中） |
| LLMs | Doubao (Volces Ark) · DeepSeek · LM Studio · LongCat | 4 vendors, hot-swappable per phase |
| Prompt System | `nbti/prompts.py` | 🆕 7种吐槽风格：暴躁老油条/冷面纪录片/戏精闺蜜/霸总文学/玄学算命/二次元萌系/官方MBTI |
| Output | JSON structured + 4-layer parse fallback | Smart options (2-4 per question) |
| Avatars | Pure SVG procedural generator | 🆕 41种头像：16职场+5彩蛋+12动物+8色彩 |
| Posters | Canvas poster generator | 🆕 多主题配色海报，动物CP合盘海报 |
| Compatibility | `compat-data.js` | 🆕 跨主题CP合盘引擎 |
| Themes | Dark / Light, auto-detect | 🆕 主题联动视觉系统 |
| PWA | manifest.json + sw.js + icon.svg | Installable, resumable |
| Charts | radar-chart.js (SVG radar) | Theme-aware radar charts |
| Deploy | Docker + Gunicorn (workers=1, threads=8) | Production-ready |
| CI | GitHub Actions (Python 3.10 / 3.11 / 3.12) | Comprehensive test suite |

---

## Configuration / 配置

### API Keys

Copy the example config and fill in your API keys:

```bash
cp data/config.json.example data/config.json
```

Or use environment variables (overrides config.json at runtime):

```bash
export NBTI_API_KEY_LONGCAT=your_key
export NBTI_API_KEY_DEEPSEEK_V4_FLASH=your_key
export NBTI_API_KEY_DOUBAO=your_key

# Admin token for config write APIs (X-Admin-Token header).
# If unset, only localhost requests are treated as admin.
export NBTI_ADMIN_TOKEN=your_admin_token
```

### LLM Profiles

Each profile bundles: vendor, endpoint, model, API key, temperature, thinking mode, JSON mode. Mix-and-match per phase (init/assess/result).

Supported vendors:

| Vendor | Example Model | Notes |
|--------|--------------|-------|
| Doubao | doubao-seed-2-0-mini | ByteDance / Volces Ark |
| DeepSeek | deepseek-v4-flash | Thinking mode supported |
| LM Studio | google/gemma-4-e4b | Local inference |
| LongCat | LongCat-Flash-Chat | Built-in thinking models |

### Roast Styles / 吐槽风格预设

7 built-in personas, switchable at runtime:

- **🔥 暴躁老油条 / Roast Homie** — Sarcastic internet friend, roasts you with love (classic)
- **🎬 冷面纪录片 / BBC Narrator** — Cold, clinical observation with deadpan humor
- **💅 戏精闺蜜 / Gossip Bestie** — Dramatic, over-the-top soap opera reaction
- **👑 霸总文学 / CEO Romance** — Overbearing CEO, possessive yet doting
- **🔮 玄学算命 / Fortune Teller** — Mystical Zhongnan Mountain hermit, cryptic wisdom
- **🌸 二次元萌系 / Anime Moe** — Soft JK girl with Japanese speech patterns and emoticons
- **📊 官方MBTI / Certified MBTI** — Professional, neutral psychology assessment

### Game Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| min_questions | 12 | AI cannot conclude before this |
| max_questions | 16 | AI forced to conclude at this |
| preload_enabled | true | Preload next-question drafts for all answer branches |
| rate_limit_per_minute | 30 | Per-IP rate limit on chat/share APIs (0 = unlimited) |
| easter_egg_enabled | true | Enable hidden personality types |

---

## Project Structure / 项目结构

```
NBTI/
├── server.py              # Backend entry point
├── frontend_server.py     # Static file server + API proxy
├── app.js                 # Frontend logic (SSE streaming, theme switch, rendering)
├── avatar-generator.js    # Procedural SVG avatar generator (41 types)
├── radar-chart.js         # 4-dimension SVG radar chart (theme-aware)
├── share-poster.js        # 750×1200 Canvas share/compat poster (multi-theme)
├── compat-data.js         # Friend/Animal CP compatibility rule engine
├── style.css              # Main stylesheet (2026 new UI)
├── index.html             # Test page (theme selection + test flow)
├── share.html             # Read-only shared result + CP compat page
├── config.html            # Admin config panel
├── config.css             # Config panel styles
├── manifest.json          # PWA manifest
├── sw.js                  # Service worker (static asset cache)
├── icon.svg               # PWA icon
├── nbti/                  # Backend Python package
│   ├── app.py             # Flask app + all API routes
│   ├── config.py          # Config management
│   ├── themes.py          # 🆕 7 multi-theme definitions
│   ├── prompts.py         # 🆕 7 style prompt templates
│   ├── llm.py             # LLM client + streaming
│   ├── conversation.py    # Thread-safe storage
│   └── utils.py           # Parsing + normalization
├── data/
│   └── config.json.example  # Config template
├── tests/                 # Test suite
├── docs/
│   ├── avatars/           # 21 SVG avatar samples
│   └── screenshots/
├── Dockerfile
├── docker-compose.yml
├── gunicorn.conf.py
├── requirements.txt
├── start.sh
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE                # MIT
```

---

## Development / 开发

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run only unit + integration tests (no e2e, no manual)
pytest tests/ -v --ignore=tests/e2e --ignore=tests/test_deepseek.py --ignore=tests/test_longcat_presets.py --ignore=tests/test_preload.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add new themes, prompt presets, LLM vendors, and personality types.

---

## Contributing / 参与贡献

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest tests/ -v`)
4. Commit your changes (`git commit -m 'feat: add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## Changelog / 更新日志

See [CHANGELOG.md](CHANGELOG.md) for release history. Full v3.0 changelog in the changelog file.

---

## License / 开源协议

This project is licensed under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2026 Gary23333

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

<p align="center">
  <b>NBTI · 牛比体 v3.0</b><br/>
  <sub>🎊 终极升级版 · 7大主题 · 41种头像 · 你的人格，被AI毒舌了 🎊</sub><br/>
  <sub>Your personality. Roasted. In 7 ways.</sub>
</p>
