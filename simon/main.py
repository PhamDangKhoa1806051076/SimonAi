import asyncio
import logging
from pathlib import Path

from simon.brain.ollama_brain import SimonBrain
from simon.config_loader import get_brain

LOG_PATH = Path(__file__).resolve().parent.parent / "simon_build_log.md"
LOGGER = logging.getLogger("simon")
LOGGER.setLevel(logging.DEBUG)
if not LOGGER.handlers:
    fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    LOGGER.addHandler(fh)
    LOGGER.addHandler(logging.StreamHandler())


def build_log(title: str, content: str = "") -> None:
    LOGGER.info("BUILD_LOG: %s | %s", title, content.replace("\n", " ") if content else "-")


async def main_async() -> None:
    build_log("Project scaffold", "Folder structure, brain prompt, config loader")
    build_log("GitHub remote", "https://github.com/PhamDangKhoa1806051076/SimonAi.git")

    brain: SimonBrain = get_brain()
    build_log("Brain init", f"Ollama URL={brain.ollama_url} model={brain.model}")

    build_log("Main loop started")
    try:
        while True:
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
            except Exception as exc:
                LOGGER.exception("Brain request failed")
                build_log("Brain error", str(exc))
    except KeyboardInterrupt:
        build_log("Main loop interrupted")
    finally:
        build_log("Main loop exit")


if __name__ == "__main__":
    asyncio.run(main_async())
