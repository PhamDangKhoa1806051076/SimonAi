import sys
from pathlib import Path

import yaml
from openai import OpenAI

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
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_brain():
    cfg = load_config()
    openai_cfg = cfg.get("openai", {})
    return OpenAI(
        api_key=openai_cfg.get("api_key", ""),
        base_url=openai_cfg.get("base_url", "https://api.openai.com/v1"),
    )
