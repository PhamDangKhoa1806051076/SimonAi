import asyncio
import logging
from pathlib import Path

import yaml

from simon.brain.ollama_brain import SimonBrain

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "settings.yaml"


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
