"""
Simon TTS – Text-to-Speech using Edge-TTS with pygame audio playback.
Fast, no extra windows, supports audio queue and stop mid-speech.
"""

import asyncio
import logging
import os
import tempfile
import threading
from pathlib import Path
from typing import Optional

import edge_tts

from simon.config_loader import load_config

LOGGER = logging.getLogger("simon.voice.tts")

_cfg = load_config().get("voice", {})
VOICE_VI = _cfg.get("tts_voice", "vi-VN-NamMinhNeural")
VOICE_EN = _cfg.get("tts_voice_en", "en-US-GuyNeural")

# Audio playback state
_playback_lock = threading.Lock()
_stop_flag = threading.Event()
_mixer_initialized = False


def _init_mixer() -> bool:
    """Initialize pygame mixer if available."""
    global _mixer_initialized
    if _mixer_initialized:
        return True
    try:
        import pygame
        pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=2048)
        _mixer_initialized = True
        LOGGER.info("pygame.mixer initialized for TTS playback")
        return True
    except ImportError:
        LOGGER.warning("pygame not installed – falling back to system player")
        return False
    except Exception as exc:
        LOGGER.warning("pygame.mixer init failed: %s – falling back", exc)
        return False


def get_voice(language: str = "vi") -> str:
    """Get the TTS voice for the given language."""
    return VOICE_EN if language == "en" else VOICE_VI


async def _synthesize_to_file(text: str, output_file: Path, voice: str) -> None:
    """Synthesize text to audio file using Edge-TTS."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_file))


def _run_async(coro):
    """Run an async coroutine from sync context, handling existing event loops."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()


def _play_with_pygame(filepath: str) -> None:
    """Play audio file using pygame.mixer (non-blocking, stoppable)."""
    import pygame
    try:
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if _stop_flag.is_set():
                pygame.mixer.music.stop()
                break
            pygame.time.wait(50)
    except Exception as exc:
        LOGGER.warning("pygame playback error: %s", exc)


def _play_with_system(filepath: str) -> None:
    """Fallback: play audio using system command."""
    if os.name == "nt":
        # Use PowerShell to play without opening a window
        import subprocess
        try:
            subprocess.run(
                [
                    "powershell", "-WindowStyle", "Hidden", "-Command",
                    f"Add-Type -AssemblyName PresentationCore; "
                    f"$player = New-Object System.Windows.Media.MediaPlayer; "
                    f"$player.Open('{filepath}'); "
                    f"Start-Sleep -Milliseconds 500; "
                    f"$player.Play(); "
                    f"Start-Sleep -Seconds ([math]::Ceiling($player.NaturalDuration.TimeSpan.TotalSeconds + 1)); "
                    f"$player.Close();"
                ],
                capture_output=True,
                timeout=60,
            )
        except Exception as exc:
            LOGGER.warning("PowerShell playback failed: %s, trying wmplayer", exc)
            os.system(f'start /min wmplayer "{filepath}"')
    else:
        os.system(f'afplay "{filepath}"')


def speak(text: str, language: str = "vi") -> None:
    """
    Synthesize and play speech. Thread-safe with stop support.
    Uses pygame.mixer if available, falls back to system player.
    """
    _stop_flag.clear()

    with _playback_lock:
        output_file = Path(tempfile.gettempdir()) / "simon_voice_output.mp3"
        voice = get_voice(language)

        try:
            _run_async(_synthesize_to_file(text, output_file, voice))
        except Exception as exc:
            LOGGER.exception("TTS synthesis failed")
            return

        if _stop_flag.is_set():
            return

        if _init_mixer():
            _play_with_pygame(str(output_file))
        else:
            _play_with_system(str(output_file))


def stop_speaking() -> None:
    """Stop any currently playing speech."""
    _stop_flag.set()
    try:
        import pygame
        if _mixer_initialized and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    except Exception:
        pass


def is_speaking() -> bool:
    """Check if TTS is currently playing."""
    try:
        import pygame
        if _mixer_initialized:
            return pygame.mixer.music.get_busy()
    except Exception:
        pass
    return False
