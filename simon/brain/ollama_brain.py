import json
from typing import Any, Dict, Optional

import requests

from simon.brain.simon_prompt import SIMON_SYSTEM_PROMPT


class SimonBrain:
    def __init__(self, ollama_url: str, model: str, timeout: int = 120):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def ask(self, user_input: str, history: Optional[list[Dict[str, str]]] = None) -> str:
        payload = {
            "model": self.model,
            "system": SIMON_SYSTEM_PROMPT,
            "prompt": user_input,
            "stream": False,
        }
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
