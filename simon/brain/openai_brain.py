import re
from typing import Optional

from openai import OpenAI

from simon.brain.simon_prompt import SIMON_SYSTEM_PROMPT


class SimonBrain:
    def __init__(self, client: OpenAI, model: str, timeout: int = 60):
        self.client = client
        self.model = model
        self.timeout = timeout
        self.current_language = "vi"

    def _build_system_prompt(self) -> str:
        lang_hint = "Trả lời bằng tiếng Việt." if self.current_language == "vi" else "Reply in English."
        return f"{SIMON_SYSTEM_PROMPT}\n\nNgôn ngữ hiện tại: {self.current_language}\n{lang_hint}"

    def ask(self, user_input: str, history: Optional[list[dict]] = None) -> str:
        prompt = user_input.strip()
        lower = prompt.lower()

        if any(k in lower for k in ["switch to english", "chuyển sang tiếng anh"]):
            self.current_language = "en"
            return "Understood, Sir. I will reply in English from now on."

        if any(k in lower for k in ["switch to vietnamese", "chuyển sang tiếng việt"]):
            self.current_language = "vi"
            return "Đã rõ, Chủ nhân. Từ giờ tôi sẽ trả lời bằng tiếng Việt."

        if "current language" in lower or "ngôn ngữ hiện tại" in lower:
            return f"Current language is {'English' if self.current_language == 'en' else 'Vietnamese'}."

        messages = [{"role": "system", "content": self._build_system_prompt()}]
        messages += history or []
        messages.append({"role": "user", "content": prompt})
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            timeout=self.timeout,
        )
        return completion.choices[0].message.content.strip()
