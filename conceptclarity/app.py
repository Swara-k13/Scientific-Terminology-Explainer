from flask import Flask, render_template, request, jsonify
from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

#  API key from .env
client = Groq(
    api_key="YOUR_KEY_HERE"
)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- EXPLAIN ----------------
@app.route("/explain", methods=["POST"])
def explain():
    data = request.get_json()

    term = data.get("term")
    lang = data.get("lang", "en")

    if not term:
        return jsonify({"error": "No term provided"}), 400

    lang_map = {
        "en": "English",
        "hi": "Hindi (Devanagari script)",
        "mr": "Marathi (Devanagari script)",
        "ta": "Tamil",
        "fr": "French",
        "de": "German",
        "es": "Spanish",
        "ja": "Japanese",
        "zh": "Chinese",
        "ar": "Arabic",
        "ru": "Russian",
        "ko": "Korean"
    }

    language_name = lang_map.get(lang, "English")

    prompt = f"""
Explain the scientific term '{term}' clearly in 4-5 sentences.

Give the explanation in {language_name}.
Use proper native script of the language.

Also give one real world example.

Then provide exactly 2 related scientific terms.

Return ONLY JSON:

{{
  "term": "...",
  "explanation": "...",
  "example": "...",
  "related_terms": ["...", "..."]
}}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        response_text = completion.choices[0].message.content

        response_json = json.loads(response_text)

        return jsonify(response_json)

    except json.JSONDecodeError:
        return jsonify({
            "error": "Invalid JSON from model",
            "raw": response_text
        }), 500

    except Exception as e:
        return jsonify({
            "error": "Something went wrong",
            "details": str(e)
        }), 500


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)