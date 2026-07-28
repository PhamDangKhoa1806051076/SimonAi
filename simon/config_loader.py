import os
import sys
from pathlib import Path

from dotenv import load_dotenv
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

ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=False)


def _first(*values):
    for value in values:
        if value:
            return value
    return ""


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def get_brain():
    cfg = load_config()
    openai_cfg = cfg.get("openai", {})
    api_key = _first(os.getenv("SIMON_OPENAI_API_KEY"), openai_cfg.get("api_key", ""))
    base_url = _first(os.getenv("SIMON_OPENAI_BASE_URL"), openai_cfg.get("base_url", "https://api.openai.com/v1"))
    model = _first(os.getenv("SIMON_OPENAI_MODEL"), openai_cfg.get("model", "gpt-4o-mini"))
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    ), model
