# Changelog

## v3.0.0 - 终极升级版 (2026-07-27)

### 🎊 重大更新 (MAJOR)

- **7大测试主题引擎** (`nbti/themes.py`)
  - 💼 **职场人格** — 经典16种职场角色（核心主题，完整支持）
  - 🐾 **动物系人格** — 16种动物人格，12种专属手绘动物头像（核心主题）
  - 🎨 **色彩人格** — 色彩心理学主题，8种光影特效头像（核心主题）
  - 💕 恋爱人格、👥 社交人格、🧠 官方MBTI、🤯 脑洞人格 — 框架就绪，更多主题持续更新
  - 每个主题独立维度定义、人格列表、彩蛋人格、视觉配色系统

- **7种吐槽风格** (`nbti/prompts.py`)
  - 🔥 暴躁老油条（经典）、🎬 冷面纪录片、💅 戏精闺蜜
  - 🆕 👑 霸总文学 — 霸道总裁宠溺文风
  - 🆕 🔮 玄学算命 — 终南山半仙附体
  - 🆕 🌸 二次元萌系 — JK软妹口癖颜文字
  - 🆕 📊 官方MBTI — 专业中立心理学视角
  - 主题×风格任意组合，共49种玩法

- **41种程序化头像系统** (`avatar-generator.js`)
  - 16种职场人类头像 + 5种彩蛋特效头像（原21种）
  - 🆕 12种手绘动物头像：狮子、狐狸、猫头鹰、海豚、鹿、猫、狼、企鹅、章鱼、树懒、蝴蝶、熊
  - 🆕 8种色彩光影头像：彩虹、发光、故障特效
  - 总计41种独特类型定义，每次刷新都是全新面孔，零图片素材

- **🐾 动物CP合盘 & 跨主题兼容** (`compat-data.js`)
  - 🆕 动物CP配对合盘功能，专属默契指数与组合名
  - 🆕 支持跨主题CP计算
  - 🆕 合盘海报自动适配主题配色

- **🖼️ 多主题海报系统** (`share-poster.js`)
  - 分享海报自动适配所选主题配色方案
  - 主题匹配的视觉风格，一键生成750×1200 Canvas PNG

- **✨ 2026全新UI**
  - 🆕 主题选择页卡片式精美布局
  - 🆕 主题切换流畅动画效果
  - 🆕 整体视觉风格升级，交互动效更丝滑
  - 🆕 响应式设计优化，移动端体验拉满
  - 暗黑/亮色主题自动适配

### 🚀 功能增强

- **智能选项数量** — 题目选项支持2-4个，简单场景2个选项（约30%题目），复杂场景3-4个，不再固定4个
- **出题场景多样化** — 优化场景生成逻辑，社交/生活/脑洞/职场场景混合出题
- **主题联动视觉** — 雷达图、海报、头像配色与当前主题联动
- **配置向后兼容** — 默认主题为职场人格，默认风格为暴躁老油条，平滑升级

### 📁 新增/修改文件

- 新增 `nbti/themes.py` — 7大测试主题定义模块
- 重构 `nbti/prompts.py` — 从3种风格扩展到7种风格，支持多主题prompt模板
- 大幅扩展 `avatar-generator.js` — 新增12种动物头像渲染、8种色彩头像特效
- 更新 `share-poster.js` — 多主题配色海报系统
- 更新 `compat-data.js` — 跨主题CP合盘支持
- 更新前端页面与样式 — 2026全新UI、主题选择界面

---

## v2.1.0 (2026-07-27)

### Added
- **Radar chart on result page** (`radar-chart.js`) — 4-dimension radar visualization (NB / BH / TF / IP) rendered as inline SVG
- **Share poster generator** (`share-poster.js`) — 750×1200 native Canvas PNG: avatar + type + one-liner + radar + meta + branding
- **Share links** — `POST /api/share` creates a read-only snapshot served at `/share/<id>` (`share.html`), valid for 30 days
- **Friend compatibility / 好友合盘** (`compat-data.js`) — local rule engine: match score, combo name, per-dimension readings, easter-egg fallback; compat section on `share.html` + compat poster
- **PWA support** — `manifest.json` + `sw.js` (static asset caching) + `icon.svg`; installable to home screen
- **Resume test / 断点续测** — progress persisted to localStorage, restored after refresh
- **Rate limiting** — IP-based limit on `/api/chat*` and `POST /api/share`; config `rate_limit_per_minute` (default 30, 0 = unlimited); returns 429 + `retry_after`
- **Admin token** — config write APIs and `/api/config/test-connection` require `X-Admin-Token` header (env `NBTI_ADMIN_TOKEN`; if unset, only localhost is treated as admin); `config.html` gains token input + read-only mode
- **New tests** — `tests/test_security.py` (28), `tests/test_robustness.py` (12), `tests/test_share.py` (9), `tests/test_frontend_assets.py` (node --check)

