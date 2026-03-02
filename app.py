import os
import subprocess
from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI, APIStatusError
from dotenv import load_dotenv
import pymysql

load_dotenv()

MYSQL_URL = os.getenv("MYSQL_URL")

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


def _parse_mysql_url(url):
    p = urlparse(url)
    return {
        "host": p.hostname,
        "port": p.port or 3306,
        "user": p.username,
        "password": p.password,
        "db": p.path.lstrip("/"),
        "charset": "utf8mb4",
    }

def _init_db():
    if not MYSQL_URL:
        print("MYSQL_URL not set — translation logging disabled.")
        return
    try:
        conn = pymysql.connect(**_parse_mysql_url(MYSQL_URL), autocommit=True)
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS translations (
                    id          INT      AUTO_INCREMENT PRIMARY KEY,
                    source_text TEXT     NOT NULL,
                    translation TEXT     NOT NULL,
                    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.close()
        print("DB ready: translations table verified.")
    except Exception as exc:
        print(f"DB init failed (logging will be skipped): {exc}")

_init_db()

def _log_translation(source_text, translation):
    if not MYSQL_URL:
        return
    try:
        conn = pymysql.connect(**_parse_mysql_url(MYSQL_URL), autocommit=True)
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO translations (source_text, translation) VALUES (%s, %s)",
                (source_text, translation),
            )
        conn.close()
    except Exception as exc:
        print(f"DB log failed: {exc}")


@app.route("/")
def index():
    return send_from_directory(app.root_path, "index.html")


@app.route("/api/last-modified")
def last_modified():
    return jsonify({"last_modified": LAST_MODIFIED})


@app.route("/api/history")
def history():
    if not MYSQL_URL:
        return jsonify([])
    try:
        conn = pymysql.connect(**_parse_mysql_url(MYSQL_URL), autocommit=True)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT source_text, translation, created_at "
                "FROM translations ORDER BY created_at DESC LIMIT 200"
            )
            rows = cur.fetchall()
        conn.close()
        return jsonify([
            {
                "source_text": r[0],
                "translation": r[1],
                "created_at": r[2].strftime("%Y-%m-%d %H:%M"),
            }
            for r in rows
        ])
    except Exception as exc:
        print(f"DB history fetch failed: {exc}")
        return jsonify({"error": "שגיאה בטעינת ההיסטוריה."}), 500


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
        _log_translation(text, translation)
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
