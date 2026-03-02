# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server (http://localhost:5000)
python app.py
```

There are no tests or linter configured for this project.

## Architecture

Single-file Flask backend ([app.py](app.py)) with a static frontend ([templates/index.html](templates/index.html), [static/style.css](static/style.css)).

**Request flow:**
1. Browser loads `GET /` → Flask renders `templates/index.html`
2. User types text and clicks **Translate** → JS `fetch` sends `POST /api/translate` with `{ "text": "..." }`
3. `app.py` calls OpenAI `gpt-4.1-nano` with a fixed `SYSTEM_PROMPT` that auto-detects Hebrew/English and returns only the translation
4. Response `{ "translation": "..." }` or `{ "error": "<Hebrew message>" }` is written into the output textarea or error span

**Error handling:** `ERROR_MESSAGES` dict in `app.py` maps OpenAI HTTP status codes (401, 429) to user-facing Hebrew strings. Any unmapped status or unexpected exception falls back to `GENERIC_SERVER_ERROR`. All error messages are in Hebrew.

**API key:** Loaded from `.env` via `python-dotenv` as `OPENAI_API_KEY`. The OpenAI client is initialized once at module level.
