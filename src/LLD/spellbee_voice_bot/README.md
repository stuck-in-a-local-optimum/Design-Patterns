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
| `GEMINI_MODEL` | No | Override model (default: `gemini-1.5-flash`) |

The server loads `.env` from the **current working directory** when you run `python server.py`.

**Grading:** Each finished utterance is sent to Gemini with the **target word** and **STT transcript**; the model returns JSON (`correct`, `normalized_spelling`, `empty_attempt`). If the API call **fails**, the player is asked to **try the same word again** (no score change).

## Run the server

```bash
python server.py
```

Defaults: **Host** `0.0.0.0`, **Port** `8080`.

```bash
python server.py --host 127.0.0.1 --port 8080
```

Open **http://127.0.0.1:8080** in your browser → **Start session** → allow microphone.

## How to play

1. Listen to the word.
2. Spell it **letter by letter** (English letter names).
3. Pause for about **two seconds** when you are done so the app can finalize your speech.

Words are listed in `words.py`; flow is in `spellbee_processor.py`.

## Project layout

| Path | Role |
|------|------|
| `server.py` | FastAPI, WebRTC, Pipecat pipeline, validates `GEMINI_API_KEY` |
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
