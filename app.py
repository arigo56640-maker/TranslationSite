import os
from flask import Flask, request, jsonify, render_template
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


@app.route("/")
def index():
    return render_template("index.html")


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
