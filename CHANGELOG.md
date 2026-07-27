# Changelog

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
