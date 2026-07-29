import asyncio
import logging
import os
import sys
from pathlib import Path

from simon.brain.openai_brain import SimonBrain
from simon.config_loader import get_brain, load_config
from simon.voice.stt import listen
from simon.voice.tts import speak

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

LOG_PATH = BASE_DIR / "simon_build_log.md"
LOGGER = logging.getLogger("simon")
LOGGER.setLevel(logging.DEBUG)
if not LOGGER.handlers:
    try:
        fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        LOGGER.addHandler(fh)
    except Exception:
        pass
    LOGGER.addHandler(logging.StreamHandler())


def build_log(title: str, content: str = "") -> None:
    LOGGER.info("BUILD_LOG: %s | %s", title, content.replace("\n", " ") if content else "-")


def create_brain() -> SimonBrain:
    cfg = load_config()
    client, model = get_brain()
    brain = SimonBrain(client=client, model=model)
    base_url = cfg.get("openai", {}).get("base_url", "https://api.openai.com/v1")
    build_log("Brain init", f"model={model} base={base_url}")
    _validate_api_key(client, base_url, model, cfg)
    return brain


def _validate_api_key(client, base_url: str, model: str, cfg: dict) -> None:
    openai_cfg = cfg.get("openai", {})
    api_key = openai_cfg.get("api_key", "")
    if not api_key or api_key == "YOUR_API_KEY":
        print("[Simon] Chưa cấu hình API key trong file .env hoặc settings.yaml.")
        return
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Reply OK only."},
                {"role": "user", "content": "Hey"},
            ],
            max_tokens=2,
            timeout=20,
        )
        reply = (completion.choices[0].message.content or "").strip()
        print(f"[Simon] API key hợp lệ. Model phản hồi: {reply}")
        build_log("API key validation", f"base={base_url} model={model} reply={reply}")
    except Exception as exc:
        print(f"[Simon] API key không hợp lệ hoặc kết nối thất bại: {exc}")
        LOGGER.warning("API key validation failed: %s", exc)
        build_log("API key validation failed", str(exc))


async def main_async(voice_mode: bool = False) -> None:
    build_log("Main loop started", f"voice_mode={voice_mode}")
    brain = create_brain()
    try:
        while True:
            language = brain.current_language
            if voice_mode:
                user_input = listen(language=language)
            else:
                user_input = input("Bạn: ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit", "thoát"}:
                build_log("Main loop ended")
                break

            try:
                reply = brain.ask(user_input)
                print("Simon:", reply)
                build_log("User input", user_input)
                build_log("Simon reply", reply)
                if voice_mode:
                    speak(reply, language=brain.current_language)
            except Exception as exc:
                LOGGER.exception("Brain request failed")
                build_log("Brain error", str(exc))
    except KeyboardInterrupt:
        build_log("Main loop interrupted")
    finally:
        build_log("Main loop exit")


if __name__ == "__main__":
    print("Chọn chế độ (1: Text, 2: Voice, 3: GUI)")
    try:
        mode = input("Chọn: ").strip()
    except Exception:
        mode = "1"

    brain = create_brain()

    if mode == "3":
        try:
            from simon.gui.app import launch_gui
            launch_gui(brain)
        except Exception as exc:
            LOGGER.exception("GUI failed")
            print("Không thể khởi chạy GUI, đang chuyển về text mode...")
            asyncio.run(main_async(voice_mode=False))
    elif mode == "2":
        asyncio.run(main_async(voice_mode=True))
    else:
        asyncio.run(main_async(voice_mode=False))
