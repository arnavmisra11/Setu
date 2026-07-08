import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")
BASE_URL = "https://api.sarvam.ai"

app = Flask(__name__, static_folder="public", static_url_path="")

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

LANG_CODES = {"en": "en-IN", "hi": "hi-IN", "kn": "kn-IN"}
ALL_LANGS = ["en", "hi", "kn"]


def auth_headers(extra=None):
    headers = {"api-subscription-key": API_KEY}
    if extra:
        headers.update(extra)
    return headers


def speech_to_text(file_bytes, filename, mimetype):
    files = {"file": (filename, file_bytes, mimetype)}
    data = {"model": "saaras:v3", "mode": "transcribe", "language_code": "unknown"}
    res = requests.post(f"{BASE_URL}/speech-to-text", headers=auth_headers(), files=files, data=data)
    if not res.ok:
        raise RuntimeError(f"speech-to-text failed ({res.status_code}): {res.text}")
    body = res.json()
    detected_lang = (body.get("language_code") or "").split("-")[0]
    return body.get("transcript"), detected_lang


def translate_text(text, source_lang_code, target_lang_code):
    res = requests.post(
        f"{BASE_URL}/translate",
        headers=auth_headers({"Content-Type": "application/json"}),
        json={
            "input": text,
            "source_language_code": source_lang_code,
            "target_language_code": target_lang_code,
            "model": "mayura:v1",
        },
    )
    if not res.ok:
        raise RuntimeError(f"translate failed ({res.status_code}): {res.text}")
    return res.json().get("translated_text")


def text_to_speech(text, target_lang_code):
    res = requests.post(
        f"{BASE_URL}/text-to-speech",
        headers=auth_headers({"Content-Type": "application/json"}),
        json={
            "text": text,
            "target_language_code": target_lang_code,
            "model": "bulbul:v3",
            "speaker": "shubh",
            "speech_sample_rate": 22050,
        },
    )
    if not res.ok:
        raise RuntimeError(f"text-to-speech failed ({res.status_code}): {res.text}")
    return res.json()["audios"][0]


def targets_for(source_lang):
    if source_lang not in ALL_LANGS:
        return None
    return [lang for lang in ALL_LANGS if lang != source_lang]


def build_translations(source_text, source_lang):
    targets = targets_for(source_lang)
    if not targets:
        raise ValueError(f'Unsupported source language "{source_lang}"')

    source_lang_code = LANG_CODES[source_lang]
    results = {}
    for target in targets:
        target_lang_code = LANG_CODES[target]
        translated = translate_text(source_text, source_lang_code, target_lang_code)
        audio = text_to_speech(translated, target_lang_code)
        results[target] = {"text": translated, "audioBase64": audio}
    return results


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/health")
def health():
    return jsonify({"ok": True})


@app.route("/api/translate-text", methods=["POST"])
@limiter.limit("12 per minute")
def translate_text_route():
    body = request.get_json(silent=True) or {}
    text = body.get("text")
    source_lang = body.get("sourceLang")
    if not text or not source_lang:
        return jsonify({"error": "text and sourceLang are required"}), 400
    try:
        translations = build_translations(text, source_lang)
        return jsonify({"source": {"lang": source_lang, "text": text}, "translations": translations})
    except Exception as err:
        print(err)
        return jsonify({"error": str(err)}), 500


@app.route("/api/translate-audio", methods=["POST"])
@limiter.limit("12 per minute")
def translate_audio_route():
    if "audio" not in request.files:
        return jsonify({"error": "audio file is required"}), 400
    audio_file = request.files["audio"]
    try:
        transcript, detected_lang = speech_to_text(
            audio_file.read(), audio_file.filename or "audio.webm", audio_file.mimetype
        )
        if not transcript:
            return jsonify({"error": "Could not transcribe audio. Please try again."}), 422
        if not targets_for(detected_lang):
            return jsonify({"error": f'Detected language "{detected_lang}" is not supported'}), 422

        translations = build_translations(transcript, detected_lang)
        return jsonify({"source": {"lang": detected_lang, "text": transcript}, "translations": translations})
    except Exception as err:
        print(err)
        return jsonify({"error": str(err)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=False)
