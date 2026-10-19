# Changelog

## v5.0.0 - 工程化 / 全栈升级 (2026-10-20)

### 🎊 重大更新 (MAJOR)

- **可扩展模型供应商注册表** (`nbti/providers.py`)
  - 将原先散落在 `nbti/llm.py` 中按 vendor 硬编码的分支逻辑，抽象为统一的 `Provider` 适配协议 + 注册表
  - 内置 5 个适配器：`openai_compatible`（通用兜底）/ `doubao` / `deepseek` / `lmstudio` / `longcat`；未知或缺失 vendor 一律回退 `openai_compatible`
  - 新增供应商只需实现 `Provider` 子类并 `register_provider()`，**无需改动 `app.py` / `llm.py`**
  - `llm.py` 的 `build_thinking_params` / `get_chat_completions_url` / `build_response_format` 改为薄封装委托注册表，对外行为逐字保持
  - lmstudio `/v1` 追加、longcat `/openai/v1/chat/completions`、deepseek `json_object`、doubao/longcat 返回 `{}`、lmstudio/openai_compatible 严格 `json_schema` 等差异全部收敛到适配器

- **共享 httpx 连接池** (`nbti/http_client.py`)
  - 模块级单例客户端 + keep-alive 连接复用与连接上限，削减单次 LLM 调用延迟
  - `post()` 保持与 `requests.post` 兼容签名；流式返回 requests 风格包装对象（`iter_lines`/`text`/`encoding`）
  - 装了 `h2` 时自动启用 HTTP/2，否则降级 HTTP/1.1（不报错）

- **并行预载 + 首题预热** (`nbti/app.py`)
  - 🆕 `POST /api/chat/preload/batch`：用线程池**并行**为每个答题分支生成草稿并逐分支落库，单分支失败隔离不影响其它分支
  - 🆕 `POST /api/chat/warmup`：预生成第一题并以键 `开始测试` 存入预载草稿；随后 `/api/chat` 命中草稿直接提交，跳过重新生成

- **缓存与存储解耦** (`nbti/cache.py` + `nbti/storage.py` + `nbti/conversation.py`)
  - 🆕 进程内 TTL 缓存：prompt 构建 + 会话读缓存复用，可由 `cache_enabled` 配置驱动开关（关闭时 get 恒未命中、set 空操作）
  - 🆕 存储后端抽象 `StorageBackend`：`FileStorage`（文件 JSON，与旧实现行为等价，附读缓存 + 写时失效）与可选 `RedisStorage`（WATCH/MULTI 乐观并发，支持多 worker）
  - 🆕 `create_store` 工厂按环境变量/配置解析后端；redis 未安装/不可达时**安全回退**文件后端，绝不抛错
  - `conversation.py` 变为存储门面，对外 API 完全不变

- **前端 ES Module 模块化** (`js/`)
  - 前端拆分为 11 个原生 ES Module（state / util / api / render / stream / preload / session / skeleton / warmup / fastmode / main）
  - `index.html` 改用 `type="module"`；`app.js` 退化为薄壳引导；`sw.js` 缓存名升级 `nbti-v3`

- **UX/UI 刷新**
  - 骨架屏加载态、首题预热即时反馈、`fast_mode` 前端开关、并行预载状态提示

### 🚀 功能增强

- `GET /api/providers` — 返回注册表供应商元数据（供配置面板渲染下拉，不含任何密钥）
- `/api/health` 新增可观测字段：`version` / `storage_backend` / `cache_enabled` / `fast_mode` / `providers_count`
- 新增配置键：`cache_enabled` / `storage_backend` / `redis_url` / `fast_mode` / `phase_max_tokens`
- `fast_mode`：assess/init 阶段关闭 thinking 并收敛 `max_tokens` 到 `phase_max_tokens` 阶段上限（默认关闭，不改变既有行为，绝不修改 profile）
- 旧格式 `config.json`（`model_init/assess/result`）自动迁移；`llm_profiles` 未知 vendor 经 `normalize_vendor` 规范化；`load_config` 补齐新键且不破坏既有键

### 📦 依赖与部署

- `requirements.txt`：`redis` 明确为**可选**依赖（仅当 `storage_backend=redis` 时需要），不作为强制安装项
- `gunicorn.conf.py`：新增 `NBTI_WORKERS` 环境变量覆盖（默认 1），并文档化「workers>1 需先启用 Redis 存储后端（`NBTI_STORAGE_BACKEND=redis`），否则文件后端会因多进程竞争丢数据」
- `Dockerfile` / `docker-compose.yml`：补充并透传 `NBTI_STORAGE_BACKEND` / `NBTI_REDIS_URL` / `NBTI_ADMIN_TOKEN` / `NBTI_WORKERS` 说明；健康检查与默认单机行为不变

