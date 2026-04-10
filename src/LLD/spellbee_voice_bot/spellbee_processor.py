"""Custom Pipecat frame processor: spelling validation and game flow."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Optional

from loguru import logger
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    InterruptionFrame,
    TranscriptionFrame,
    TTSSpeakFrame,
    VADUserStartedSpeakingFrame,
    VADUserStoppedSpeakingFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from spelling_normalization import letters_only, spelled_from_transcript, tts_letter_by_letter


def merge_spelling_transcripts(prev: str, new: str) -> str:
    """
    Merge Deepgram finals across pauses between letters.

    STT often sends cumulative text (\"see\" then \"see ay\") or a fresh segment
    after a long pause (\"tee\" only). Replacing with the last frame drops earlier
    letters; we concatenate non-cumulative segments instead.
    """
    new_s = (new or "").strip()
    if not new_s:
        return prev
    if not prev:
        return new_s
    prev_l = prev.lower()
    new_l = new_s.lower()
    if new_l.startswith(prev_l) or (prev_l in new_l and len(new_l) > len(prev_l)):
        return new_s
    return f"{prev} {new_s}"


@dataclass
class GameSessionState:
    """session state exposed to the HTTP API and the voice pipeline."""

    pc_id: str
    words: list[str]
    index: int = 0
    score: int = 0
    words_completed: int = 0
    phase: str = "connecting"
    last_bot_prompt: str = ""
    last_user_transcript: str = ""
    last_result: str = ""
    last_normalized_letters: str = ""
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
            "last_normalized_letters": self.last_normalized_letters,
            "message": self.message,
            "interrupted": self.interrupted,
        }

    def current_target(self) -> Optional[str]:
        if self.index >= len(self.words):
            return None
        return self.words[self.index]


class SpellBeeGameProcessor(FrameProcessor):
    """Buffers finals until end-of-speech, validates spelling, queues TTS replies."""

    # Final transcript must be at least this long to count as intentional barge-in (not VAD noise).
    _BARGE_IN_MIN_CHARS = 4

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
        # Merged finals across the whole spelling attempt (handles long pauses between letters).
        self._rolling_transcript: str = ""
        self._eval_task: Optional[asyncio.Task] = None
        # Extra time after VAD end so Deepgram finalize + last letters land in the buffer.
        self._eval_delay_sec = 1.85
        # True while output transport is playing bot TTS (from upstream Bot* frames).
        self._bot_output_active = False
        # Barge-in: only after STT confirms real words (VAD alone fires on background noise).
        self._barge_in_interrupt_sent = False

    def _task(self):
        t = self._task_ref.get("task")
        if t is None:
            raise RuntimeError("PipelineTask not bound yet")
        return t

    def _should_barge_in_on_transcript(self, frame: TranscriptionFrame) -> bool:
        """Interrupt bot TTS only when STT produces a substantive final (not VAD alone)."""
        if self._session.phase == "done" or self._barge_in_interrupt_sent:
            return False
        if self._listening_for_spell:
            return False
        if not (self._bot_output_active or self._session.phase == "bot_speaking"):
            return False
        text = (frame.text or "").strip()
        # Deepgram emits TranscriptionFrame only for finals; keep a floor to drop noise crumbs.
        if len(text) < self._BARGE_IN_MIN_CHARS:
            return False
        return True

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
            "When you are ready, spell it letter by letter, using English letter names. "
            "Pause for about two seconds when you are done."
        )
        self._session.last_bot_prompt = intro
        self._listening_for_spell = False
        self._session.interrupted = False
        await self._task().queue_frames([TTSSpeakFrame(intro)])
        logger.info(f"SpellBee: Started session for word {w}")

    # This method handles everything
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if direction == FrameDirection.DOWNSTREAM:
            if isinstance(frame, TranscriptionFrame):
                if self._listening_for_spell and self._session.phase != "done":
                    self._rolling_transcript = merge_spelling_transcripts(
                        self._rolling_transcript, frame.text
                    )
                    self._session.last_user_transcript = self._rolling_transcript
                elif self._should_barge_in_on_transcript(frame):
                    await self.broadcast_interruption()
                    self._barge_in_interrupt_sent = True
                    logger.info(
                        "SpellBee: STT barge-in during bot speech — interruption broadcast "
                        f"(text={frame.text!r})"
                    )
            elif isinstance(frame, VADUserStartedSpeakingFrame):
                if self._listening_for_spell and self._session.phase != "done":
                    self._cancel_pending_eval()
            elif isinstance(frame, VADUserStoppedSpeakingFrame):
                if self._listening_for_spell and self._session.phase != "done":
                    self._schedule_evaluate()
            elif isinstance(frame, InterruptionFrame):
                self._session.interrupted = True
                self._session.message = "User interrupted bot speech; listening resumes after bot stops."
                logger.info("SpellBee: InterruptionFrame — bot audio cancelled, pipeline handles cleanup.")

        elif direction == FrameDirection.UPSTREAM:
            if isinstance(frame, BotStartedSpeakingFrame):
                self._bot_output_active = True
                self._barge_in_interrupt_sent = False
            elif isinstance(frame, BotStoppedSpeakingFrame):
                self._bot_output_active = False
                if self._session.phase != "done":
                    self._listening_for_spell = True
                    self._rolling_transcript = ""
                    self._session.phase = "listening"
                    self._session.message = "Waiting for your spelling."

        await self.push_frame(frame, direction)

    def _cancel_pending_eval(self) -> None:
        if self._eval_task and not self._eval_task.done():
            self._eval_task.cancel()
            self._eval_task = None

    def _schedule_evaluate(self) -> None:
        self._cancel_pending_eval()
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

        raw = self._rolling_transcript
        self._rolling_transcript = ""
        spoken = spelled_from_transcript(raw)
        if not spoken:
            # Whole word at once (e.g. "cat") — not in letter-name map.
            spoken = letters_only(raw)
        expected = letters_only(target)
        self._session.last_normalized_letters = spoken

        self._session.last_user_transcript = raw
        self._listening_for_spell = False
        self._session.phase = "evaluating"

        if not spoken:
            self._session.last_result = "empty"
            logger.debug(f"SpellBee: empty normalized spelling raw={raw!r}")
            reply = (
                "I did not catch any letters. Let's try the same word again. "
                f"The word is {target}. Spell it when you're ready."
            )
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
        correct_letters = tts_letter_by_letter(target)
        reply = (
            f"Not quite. The correct spelling is: {correct_letters}. "
            f"Next: word {self._session.index + 1} of {len(self._session.words)}. "
            f"The word is {next_w}. Spell it when ready."
        )
        await self._speak_only(reply)

    async def _speak_only(self, text: str) -> None:
        self._session.interrupted = False
        self._session.last_bot_prompt = text
        self._session.phase = "bot_speaking"
        await self._task().queue_frames([TTSSpeakFrame(text)])

    async def _finish_game(self, last_word: str | None = None) -> None:
        self._session.phase = "done"
        self._listening_for_spell = False
        self._rolling_transcript = ""
        if last_word:
            lw = tts_letter_by_letter(last_word)
            msg = (
                f"Game over. Your final score is {self._session.score} out of {len(self._session.words)}. "
                f"The last word was {last_word}, spelled {lw}. Thanks for playing."
            )
        else:
            msg = (
                f"Congratulations, you have spelled all words. "
                f"Final score: {self._session.score} out of {len(self._session.words)}. Thanks for playing."
            )
        self._session.message = "Session complete."
        self._session.interrupted = False
        self._session.last_bot_prompt = msg
        await self._task().queue_frames([TTSSpeakFrame(msg)])
