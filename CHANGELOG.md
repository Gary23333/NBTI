# Changelog

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