### 🧪 测试

- 测试用例总数 442 → 526
- 🆕 `tests/test_providers.py` — 供应商适配器 URL / thinking / `response_format` 断言 + 注册表注册/查找/元数据行为
- 🆕 `tests/test_cache.py` — TTL 命中/过期、开关关闭直算、set/invalidate/clear、并发写读线程安全
- 🆕 `tests/test_storage_backends.py` — `FileStorage` 行为 + `RedisStorage`（内存假 client 注入）与文件后端**行为等价** + `create_store` 安全回退
- 🆕 `tests/test_stream_contract.py` — SSE 事件序列（`first_token` / `chunk` / `done`）字段契约 + 残缺答案不入库 / 完整答案入库
- 🆕 `tests/test_compat.py` — 旧格式 config.json 迁移 + 未知 vendor 规范化 + `load_config` 补齐新键且不破坏既有键
- CI：`node --check` 步骤覆盖 `js/*.js` 全部模块（`for f in js/*.js; do node --check "$f"; done`）

---

## v4.0.0 - 全民升级版 (2026-07-28)

### 🎊 重大更新 (MAJOR)

- **9大测试主题全量开放** (`nbti/themes.py`)
  - 💼 **职场人格** — 经典16种职场角色（核心主题，完整支持）
  - 🐾 **动物系人格** — 16种动物人格，12种专属手绘动物头像（核心主题）
  - 🎨 **色彩人格** — 色彩心理学主题，8种光影特效头像（核心主题）
  - 💕 **恋爱人格** — 你的爱情模式是什么？（完整开放）
  - 👥 **社交人格** — 社牛还是社恐？一测便知（完整开放）
  - 🧠 **官方MBTI** — 经典16型心理学视角（完整开放）
  - 🤯 **脑洞人格** — 你的脑回路有多清奇？（完整开放）
  - 🆕 💰 **搞钱人格** — 梗向热门新主题，测测你的搞钱体质
  - 🆕 🔋 **精神状态检测** — 梗向热门新主题，当代人精神状态大起底
  - v3.0 的 4 个半成品主题全部补全，"敬请期待"成为历史
  - 每个主题独立维度定义、16种人格类型、5种彩蛋人格、专属配色与出题场景

- **动态 Prompt 系统** (`nbti/prompts.py`)
  - 删除硬编码人格速查表，判定规则/分数规则/场景方向全部按主题动态注入
  - 7 种吐槽风格 × 9 大主题 = **63 种玩法**（v3.0 为 49 种）
  - 修复 mbti 主题输出错误代号格式的问题

- **137 种程序化头像组合** (`avatar-generator.js`)
  - 🆕 新增 `THEME_AVATAR_PROFILES`：6 个新主题专属配色/发色/配饰/特效映射
  - 主题专属特效：love=glow、social=barrage、brainhol=glitch、money=golden 等
  - 彩蛋特效全主题通用
  - 头像组合从 41 扩到 **137**（16职场 + 12动物 + 8色彩 + 6新主题×16 + 5彩蛋），每次刷新仍是全新面孔，零图片素材

### 🚀 功能增强

- **主题选择页焕新** — 核心/热门分组展示，热门主题带 NEW 角标与主题色卡片，"敬请期待"占位全部移除
- **海报全主题适配** (`share-poster.js`) — 分享海报/合盘海报支持 9 主题配色
- **雷达图全主题适配** (`radar-chart.js`) — 四维雷达图配色联动全部 9 主题
- **合盘全主题适配** (`compat-data.js`) — CP 合盘规则覆盖 9 主题，跨主题 CP 计算照常可用

### 🐛 BUG修复

- 修复 `theme_id` 传入不可哈希值导致 500 的问题
- 修复请求体非 JSON 导致 500 的问题
- 修复会话缺少 profile 导致 500 的问题
- 修复限流器内存泄漏
- 修复会话文件包含非法 UTF-8 导致 500 的问题
- 修复"开始测试"按钮连点触发并发请求的问题

### 🧪 测试

- 测试用例总数 108 → **430**
- 🆕 `tests/test_themes.py` — 275 条 9 主题全量测试
- 🆕 `tests/test_bugfixes.py` — 本次 6 项 BUG 修复回归测试
- 🆕 `tests/test_theme_api.py` — 24 条主题 API 测试

---

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
