# Setu — English ⇄ Hindi ⇄ Kannada voice & text bridge

Speak or type in English, Hindi, or Kannada. Get back translated **text and spoken audio**
in the other language(s):
- English in → Hindi text+audio **and** Kannada text+audio
- Hindi or Kannada in → English text+audio

Built as a website (works on any phone/laptop browser, installable to a home screen via
the manifest — no app store needed). Backend is **Python (Flask)**. Powered by
[Sarvam AI](https://sarvam.ai), which trains specifically on Indian languages and
code-mixed speech.

## 1. Get a Sarvam AI API key

1. Sign up at https://dashboard.sarvam.ai — free credits automatically, no institutional
   registration, just email/Google sign-in.
2. Copy your API subscription key.

## 2. First-time setup (one time only)

**Windows:** double-click `setup.bat`. It creates the Python environment, installs
everything, and opens `.env` in Notepad for you to paste your key into.

**Mac/Linux:** in a terminal, `cd` into this folder and run:
```bash
chmod +x setup.sh start.sh   # only needed once, makes the scripts runnable
./setup.sh
```
Then open the `.env` file it creates and paste your key into `API_KEY=`.

## 3. Running it day-to-day

No more typing commands — just:

- **Windows:** double-click `start.bat`
- **Mac/Linux:** double-click `start.sh`, or run `./start.sh` in a terminal

It starts the server and opens `http://localhost:3000` in your browser automatically.
To stop it, close the terminal/command window that opened, or press `Ctrl+C` in it.

<details>
<summary>Manual method (if you prefer typing commands yourself)</summary>

```bash
python3 -m venv venv          # create an isolated environment for this project
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Then open http://localhost:3000 manually.
</details>

## 4. Deploy it publicly

This is a normal Flask app, so it deploys anywhere that runs Python:

- **Render** (easiest, free tier available): New → Web Service → connect this folder/repo →
  build command `pip install -r requirements.txt`, start command
  `gunicorn -w 2 -b 0.0.0.0:$PORT app:app` → add `API_KEY` under Environment.
  (`gunicorn` is already in requirements.txt — it's a production-grade server; the
  `python app.py` command from step 2 is fine for local testing but not for real traffic.)
- **Railway** / **Fly.io**: similar — push the repo, set `API_KEY`, use the same
  gunicorn start command.

Once deployed, share the URL. Anyone can open it in a browser — no install required.

## 5. Before you make it public — things worth doing

Since this is a public tool for many users, a few things matter more than for a personal
project:

- **Rate limiting is already on** (`app.py`, 12 requests/minute/IP on the two API routes).
  Tune it based on your Sarvam credit budget — each translate+speak round trip costs real
  money once free credits run out (roughly ₹0.02–0.05 per short phrase at current Sarvam
  pricing).
- **Set a spending cap** in the Sarvam dashboard so a traffic spike can't run up a large
  bill unexpectedly.
- **HTTPS**: microphone access only works over HTTPS or localhost — Render/Railway/Fly give
  you HTTPS automatically once deployed.
- **Abuse**: if this gets real traffic, consider adding a lightweight CAPTCHA or login for
  the audio endpoint specifically, since that's the most expensive one to abuse.

## How it works

```
Browser (public/) ──HTTP──> app.py (Flask) ──HTTPS──> Sarvam AI
  records mic audio          keeps your API             /speech-to-text
  or takes typed text        key private,                /translate
                              rate-limits,                /text-to-speech
                              orchestrates the
                              3-step pipeline
```

`app.py` has three Sarvam calls wired up (`speech_to_text`, `translate_text`,
`text_to_speech`) — if Sarvam changes a field name in their API, that's the file to check
against https://docs.sarvam.ai.

## Files

- `app.py` — Flask backend, proxies Sarvam AI, rate-limited
- `public/index.html`, `style.css`, `app.js` — the frontend (unchanged — still plain
  JavaScript, since that's the only language browsers run natively)
- `requirements.txt` — Python dependencies
- `.env.example` — copy to `.env` and add your key (never commit `.env`)
- `setup.bat` / `setup.sh` — one-time setup (Windows / Mac-Linux)
- `start.bat` / `start.sh` — everyday launcher, starts the server and opens your browser
