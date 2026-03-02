import os
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI, APIStatusError
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "You are a highly accurate, professional translator. "
    "Your task is to seamlessly translate text between Hebrew and English.\n"
    "- If the user provides text in Hebrew, translate it to English.\n"
    "- If the user provides text in English, translate it to Hebrew.\n"
    "IMPORTANT: Return ONLY the translated text. Do not include any greetings, "
    "explanations, markdown formatting, or conversational filler."
)

ERROR_MESSAGES = {
    401: "שגיאה בחיבור למערכת. מפתח ה-API אינו תקין.",
    429: "חרגת ממכסת השימוש או מהתקציב של OpenAI. אנא נסה שוב מאוחר יותר.",
}
GENERIC_SERVER_ERROR = "אירעה שגיאת שרת כללית, אנא נסה שוב."

def _get_last_modified():
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=format:%Y-%m-%d %H:%M"],
            capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))
        )
        ts = result.stdout.strip()
        if ts:
            return ts
    except Exception:
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M")

LAST_MODIFIED = _get_last_modified()


@app.route("/")
def index():
    return send_from_directory(app.root_path, "index.html")


@app.route("/api/last-modified")
def last_modified():
    return jsonify({"last_modified": LAST_MODIFIED})


@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "אנא הזן טקסט לתרגום."}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
        )
        translation = response.choices[0].message.content.strip()
        return jsonify({"translation": translation})

    except APIStatusError as e:
        status = e.status_code
        message = ERROR_MESSAGES.get(status)
        if message is None:
            message = GENERIC_SERVER_ERROR
        return jsonify({"error": message}), status

    except Exception:
        return jsonify({"error": GENERIC_SERVER_ERROR}), 500


if __name__ == "__main__":
    app.run(debug=True)
