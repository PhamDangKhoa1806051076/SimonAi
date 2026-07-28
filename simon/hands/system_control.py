import logging
import platform
import subprocess
import webbrowser
from pathlib import Path

import psutil
import pyautogui

LOGGER = logging.getLogger("simon.hands")
pyautogui.FAILSAFE = True


def open_app(app_name: str) -> str:
    app_name = app_name.strip()
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(app_name, shell=True)
        elif system == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        else:
            subprocess.Popen(app_name, shell=True)
        return f"Đã mở {app_name}"
    except Exception as exc:
        LOGGER.exception("open_app failed")
        return f"Không mở được {app_name}: {exc}"


def web_search(query: str) -> str:
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Đã tìm kiếm: {query}"


def check_cpu() -> str:
    return f"CPU usage: {psutil.cpu_percent(interval=1)}%"


def check_ram() -> str:
    mem = psutil.virtual_memory()
    return f"RAM: {mem.percent}% used, {mem.available // (1024 * 1024)} MB available"


def type_text(text: str) -> str:
    pyautogui.typewrite(text)
    return f"Đã gõ: {text}"
