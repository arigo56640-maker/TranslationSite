# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server (http://localhost:5000)
python app.py
```

No tests or linter are configured.

## Architecture

Single-file Flask backend ([app.py](app.py)) serving both the frontend and the API. The frontend is [index.html](index.html) (project root) + [static/style.css](static/style.css).

**Routes:**
- `GET /` — serves `index.html` via `send_from_directory`
- `POST /api/translate` — accepts `{ "text": "..." }`, calls OpenAI, returns `{ "translation": "..." }` or `{ "error": "<Hebrew string>" }`
- `GET /api/last-modified` — returns `{ "last_modified": "YYYY-MM-DD HH:MM" }` from the last git commit (computed once at startup)

**Key details:**
- Model: `gpt-4.1-nano` with a fixed `SYSTEM_PROMPT` that auto-detects Hebrew/English and returns translation only
- Error messages are always in Hebrew. `ERROR_MESSAGES` dict maps status codes 401/429; everything else falls back to `GENERIC_SERVER_ERROR`
- `OPENAI_API_KEY` loaded from `.env` via `python-dotenv`; OpenAI client initialized once at module level
- `LAST_MODIFIED` computed at startup via `subprocess` calling `git log`; falls back to `datetime.now()` if git is unavailable

## Deployment

Hosted on Railway. `Procfile` starts the app with `gunicorn app:app`. Set `OPENAI_API_KEY` as an environment variable in the Railway dashboard — no `.env` file needed in production.
