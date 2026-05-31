<p align="center">
  <img src="https://img.shields.io/badge/AI-Powered-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LLMs-4%20Vendors-ff69b4?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Streaming-SSE-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-Flask-000?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/Frontend-Vanilla%20JS-F7DF1E?style=for-the-badge&logo=javascript" />
  <img src="https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker" />
</p>

<h1 align="center">
  NBTI · 牛比体
  <br/>
  <sub>Your Workplace DNA, Roasted by AI</sub>
  <br/>
  <sub>专治各种职场不服</sub>
</h1>

<p align="center">
  <i>Not another MBTI clone. This one has attitude.</i>
  <br/>
  <i>不是又一个 MBTI 山寨。这个有脾气。</i>
</p>

---

> **EN** — NBTI is an AI-powered workplace personality test that hooks you up with one of 16 hilariously accurate archetypes — from "Workaholic King" to "Workplace Air". Powered by real LLMs (Doubao, DeepSeek, LM Studio, LongCat), it asks improv scenarios, tracks your vibes across 4 dimensions, and delivers a roast so personal you'll wonder if it read your Slack DMs.

> **CN** — NBTI 是 AI 驱动的职场人格测试。连接真实大模型（豆包、DeepSeek、LM Studio、LongCat），用场景化灵魂拷问评估你 4 个维度的行为倾向，给出 16 种人格中属于你的那一个——从「卷王」到「职场空气」，毒舌程度让你怀疑它偷看了你的钉钉。

---

## Quick Start / 快速开始

### Docker (Recommended / 推荐)

```bash
git clone https://github.com/Gary23333/NBTI.git
cd NBTI

# Copy and edit config
cp data/config.json.example data/config.json
# Edit data/config.json with your API keys

# Run with Docker
docker-compose up -d

# Open
open http://localhost:8080
```

### Manual / 手动启动

```bash
pip install -r requirements.txt

# Copy and edit config
cp data/config.json.example data/config.json
# Edit data/config.json with your API keys

# Terminal 1: Backend API
python server.py

# Terminal 2: Frontend
python frontend_server.py 8080

# Open
open http://localhost:8080
```

---

## The Flex / 为什么牛逼

<table>
<tr>
<td width="50%">

### Real AI, Not a Spreadsheet
No hardcoded branching logic. Every question is **improvised by an LLM** based on your previous answers. 3 prompt personas to choose from.

### Multi-LLM Profiles Engine
Hot-swap between **4 vendors** at runtime. Assign different models to different phases (init/assess/result). Test connectivity with one click.

### Streaming + Preloading Pipeline
SSE streaming renders responses in real-time. While you're staring at a question, the next one is **already being generated** for all answer branches.

### Procedural Avatar Generator
Each of the 16 types gets a **randomly generated SVG avatar** — unique every time. Pure math. Every refresh = brand new face.

### 4-Layer JSON Parsing
LLMs love to wrap JSON in markdown blocks, add preambles, or cut off mid-response. Our parser eats all of that for breakfast.

### Docker Ready
One command deployment with Docker Compose. Environment variable support for API keys. Production-ready with Gunicorn.

</td>
<td width="50%">

### 真 AI，不是 Excel
没有硬编码的题目分支。每一道题都是大模型根据你的历史回答**即兴生成的**。3 套提示词人设一键切换。

### 多模型热插拔引擎
运行时在 4 个供应商之间**任意切换**。不同阶段可分配不同模型。连通性一键测试。

### 流式渲染 + 预加载流水线
SSE 实时渲染每个字。你还在看题，下一题的 4 个分支答案**已经生成好了**。秒级切题，体验丝滑。

### 程序化头像生成器
16 种人格每种配一个**随机生成的 SVG 头像**——每次都不一样。纯数学运算，零图片素材。

### 四层 JSON 解析兜底
大模型喜欢给 JSON 套 markdown 代码块、加前缀废话、或者中途截断。我们的解析器四层递进，吃一切吐一切。

### Docker 一键部署
一条命令启动。环境变量注入 API 密钥。Gunicorn 生产级服务。

</td>
</tr>
</table>

## 16 Personalities / 16 种人格

| Code | Name | Tagline |
|------|------|---------|
| NBTI | 卷王 | 我不是在加班，我是在修行 |
| NBTP | 棋手 | 棋盘上就我一个活人 |
| NBFI | 独狼 | 一个人干翻一个部门 |
| NBFP | 浪子 | 简历像一部冒险小说 |
| NHTI | 霸总 | 我不是在PUA你 |
| NHTP | 教练 | 我培养英雄 |
| NHFI | 护犊子 | 天塌了我顶着 |
| NHFP | 气氛组 | 公司没我早散了 |
| SBTI | 工蚁 | 我让所有灯都亮着 |
| SBTP | 人形计算器 | 感情会影响判断 |
| SBFI | 螺丝钉 | 最无聊但最不可替代 |
| SBFP | 扫地僧 | 你以为我是青铜 |
| SHTI | 大管家 | 诸葛亮都没我会排 |
| SHTP | 质检警察 | 99.9%不行，要100% |
| SHFI | 居委会大妈 | 有矛盾找我 |
| SHFP | 职场空气 | 随缘随风随工资条 |

> Plus hidden easter egg types — Schrodinger's Employee, Hexagon Warrior, Workplace Buddha, Two-Face, and Meme Lord.

## AI-Generated Avatars

Each personality type gets a **procedurally generated, one-of-a-kind SVG avatar** — no two are ever the same.

<p align="center">
  <img src="docs/avatars/NBTI.svg" width="120" title="卷王 NBTI" />
  <img src="docs/avatars/NBTP.svg" width="120" title="棋手 NBTP" />
  <img src="docs/avatars/NHTI.svg" width="120" title="霸总 NHTI" />
  <img src="docs/avatars/NHFP.svg" width="120" title="气氛组 NHFP" />
  <img src="docs/avatars/SBTI.svg" width="120" title="工蚁 SBTI" />
  <img src="docs/avatars/SBFP.svg" width="120" title="扫地僧 SBFP" />
</p>

## Architecture / 架构

```
Browser → Frontend :8080 → proxy /api/* → Backend :8081 → LLM APIs

nbti/                  Backend Python package
  app.py               Flask app + all API routes
  config.py            Config management + LLM profiles
  prompts.py           3 prompt personas (暴躁老油条/冷面纪录片/戏精闺蜜)
  llm.py               LLM client, streaming, thinking params
  conversation.py      Thread-safe conversation storage
  utils.py             JSON parsing, normalization, easter eggs
```

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Vanilla HTML/CSS/JS — zero dependencies |
| Backend | Python Flask + SSE streaming |
| LLMs | Doubao · DeepSeek · LM Studio · LongCat |
| Deploy | Docker + Gunicorn |
| CI | GitHub Actions (Python 3.10/3.11/3.12) |

## Configuration

Copy `data/config.json.example` to `data/config.json` and add your API keys. Or use environment variables:

```bash
export NBTI_API_KEY_DEEPSEEK_V4_FLASH=your_key
```

## Development

```bash
# Run tests
pytest tests/ -v

# See CONTRIBUTING.md for how to add presets, vendors, and personality types
```

## License

MIT

---

<p align="center">
  <b>NBTI · 牛比体</b><br/>
  <sub>Your personality. Roasted.</sub>
</p>
