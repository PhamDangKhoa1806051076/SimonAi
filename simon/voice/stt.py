import logging
from pathlib import Path

import speech_recognition as sr

from simon.config_loader import load_config

LOGGER = logging.getLogger("simon.voice")
STT_LANG_VI = load_config().get("voice", {}).get("stt_language", "vi-VN")
STT_LANG_EN = load_config().get("voice", {}).get("stt_language_en", "en-US")


def listen(timeout: int = 5, phrase_time_limit: int = 15, language: str = "vi") -> str:
    recognizer = sr.Recognizer()
    lang = STT_LANG_VI if language == "vi" else STT_LANG_EN
    with sr.Microphone() as source:
        print("[Simon] listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = recognizer.recognize_google(audio, language=lang)
            print("[You]:", text)
            return text
        except sr.WaitTimeoutError:
            LOGGER.warning("No speech detected")
            return ""
        except sr.UnknownValueError:
            LOGGER.warning("Speech not understood")
            return ""
        except Exception as exc:
            LOGGER.exception("STT error")
            return ""
