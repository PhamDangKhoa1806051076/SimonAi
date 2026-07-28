import asyncio
import logging
import sys
from pathlib import Path

import yaml

from simon.brain.ollama_brain import SimonBrain

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
    INTERNAL_CONFIG = BASE_DIR / "_internal" / "config" / "settings.yaml"
    if INTERNAL_CONFIG.exists():
        CONFIG_PATH = INTERNAL_CONFIG
    else:
        CONFIG_PATH = BASE_DIR / "config" / "settings.yaml"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    CONFIG_PATH = BASE_DIR / "config" / "settings.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_brain() -> SimonBrain:
    cfg = load_config()
    ollama_cfg = cfg.get("ollama", {})
    return SimonBrain(
        ollama_url=ollama_cfg.get("url", "http://localhost:11434/api/generate"),
        model=ollama_cfg.get("model", "qwen2.5:3b"),
    )
