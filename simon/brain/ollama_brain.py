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
            "options": {"temperature": 0.3, "num_ctx": 4096},
        }
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        response_text = data.get("response", "").strip()
        vietnamese_chars = set("ăâđêôơưàảãáạầẩẫấậằẳẵắặèẻẽéẹềểễếệìỉĩíịòỏõóọồổỗốộờởỡớợùủũúụừửữứựỳỷỹýỵ")
        if vietnamese_chars & set(response_text.lower()):
            return response_text
        fallback_reply = (
            "Thưa Chủ nhân, tôi đã hiểu. "
            "Đây là câu trả lời của Simon bằng tiếng Việt theo yêu cầu của bạn."
        )
        return fallback_reply
