"""
Simon Brain – OpenAI-compatible AI core with Function Calling & Conversation History.
Supports automatic tool execution loop: Brain decides → tool runs → result fed back → final reply.
"""

import json
import logging
from typing import Any, Callable, Generator, Optional

from openai import OpenAI

from simon.brain.simon_prompt import get_system_prompt

LOGGER = logging.getLogger("simon.brain")


class SimonBrain:
    """Core AI brain with function calling and persistent conversation history."""

    def __init__(
        self,
        client: OpenAI,
        model: str,
        timeout: int = 60,
        max_history: int = 50,
    ) -> None:
        self.client = client
        self.model = model
        self.timeout = timeout
        self.max_history = max_history
        self.current_language = "vi"

        # Persistent conversation history (excludes system prompt – rebuilt each call)
        self._history: list[dict[str, Any]] = []

        # Tool registry: name → (callable, openai_schema)
        self._tools: dict[str, tuple[Callable, dict]] = {}

    # ------------------------------------------------------------------
    # Tool registration
    # ------------------------------------------------------------------
    def register_tool(self, name: str, func: Callable, schema: dict) -> None:
        """Register a tool that the Brain can call via function calling."""
        self._tools[name] = (func, schema)
        LOGGER.info("Registered tool: %s", name)

    def register_tools(self, tools: dict[str, tuple[Callable, dict]]) -> None:
        """Bulk register tools. Each value is (callable, openai_schema)."""
        for name, (func, schema) in tools.items():
            self.register_tool(name, func, schema)

    # ------------------------------------------------------------------
    # Build messages
    # ------------------------------------------------------------------
    def _get_openai_tools(self) -> list[dict] | None:
        """Return OpenAI-format tools list, or None if no tools registered."""
        if not self._tools:
            return None
        return [schema for _, (_, schema) in self._tools.items()]

    def _build_messages(self, user_input: str) -> list[dict]:
        """Build full message list: system + trimmed history + new user msg."""
        tool_names = list(self._tools.keys()) if self._tools else None
        system_prompt = get_system_prompt(
            language=self.current_language,
            available_tools=tool_names,
        )
        messages = [{"role": "system", "content": system_prompt}]

        # Trim history to max_history (keep recent messages)
        trimmed = self._history[-(self.max_history * 2):]
        messages.extend(trimmed)

        messages.append({"role": "user", "content": user_input})
        return messages

    # ------------------------------------------------------------------
    # Tool execution
    # ------------------------------------------------------------------
    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a registered tool and return its result as string."""
        if tool_name not in self._tools:
            return f"Error: tool '{tool_name}' not found."
        func, _ = self._tools[tool_name]
        try:
            result = func(**arguments)
            LOGGER.info("Tool %s(%s) → %s", tool_name, arguments, result)
            return str(result)
        except Exception as exc:
            LOGGER.exception("Tool %s execution failed", tool_name)
            return f"Error executing {tool_name}: {exc}"

    # ------------------------------------------------------------------
    # Language switching (handled locally for instant response)
    # ------------------------------------------------------------------
    def _check_language_switch(self, user_input: str) -> str | None:
        """Check if user wants to switch language. Returns reply or None."""
        lower = user_input.strip().lower()

        if any(k in lower for k in ["switch to english", "chuyển sang tiếng anh"]):
            self.current_language = "en"
            reply = "Understood, Sir. I will reply in English from now on."
            self._history.append({"role": "user", "content": user_input})
            self._history.append({"role": "assistant", "content": reply})
            return reply

        if any(k in lower for k in ["switch to vietnamese", "chuyển sang tiếng việt"]):
            self.current_language = "vi"
            reply = "Đã rõ, Chủ nhân. Từ giờ tôi sẽ trả lời bằng tiếng Việt."
            self._history.append({"role": "user", "content": user_input})
            self._history.append({"role": "assistant", "content": reply})
            return reply

        return None

    # ------------------------------------------------------------------
    # Main ask (blocking)
    # ------------------------------------------------------------------
    def ask(self, user_input: str) -> str:
        """
        Send user input to the Brain. Handles:
        1. Language switching
        2. Function calling (auto tool execution loop)
        3. Regular conversation with history
        Returns the final text reply.
        """
        # Check language switch first
        lang_reply = self._check_language_switch(user_input)
        if lang_reply:
            return lang_reply

        messages = self._build_messages(user_input)
        tools = self._get_openai_tools()

        # Function calling loop (max 5 iterations to prevent infinite loops)
        for _ in range(5):
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "timeout": self.timeout,
                "max_tokens": 600,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"


            try:
                completion = self.client.chat.completions.create(**kwargs)
            except Exception as exc:
                LOGGER.exception("Brain API call failed")
                error_msg = f"Xin lỗi Chủ nhân, tôi gặp lỗi kết nối: {exc}"
                return error_msg

            choice = completion.choices[0]
            message = choice.message

            if message.tool_calls:
                # Add assistant's tool_calls message to conversation (strictly format for OpenAI/Groq compatibility)
                messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                    ],
                })

                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    try:
                        func_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        func_args = {}

                    LOGGER.info("Brain calling tool: %s(%s)", func_name, func_args)
                    result = self._execute_tool(func_name, func_args)

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })

                # Continue loop – model will process tool results
                continue

            # No tool calls – we have the final reply
            reply = (message.content or "").strip()
            if not reply:
                reply = "Tôi đã xử lý xong, Chủ nhân." if self.current_language == "vi" else "Done, Sir."

            # Save to history
            self._history.append({"role": "user", "content": user_input})
            self._history.append({"role": "assistant", "content": reply})

            return reply

        # Fallback if loop exhausted
        return "Xin lỗi Chủ nhân, tôi gặp khó khăn khi xử lý yêu cầu này." if self.current_language == "vi" else "Sorry Sir, I had trouble processing that request."

    # ------------------------------------------------------------------
    # Streaming ask (for GUI real-time display)
    # ------------------------------------------------------------------
    def ask_stream(self, user_input: str) -> Generator[str, None, None]:
        """
        Stream response tokens. Yields chunks of text as they arrive.
        Handles tool calls internally before streaming final response.
        """
        lang_reply = self._check_language_switch(user_input)
        if lang_reply:
            yield lang_reply
            return

        messages = self._build_messages(user_input)
        tools = self._get_openai_tools()

        # First pass: handle any tool calls (non-streaming)
        for _ in range(5):
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "timeout": self.timeout,
                "max_tokens": 600,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"


            try:
                completion = self.client.chat.completions.create(**kwargs)
            except Exception as exc:
                LOGGER.exception("Brain stream API call failed")
                yield f"Xin lỗi Chủ nhân, lỗi kết nối: {exc}"
                return

            choice = completion.choices[0]
            message = choice.message

            if not message.tool_calls:
                # If no tools were called in the first pass, we already have the full reply!
                reply = (message.content or "").strip()
                if not reply:
                    reply = "Tôi đã xử lý xong, Chủ nhân." if self.current_language == "vi" else "Done, Sir."

                self._history.append({"role": "user", "content": user_input})
                self._history.append({"role": "assistant", "content": reply})

                # Stream out the response tokens/words smoothly
                import re
                chunks = re.findall(r"\S+\s*|\s+", reply)
                for chunk in chunks:
                    yield chunk
                return

            # Tool calls present: append assistant message and execute tools
            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    func_args = {}
                result = self._execute_tool(func_name, func_args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
            # Continue loop to process tool results or stream final reply

        # Stream the final response
        try:
            stream_kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "timeout": self.timeout,
                "max_tokens": 600,
                "stream": True,
            }

            stream = self.client.chat.completions.create(**stream_kwargs)

            full_reply = []
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_reply.append(token)
                    yield token

            final_text = "".join(full_reply).strip()
            if final_text:
                self._history.append({"role": "user", "content": user_input})
                self._history.append({"role": "assistant", "content": final_text})

        except Exception as exc:
            LOGGER.exception("Brain streaming failed")
            yield f"\n[Lỗi streaming: {exc}]"

    # ------------------------------------------------------------------
    # History management
    # ------------------------------------------------------------------
    def clear_history(self) -> None:
        """Clear conversation history."""
        self._history.clear()

    def get_history(self) -> list[dict]:
        """Return a copy of conversation history."""
        return list(self._history)

    @property
    def history_count(self) -> int:
        """Number of messages in history."""
        return len(self._history)
