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
  prompts.py           # LLM prompt presets (3 personas)
  config.py            # Configuration management
  conversation.py      # Conversation storage
  llm.py               # LLM client & streaming
  utils.py             # JSON parsing, normalization
  app.py               # Flask app & API routes
server.py              # Entry point
frontend_server.py     # Static file server + proxy
app.js                 # Frontend logic
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

1. In `nbti/llm.py`:
   - Add vendor-specific logic in `build_thinking_params()` if the vendor has unique thinking/reasoning params
   - Add URL construction in `get_chat_completions_url()` if the vendor uses a non-standard endpoint path
   - Add response format handling in `build_response_format()` if the vendor supports JSON schema

2. In `config.html`:
   - Add the vendor to the `<select>` dropdown in `renderProfiles()`
   - Add default values in `VENDOR_DEFAULTS`

## How to Add a New Personality Type

1. In `nbti/prompts.py`: Add the new type to the "16种人格速查" section in all 3 prompt templates (× 3 presets = 9 places)
2. In `avatar-generator.js`: Add a new theme config with colors and accessories
3. In `docs/avatars/`: Generate a sample SVG for the README

## Running Tests

```bash
# Unit tests only (no server needed)
pytest tests/test_config.py tests/test_normalize.py tests/test_parsing.py tests/test_easter_eggs.py tests/test_commit_history.py -v

# Integration tests (need mocked LLM)
pytest tests/test_api_integration.py -v

# All tests
pytest tests/ -v
```

## Code Style

- Python: Follow PEP 8, use type hints where helpful
- JavaScript: Vanilla JS, no framework dependencies
- CSS: Use CSS custom properties (variables) for theming
- Commit messages: Use conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`)
