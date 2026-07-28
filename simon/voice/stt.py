import logging
from pathlib import Path

import speech_recognition as sr

from simon.config_loader import load_config

LOGGER = logging.getLogger("simon.voice")
STT_LANG = load_config().get("voice", {}).get("stt_language", "vi-VN")


def listen(timeout: int = 5, phrase_time_limit: int = 15) -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[Simon] đang nghe...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = recognizer.recognize_google(audio, language=STT_LANG)
            print("[Bạn]:", text)
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
