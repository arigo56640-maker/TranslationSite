# Arie Translator

A minimalist web application for bidirectional translation between Hebrew and English, powered by OpenAI's `gpt-4.1-nano` model.

## Features

- Automatic language detection — paste Hebrew or English and it translates to the other
- Clean, minimal UI
- Hebrew error messages for API failures
- Footer shows the date and time of the last code update

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript (Fetch API)
- **AI:** OpenAI API (`gpt-4.1-nano`)
- **Hosting:** Railway

## Local Setup

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Run the server:
   ```bash
   python app.py
   ```

4. Open `http://localhost:5000` in your browser.

## Deployment (Railway)

1. Connect this GitHub repo to [Railway](https://railway.app)
2. Add `OPENAI_API_KEY` as an environment variable in the Railway dashboard
3. Railway uses the `Procfile` to start the app: `gunicorn app:app`
