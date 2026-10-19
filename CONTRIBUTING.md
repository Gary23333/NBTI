# Contributing to NBTI

Thanks for your interest in contributing to NBTI! Here's how to get started.

## Development Setup

```bash
# Clone
git clone https://github.com/Gary23333/NBTI.git
cd NBTI

# Install dependencies
pip install -r requirements.txt

# Copy config template
cp data/config.json.example data/config.json
# Edit data/config.json with your API keys

# Start servers
python server.py          # Backend (port 8081)
python frontend_server.py # Frontend (port 8080)

# Run tests
pytest tests/ -v
```

## Project Structure

```
nbti/                  # Backend package
  providers.py         # Model vendor registry (Provider adapters)
  http_client.py       # Shared httpx connection-pool client
  cache.py             # In-process TTL cache
  storage.py           # Storage backends (FileStorage / RedisStorage)
  conversation.py      # Conversation store facade over the storage backend
  prompts.py           # LLM prompt presets
  config.py            # Configuration management
  llm.py               # LLM client & streaming (delegates vendor specifics to providers.py)
  utils.py             # JSON parsing, normalization
  app.py               # Flask app & API routes
js/                    # Frontend ES Modules (state/util/api/render/stream/preload/session/skeleton/warmup/fastmode/main)
server.py              # Entry point
frontend_server.py     # Static file server + proxy
app.js                 # Thin bootstrap shell for the js/ modules
avatar-generator.js    # SVG avatar generator
style.css              # Styles
index.html             # Main page
config.html            # Admin panel
config.css             # Admin panel styles
```

## How to Add a New Prompt Preset

1. Open `nbti/prompts.py`
2. Add a new entry to the dict returned by `get_prompt_presets()`:
   ```python
   "你的预设名": {
       "prompt_init": "...",
       "prompt_assess": "...",
       "prompt_result": "..."
   }
   ```
3. Each prompt needs `{previous_scenes}`, `{min_questions}`, etc. placeholders in `prompt_assess`
4. The result prompt needs `{easter_schrodinger}`, `{easter_hexagon}`, etc. placeholders

## How to Add a New LLM Vendor

Vendors are **registered adapters** — you do **not** need to modify `app.py` or `llm.py`.
The registry lives in `nbti/providers.py`; `llm.py` and the API simply look vendors up by `vendor_id`.

1. In `nbti/providers.py`, define a `Provider` subclass:

   ```python
   class MyVendorProvider(Provider):
       vendor_id = "myvendor"                 # unique id, used in config profiles
       label = "My Vendor"                    # display name for the config dropdown
       supports_streaming = True
       supports_json_schema = False           # True if the API accepts strict json_schema
       supports_thinking = True
       default_base_url = "https://api.myvendor.com/v1"
       default_model = "my-default-model"

       # Only override the methods whose default behavior differs:
       # def chat_completions_url(self, profile): ...         # non-standard endpoint path
       # def build_thinking_params(self, profile): ...        # custom thinking/reasoning params
       # def _enabled_thinking_params(self, effort): ...      # params sent when thinking is enabled
       # def build_response_format(self, profile, phase): ... # JSON schema / json_object handling
   ```

2. Register it so it becomes available everywhere:

   ```python
   # in nbti/providers.py, alongside the built-in registrations
   register_provider(MyVendorProvider())
   ```

   Registered vendors are exposed automatically via `GET /api/providers` (the config panel
   renders its vendor dropdown from this list), so **no `config.html` edits are required**.

3. Users then set `"vendor": "myvendor"` in any LLM profile. Unknown or missing vendor ids
   fall back to the generic `openai_compatible` adapter.

4. Add a test in `tests/test_providers.py` asserting the new adapter's URL / thinking /
   `response_format` behavior.

## How to Add a New Personality Type

1. In `nbti/prompts.py`: Add the new type to the "16种人格速查" section in all 3 prompt templates (× 3 presets = 9 places)
2. In `avatar-generator.js`: Add a new theme config with colors and accessories
3. In `docs/avatars/`: Generate a sample SVG for the README

## Running Tests

```bash
# Unit tests only (no server needed)
pytest tests/test_config.py tests/test_normalize.py tests/test_parsing.py tests/test_easter_eggs.py tests/test_commit_history.py -v

# Engineering / infrastructure tests (no server needed)
pytest tests/test_providers.py tests/test_cache.py tests/test_storage_backends.py tests/test_compat.py -v

# Integration tests (need mocked LLM)
pytest tests/test_api_integration.py tests/test_stream_contract.py tests/test_preload_batch.py -v

# All tests
pytest tests/ -v
```

## Code Style

- Python: Follow PEP 8, use type hints where helpful
- JavaScript: Vanilla JS, no framework dependencies
- CSS: Use CSS custom properties (variables) for theming
- Commit messages: Use conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`)
