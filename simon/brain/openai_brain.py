from typing import Optional

from openai import OpenAI

from simon.brain.simon_prompt import SIMON_SYSTEM_PROMPT


class SimonBrain:
    def __init__(self, client: OpenAI, model: str, timeout: int = 60):
        self.client = client
        self.model = model
        self.timeout = timeout

    def ask(self, user_input: str, history: Optional[list[dict]] = None) -> str:
        messages = [{"role": "system", "content": SIMON_SYSTEM_PROMPT}]
        messages += history or []
        messages.append({"role": "user", "content": user_input})
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            timeout=self.timeout,
        )
        return completion.choices[0].message.content.strip()
