"""Custom Pipecat frame processor: spelling validation and game flow."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Optional

from loguru import logger
from pipecat.frames.frames import (
    BotStoppedSpeakingFrame,
    Frame,
    InterruptionFrame,
    TranscriptionFrame,
    TTSSpeakFrame,
    VADUserStoppedSpeakingFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


def letters_only(text: str) -> str:
    """Normalize spoken or typed spelling to uppercase letters only."""
    return "".join(ch.upper() for ch in text if ch.isalpha())


@dataclass
class GameSessionState:
    """Mutable session state exposed to the HTTP API and the voice pipeline."""

    pc_id: str
    words: list[str]
    index: int = 0
    score: int = 0
    words_completed: int = 0
    phase: str = "connecting"
    last_bot_prompt: str = ""
    last_user_transcript: str = ""
    last_result: str = ""
    message: str = ""
    interrupted: bool = False

    def snapshot(self) -> dict[str, Any]:
        return {
            "pc_id": self.pc_id,
            "score": self.score,
            "word_number": min(self.index + 1, len(self.words)),
            "words_total": len(self.words),
            "words_completed": self.words_completed,
            "phase": self.phase,
            "last_result": self.last_result,
            "last_user_transcript": self.last_user_transcript,
            "message": self.message,
            "interrupted": self.interrupted,
        }

    def current_target(self) -> Optional[str]:
        if self.index >= len(self.words):
            return None
        return self.words[self.index]


class SpellBeeGameProcessor(FrameProcessor):
    """Buffers finals until end-of-speech, validates spelling, queues TTS replies."""

    def __init__(
        self,
        session: GameSessionState,
        task_ref: dict[str, Any],
        **kwargs,
    ):
        super().__init__(name="SpellBeeGame", **kwargs)
        self._session = session
        self._task_ref = task_ref
        self._listening_for_spell = False
        self._spell_parts: list[str] = []
        self._eval_task: Optional[asyncio.Task] = None
        self._eval_delay_sec = 0.5

    def _task(self):
        t = self._task_ref.get("task")
        if t is None:
            raise RuntimeError("PipelineTask not bound yet")
        return t

    async def start_session(self) -> None:
        """Queue intro + first word after the client is connected."""
        w = self._session.current_target()
        if not w:
            self._session.phase = "done"
            self._session.message = "No words configured."
            return
        self._session.phase = "bot_speaking"
        intro = (
            f"Welcome to Spell Bee. There are {len(self._session.words)} words. "
            f"Word number {self._session.index + 1}. Your word is {w}. "
            "When you are ready, spell it letter by letter."
        )
        self._session.last_bot_prompt = intro
        self._listening_for_spell = False
        await self._task().queue_frames([TTSSpeakFrame(intro)])

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if direction == FrameDirection.DOWNSTREAM:
            if isinstance(frame, TranscriptionFrame):
                if self._listening_for_spell and self._session.phase != "done":
                    self._spell_parts.append(frame.text)
                    self._session.last_user_transcript = " ".join(self._spell_parts).strip()
            elif isinstance(frame, VADUserStoppedSpeakingFrame):
                if self._listening_for_spell and self._session.phase != "done":
                    self._schedule_evaluate()
            elif isinstance(frame, InterruptionFrame):
                self._session.interrupted = True
                self._session.message = "User interrupted bot speech; listening resumes after bot stops."
                logger.info("SpellBee: InterruptionFrame — bot audio cancelled, pipeline handles cleanup.")

        elif direction == FrameDirection.UPSTREAM:
            if isinstance(frame, BotStoppedSpeakingFrame):
                if self._session.phase != "done":
                    self._listening_for_spell = True
                    self._spell_parts = []
                    self._session.phase = "listening"
                    self._session.message = "Waiting for your spelling."
                self._session.interrupted = False

        await self.push_frame(frame, direction)

    def _schedule_evaluate(self) -> None:
        if self._eval_task and not self._eval_task.done():
            self._eval_task.cancel()
        self._eval_task = self.create_task(self._evaluate_after_delay(), "spellbee_eval")

    async def _evaluate_after_delay(self) -> None:
        try:
            await asyncio.sleep(self._eval_delay_sec)
            await self._evaluate_spelling()
        except asyncio.CancelledError:
            raise

    async def _evaluate_spelling(self) -> None:
        if not self._listening_for_spell or self._session.phase == "done":
            return
        target = self._session.current_target()
        if not target:
            await self._finish_game()
            return

        raw = " ".join(self._spell_parts).strip()
        self._spell_parts = []
        spoken = letters_only(raw)
        expected = letters_only(target)

        self._session.last_user_transcript = raw
        self._listening_for_spell = False
        self._session.phase = "evaluating"

        if not spoken:
            self._session.last_result = "empty"
            reply = "I did not catch any letters. Let's try the same word again. " f"The word is {target}."
            await self._speak_only(reply)
            return

        if spoken == expected:
            self._session.score += 1
            self._session.words_completed += 1
            self._session.last_result = "correct"
            self._session.index += 1
            next_w = self._session.current_target()
            if not next_w:
                await self._finish_game()
                return
            reply = (
                f"Correct! Your score is {self._session.score}. "
                f"Next: word {self._session.index + 1} of {len(self._session.words)}. "
                f"The word is {next_w}. Spell it when ready."
            )
            await self._speak_only(reply)
            return

        self._session.last_result = "incorrect"
        self._session.index += 1
        next_w = self._session.current_target()
        if not next_w:
            await self._finish_game(last_word=target)
            return
        reply = (
            f"Not quite. The correct spelling was {target}. "
            f"Next: word {self._session.index + 1} of {len(self._session.words)}. "
            f"The word is {next_w}. Spell it when ready."
        )
        await self._speak_only(reply)

    async def _speak_only(self, text: str) -> None:
        self._session.last_bot_prompt = text
        self._session.phase = "bot_speaking"
        await self._task().queue_frames([TTSSpeakFrame(text)])

    async def _finish_game(self, last_word: str | None = None) -> None:
        self._session.phase = "done"
        self._listening_for_spell = False
        self._spell_parts = []
        if last_word:
            msg = (
                f"Game over. Your final score is {self._session.score} out of {len(self._session.words)}. "
                f"The last word was {last_word}. Thanks for playing."
            )
        else:
            msg = (
                f"Congratulations, you have spelled all words. "
                f"Final score: {self._session.score} out of {len(self._session.words)}. Thanks for playing."
            )
        self._session.message = "Session complete."
        self._session.last_bot_prompt = msg
        await self._task().queue_frames([TTSSpeakFrame(msg)])
