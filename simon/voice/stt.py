"""
Simon STT – Speech-to-Text using Google Speech Recognition.
Improved with ambient noise calibration, continuous listening, and better error handling.
"""

import logging
from typing import Optional

import speech_recognition as sr

from simon.config_loader import load_config

LOGGER = logging.getLogger("simon.voice.stt")

_cfg = load_config().get("voice", {})
STT_LANG_VI = _cfg.get("stt_language", "vi-VN")
STT_LANG_EN = _cfg.get("stt_language_en", "en-US")


def listen(
    timeout: int = 8,
    phrase_time_limit: int = 15,
    language: str = "vi",
    calibrate: bool = True,
    calibration_duration: float = 0.5,
) -> str:
    """
    Listen for speech and convert to text.

    Args:
        timeout: Max seconds to wait for speech to start.
        phrase_time_limit: Max seconds for a single phrase.
        language: 'vi' or 'en'.
        calibrate: Whether to calibrate for ambient noise first.
        calibration_duration: Seconds to spend calibrating.

    Returns:
        Recognized text, or empty string on failure/silence.
    """
    recognizer = sr.Recognizer()
    lang = STT_LANG_VI if language == "vi" else STT_LANG_EN

    # Tuning for better recognition
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8

    try:
        with sr.Microphone() as source:
            if calibrate:
                LOGGER.debug("Calibrating for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=calibration_duration)

            print("[Simon] 🎤 Đang lắng nghe...")
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

            text = recognizer.recognize_google(audio, language=lang)
            print(f"[Bạn]: {text}")
            LOGGER.info("STT recognized: %s", text)
            return text

    except sr.WaitTimeoutError:
        LOGGER.debug("No speech detected (timeout)")
        return ""
    except sr.UnknownValueError:
        LOGGER.debug("Speech not understood")
        print("[Simon] Xin lỗi, tôi không nghe rõ. Chủ nhân nói lại được không?")
        return ""
    except sr.RequestError as exc:
        LOGGER.error("Google STT request failed: %s", exc)
        print(f"[Simon] Lỗi kết nối STT: {exc}")
        return ""
    except OSError as exc:
        LOGGER.error("Microphone error: %s", exc)
        print(f"[Simon] Lỗi microphone: {exc}")
        return ""
    except Exception as exc:
        LOGGER.exception("Unexpected STT error")
        return ""


def listen_continuous(
    language: str = "vi",
    on_speech: Optional[callable] = None,
    stop_event=None,
) -> None:
    """
    Continuously listen and call on_speech(text) for each recognized phrase.
    Runs until stop_event is set (threading.Event).
    """
    import threading

    if stop_event is None:
        stop_event = threading.Event()

    LOGGER.info("Starting continuous listening (lang=%s)", language)

    while not stop_event.is_set():
        text = listen(
            timeout=10,
            phrase_time_limit=15,
            language=language,
            calibrate=False,
            calibration_duration=0.3,
        )
        if text and on_speech:
            try:
                on_speech(text)
            except Exception as exc:
                LOGGER.exception("Continuous listen callback error")