### Changed
- **Default question count**: min 20 → **12**, max 25 → **16** (shorter games, same roast quality)
- **New config key** `preload_enabled` (default true) with a toggle in `config.html`
- **Gunicorn tuning**: `workers=1, threads=8` (file-storage constraint); cleanup thread restarted via `post_worker_init`
- **LLM history trimmed** to the most recent 12 messages; question numbering still counts the full history
- **Progress bar** now reflects the actual question count
- **Mobile polish**: safe-area insets, larger touch targets, no horizontal scroll
- **CI**: restored `test_longcat_presets`, added `node --check` step for frontend assets

### Fixed
- **XSS**: all LLM-generated content is escaped before rendering
- **Option button event binding** — answers no longer polluted by escaped text or mismatched preload keys
- **Incomplete-question retry** capped at 3 attempts
- **SSE handling** checks the `done` event first
- **Truncated streaming answers** are no longer persisted to storage

### Security
- `GET /api/config` masks `api_key` for non-admins (`***` + last 4 chars)
- `conversation_id` whitelist validation against path traversal
- `test-connection` validates `base_url` scheme against SSRF
- Removed wide-open CORS
- `frontend_server.py` forwards trusted `X-Forwarded-For`
- Periodic cleanup: conversations expire after 24h, share snapshots after 30 days

## v2.0.0 (2026-06-01)

### Architecture
- **Backend refactored**: `server.py` (2651 lines) decomposed into modular `nbti/` package
  - `nbti/prompts.py` — prompt presets (暴躁老油条, 冷面纪录片, 戏精闺蜜)
  - `nbti/config.py` — configuration management, LLM profile CRUD
  - `nbti/conversation.py` — thread-safe conversation storage
  - `nbti/llm.py` — LLM client, streaming, thinking params, schemas
  - `nbti/utils.py` — JSON parsing, normalization, easter eggs
  - `nbti/app.py` — Flask app factory with all API routes
- `server.py` is now a thin entry point (backward-compatible for tests)

### Security
- Removed API keys from git history (clean repo restart)
- Created `data/config.json.example` with placeholder values
- Created `.env.example` documenting all environment variables
- Updated `.gitignore` for comprehensive file exclusion

### Frontend
- Extracted `config.html` inline CSS to `config.css`
- Enhanced CSS animations: page transitions, progress bar shimmer, comment bubble slide-in, result page entrance sequence
- Improved option button micro-interactions (hover translate, active scale)
- Mobile responsive improvements: 48px touch targets, safe area insets, responsive avatar sizing
- Result page staggered entrance animations

### Deployment
- Added `Dockerfile` with health check
- Added `docker-compose.yml` for single-command deployment
- Added `gunicorn.conf.py` for production serving
- Added `/api/health` endpoint

### CI/CD
- Added `.github/workflows/ci.yml` — GitHub Actions CI with Python 3.10/3.11/3.12 matrix
- Fixed `tests/conftest.py` schema mismatch (`"profiles"` → `"llm_profiles"`)
- Added `tests/test_parsing.py` — JSON parsing unit tests
- Added `tests/test_easter_eggs.py` — easter egg detection unit tests

### Dependencies
- Added `gunicorn` and `pytest` to `requirements.txt`

## v1.0.0 (2026-05)

Initial release:
- AI-powered workplace personality test with 16 archetypes + 5 easter egg types
- 4 LLM vendor support (Doubao, DeepSeek, LM Studio, LongCat)
- SSE streaming with preload pipeline
- Procedural SVG avatar generator (660 lines, zero assets)
- Dark/light theme with auto-detection
- Admin configuration panel
