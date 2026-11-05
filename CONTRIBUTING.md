# Contributing to NBTI

Thanks for your interest in contributing to NBTI! Here's how to get started.

## Development Setup

```bash
# Clone
git clone https://github.com/Gary23333/NBTI.git
cd NBTI

# Install dependencies (Python 3.10+ and Node.js 20+)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Copy config template
cp data/config.json.example data/config.json
# Edit data/config.json with your API keys

# Start servers
python server.py          # Backend (port 8081)
python frontend_server.py # Frontend (port 8080)

# Run tests
python -m pytest -v
```

## Project Structure

```
nbti/                  # Backend package
  prompts.py           # Dynamic prompts and 7 personas
  themes.py            # 9 themes, dimensions and personality definitions
  config.py            # Configuration management
  conversation.py      # Conversation storage
  llm.py               # LLM client & streaming
  utils.py             # JSON parsing, normalization
  app.py               # Flask app & API routes
  limits.py            # Shared request-body limit
server.py              # Entry point
frontend_server.py     # Static file server + proxy
app.js                 # Frontend logic
avatar-generator.js    # SVG avatar generator
style.css              # Styles
index.html             # Main page
config.html            # Admin panel
config.css             # Admin panel styles
scripts/healthcheck.py  # Frontend + backend readiness probe
start.sh               # Production Gunicorn process supervisor
requirements-dev.txt   # Development/test dependencies
pytest.ini             # Offline test defaults
```

## How to Add a New Prompt Preset

1. Open `nbti/prompts.py`
2. Register the style in `BASE_STYLES` or `NEW_STYLES` and add its persona and scene rules to the matching builders.
3. Preserve the shared question, option, score and result constraints. `get_prompt()` combines the selected theme with the selected style; `get_prompt_presets()` exposes compatible presets.
4. Extend `tests/test_themes.py` and `tests/test_theme_api.py` for any new theme/style combinations.

## How to Add a New LLM Vendor

1. In `nbti/llm.py`:
   - Add vendor-specific logic in `build_thinking_params()` if the vendor has unique thinking/reasoning params
   - Add URL construction in `get_chat_completions_url()` if the vendor uses a non-standard endpoint path
   - Add response format handling in `build_response_format()` if the vendor supports JSON schema

2. In `config.html`:
   - Add the vendor to the `<select>` dropdown in `renderProfiles()`
   - Add default values in `VENDOR_DEFAULTS`

## How to Add a New Personality Type

1. In `nbti/themes.py`: Update the relevant theme's `personality_types`; prompt quick-reference lists are generated from these definitions.
2. In `avatar-generator.js`: Add a new theme config with colors and accessories
3. In `docs/avatars/`: Generate a sample SVG for the README

## Running Tests

```bash
# Default offline suite (no running server or API key needed)
python -m pytest -q

# Focused integration tests (LLM responses are mocked by the tests)
python -m pytest tests/test_api_integration.py -v

# Deployment and configuration regressions
python -m pytest tests/test_deployment.py tests/test_config_loading.py tests/test_request_safety.py -v
```

`pytest.ini` excludes `tests/e2e/`, `test_deepseek.py`, `test_preload.py` and `test_longcat_presets.py`. These are manual scripts that need running services, Playwright or real model access. Run them explicitly with Python only in an isolated test setup after reviewing their configuration changes and potential API costs. They are not part of the offline pass.

CI runs the offline suite on Python 3.10, 3.11 and 3.12, checks JavaScript syntax, builds the Docker image, verifies private files stay out of the build, and exercises production startup and the proxied health endpoint. For a local container check:

```bash
docker compose config --quiet
docker build -t nbti:local .
# Set a real NBTI_ADMIN_TOKEN in .env before starting Compose.
docker compose up -d
docker compose ps
docker compose logs
```

Production uses one backend worker because the JSON stores and rate limiter are process-local. Do not enable Gunicorn preloading: the cleanup thread must start inside the worker. `start.sh` requires an admin token, forwards shutdown signals, and stops both services when either exits. Keep new public assets in `frontend_server.PUBLIC_FILES` and add new runtime files explicitly to `.dockerignore`.

## Code Style

- Python: Follow PEP 8, use type hints where helpful
- JavaScript: Vanilla JS, no framework dependencies
- CSS: Use CSS custom properties (variables) for theming
- Commit messages: Use conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`)

