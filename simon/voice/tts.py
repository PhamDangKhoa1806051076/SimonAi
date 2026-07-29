import asyncio
import os
import tempfile
from pathlib import Path

import edge_tts

from simon.config_loader import load_config


VOICE = load_config().get("voice", {}).get("tts_voice", "vi-VN-SimonNeural")


async def _synthesize_to_file(text: str, output_file: Path) -> None:
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(str(output_file))


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()


def speak(text: str) -> None:
    output_file = Path(tempfile.gettempdir()) / "simon_voice_output.mp3"
    _run_async(_synthesize_to_file(text, output_file))
    if os.name == "nt":
        os.system(f"start /min wmplayer \"{output_file}\"")
    else:
        os.system(f"afplay \"{output_file}\"")
