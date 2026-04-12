# Spell Bee Voice Bot

A small **voice spelling game** built with [Pipecat](https://github.com/pipecat-ai/pipecat): the browser sends audio over **WebRTC**, **Deepgram** transcribes speech, **Google Gemini** **grades** each spelling attempt from the transcript, and **Cartesia** speaks the prompts.

Spelling is judged **only** by Gemini (no rule-based path). Helpers in `spelling_normalization.py` format letter-by-letter TTS only.

## Prerequisites

- **Python 3.10+**
- API keys for:
  - [Deepgram](https://deepgram.com/) (speech-to-text)
  - [Cartesia](https://cartesia.ai/) (text-to-speech)
  - [Google Gemini](https://aistudio.google.com/apikey) (spelling evaluation; free tier available)
- A **desktop browser** (Chrome, Firefox, or Safari) with microphone access.  
  IDE embedded previews often do not support `getUserMedia`; open the app at `http://127.0.0.1:<port>` in a normal browser.

## Setup

### 1. Go to this package directory

```bash
cd src/LLD/spellbee_voice_bot
```

(Adjust the path if your clone layout differs.)

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp env.example .env
```

Edit `.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPGRAM_API_KEY` | Yes | Deepgram API key |
| `CARTESIA_API_KEY` | Yes | Cartesia API key |
| `GEMINI_API_KEY` | Yes | [Google AI Studio](https://aistudio.google.com/apikey) |
| `GEMINI_MODEL` | No | Override model (default: `gemini-2.5-flash`; see [models](https://ai.google.dev/gemini-api/docs/models/gemini)) |

The server loads `.env` from the **current working directory** when you run `python server.py`. **Run the server from this package directory** (the folder that contains `server.py`) so imports like `spellbee_processor` resolve and `.env` is found.

**Grading:** Each finished utterance triggers **one** `generateContent` call (no HTTP retries, to avoid extra quota use). The model returns JSON (`correct`, `normalized_spelling`, `empty_attempt`). If the call fails (including **429** rate limit), the player is asked to **try the same word again**.

**404 on Gemini:** The request URL includes the model id (e.g. `.../models/gemini-2.5-flash:generateContent`). **404 means that model name is not available** for your key (often because an old id like `gemini-1.5-flash` was retired). Fix: use a current id from the [model list](https://ai.google.dev/gemini-api/docs/models/gemini), or clear `GEMINI_MODEL` so the default applies.

## Run the server

```bash
python server.py
```

Defaults: **Host** `0.0.0.0`, **Port** `8080`.

```bash
python server.py --host 127.0.0.1 --port 8080
```

Open **http://127.0.0.1:8080** in your browser → **Start session** → allow microphone. The home page serves `static/index.html` when present; otherwise you are redirected to Pipecat’s prebuilt client at **`/client/`**.

## How to play

1. Listen to the word.
2. Spell it **letter by letter** (English letter names).
3. Pause for about **two seconds** when you are done so the app can finalize your speech.

Words are listed in `words.py`; flow is in `spellbee_processor.py`.

## Project layout

| Path | Role |
|------|------|
| `server.py` | FastAPI, WebRTC, Pipecat pipeline, validates keys; Cartesia **voice id** defaults in code (`_DEFAULT_CARTESIA_VOICE_IN`), not via `.env` |
| `spellbee_processor.py` | Session state, STT merge, Gemini grading, TTS prompts |
| `llm_spelling.py` | Gemini `generateContent` HTTP call |
| `spelling_normalization.py` | `tts_letter_by_letter` only (TTS formatting) |
| `words.py` | Word list |
| `static/index.html` | Web UI + WebRTC client |
| `env.example` | Env template |

## Troubleshooting

- **`GEMINI_API_KEY is required`** — Add your key from AI Studio.
- **`Missing required environment variables`** — Deepgram / Cartesia keys.
- **Microphone / WebRTC** — Use a real browser at `http://127.0.0.1:<port>`, not `file://`.
- **NLTK** — Server sets `NLTK_DATA` to `.nltk_data` under this package unless you override it.
