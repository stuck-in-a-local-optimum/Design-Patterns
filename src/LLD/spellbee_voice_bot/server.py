"""
Spell Bee voice server: FastAPI + Pipecat Small WebRTC pipeline.

Run from this directory:
  pip install -r requirements.txt
  cp env.example .env   # add DEEPGRAM_API_KEY and CARTESIA_API_KEY
  python server.py
"""

from __future__ import annotations

import os

# Pipecat TTS may pull NLTK sentence tokenizers; keep data inside this package.
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
_nltk_dir = os.path.join(_pkg_dir, ".nltk_data")
os.makedirs(_nltk_dir, exist_ok=True)
if not os.environ.get("NLTK_DATA"):
    os.environ["NLTK_DATA"] = _nltk_dir

import argparse
import asyncio
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from loguru import logger
from pipecat_ai_small_webrtc_prebuilt.frontend import SmallWebRTCPrebuiltUI

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.connection import IceServer, SmallWebRTCConnection
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport

from spellbee_processor import GameSessionState, SpellBeeGameProcessor
from words import SPELL_WORDS

load_dotenv(override=True)

pcs_map: Dict[str, SmallWebRTCConnection] = {}
SESSIONS: Dict[str, GameSessionState] = {}

ice_servers = [
    IceServer(
        urls="stun:stun.l.google.com:19302",
    )
]

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def _require_keys() -> None:
    missing = [k for k in ("DEEPGRAM_API_KEY", "CARTESIA_API_KEY") if not os.getenv(k)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)


async def run_spellbee_bot(webrtc_connection: SmallWebRTCConnection) -> None:
    pc_id = webrtc_connection.pc_id
    session = GameSessionState(pc_id=pc_id, words=list(SPELL_WORDS))
    SESSIONS[pc_id] = session

    transport = SmallWebRTCTransport(
        webrtc_connection=webrtc_connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    stt = DeepgramSTTService(
        api_key=os.environ["DEEPGRAM_API_KEY"],
        settings=DeepgramSTTService.Settings(
            punctuate=False,
            smart_format=False,
            interim_results=True,
        ),
    )

    tts = CartesiaTTSService(
        api_key=os.environ["CARTESIA_API_KEY"],
        settings=CartesiaTTSService.Settings(
            voice="71a7ad14-091c-4e8e-a314-022ece01c121",
        ),
    )

    task_ref: dict[str, Any] = {}
    spell = SpellBeeGameProcessor(session=session, task_ref=task_ref)

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            spell,
            tts,
            transport.output(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )
    task_ref["task"] = task

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client) -> None:
        logger.info("Spell Bee client connected")
        session.phase = "starting"
        await spell.start_session()

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client) -> None:
        logger.info("Spell Bee client disconnected")
        SESSIONS.pop(pc_id, None)
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)
    await runner.run(task)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    coros = [pc.disconnect() for pc in pcs_map.values()]
    await asyncio.gather(*coros, return_exceptions=True)
    pcs_map.clear()
    SESSIONS.clear()


app = FastAPI(title="Spell Bee Voice Bot", lifespan=lifespan)

app.mount("/client", SmallWebRTCPrebuiltUI, name="prebuilt_client")


@app.get("/", include_in_schema=False)
async def root():
    index = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index):
        return FileResponse(index)
    return RedirectResponse(url="/client/")


@app.get("/api/game/state")
async def game_state(pc_id: str):
    s = SESSIONS.get(pc_id)
    if not s:
        raise HTTPException(status_code=404, detail="Unknown or ended session")
    return s.snapshot()


@app.post("/api/offer")
async def offer(request: dict, background_tasks: BackgroundTasks):
    pc_id = request.get("pc_id")

    if pc_id and pc_id in pcs_map:
        pipecat_connection = pcs_map[pc_id]
        logger.info(f"Reusing WebRTC connection for pc_id={pc_id}")
        await pipecat_connection.renegotiate(
            sdp=request["sdp"],
            type=request["type"],
            restart_pc=request.get("restart_pc", False),
        )
    else:
        pipecat_connection = SmallWebRTCConnection(ice_servers)
        await pipecat_connection.initialize(sdp=request["sdp"], type=request["type"])

        @pipecat_connection.event_handler("closed")
        async def handle_disconnected(webrtc_connection: SmallWebRTCConnection) -> None:
            logger.info(f"Removing peer connection pc_id={webrtc_connection.pc_id}")
            pcs_map.pop(webrtc_connection.pc_id, None)

        background_tasks.add_task(run_spellbee_bot, pipecat_connection)

    answer = pipecat_connection.get_answer()
    if not answer:
        raise HTTPException(status_code=500, detail="No SDP answer")
    pcs_map[answer["pc_id"]] = pipecat_connection
    return answer


def main() -> None:
    _require_keys()
    parser = argparse.ArgumentParser(description="Spell Bee Pipecat server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    parser.add_argument("--port", type=int, default=7860, help="HTTP port")
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
