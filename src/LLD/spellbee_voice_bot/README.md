# Spell Bee Voice Bot

A small **voice spelling game** built with [Pipecat](https://github.com/pipecat-ai/pipecat): the browser sends audio over **WebRTC**, **Deepgram** transcribes speech, a Python **game processor** checks spelling, and **Cartesia** speaks the prompts.

## Prerequisites

- **Python 3.10+**
- Accounts / API keys for:
  - [Deepgram](https://deepgram.com/) (speech-to-text)
  - [Cartesia](https://cartesia.ai/) (text-to-speech)
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

Edit `.env` and set:

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPGRAM_API_KEY` | Yes | Deepgram API key |
| `CARTESIA_API_KEY` | Yes | Cartesia API key |

The server loads `.env` from the **current working directory** when you run `python server.py`, so run the server from this folder (or ensure `.env` is discoverable by your process).

## Run the server

```bash
python server.py
```

Defaults:

- **Host:** `0.0.0.0`
- **Port:** `8080`

Override if needed:

```bash
python server.py --host 127.0.0.1 --port 8080
```

Then open **http://127.0.0.1:8080** in your browser, click **Start session**, and allow microphone access.

## How to play

1. Listen to the word.
2. Spell it **letter by letter** (English letter names).
3. Pause for about **two seconds** when you are done so the app can finalize your speech.

Word list and behavior are defined in `words.py` and `spellbee_processor.py`.

## Project layout

| Path | Role |
|------|------|
| `server.py` | FastAPI app, WebRTC `/api/offer`, game state API, Pipecat pipeline |
| `spellbee_processor.py` | Session state, STT handling, scoring, TTS prompts |
| `spelling_normalization.py` | Map spoken letter names to A–Z |
| `words.py` | Words for the game |
| `static/index.html` | Web UI and WebRTC client |
| `env.example` | Template for `.env` (no secrets) |

## Troubleshooting

- **`Missing required environment variables`** — Set `DEEPGRAM_API_KEY` and `CARTESIA_API_KEY` in `.env` and run from the directory that contains `.env`.
- **Microphone / WebRTC errors** — Use a real browser at `http://127.0.0.1:<port>`, not `file://`, and ensure the server is running.
- **NLTK data** — The server sets `NLTK_DATA` to a local `.nltk_data` folder under this package; no extra step unless you override `NLTK_DATA` yourself.
