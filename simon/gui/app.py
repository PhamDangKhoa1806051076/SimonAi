import threading
import queue

import customtkinter as ctk

from simon.brain.openai_brain import SimonBrain


class SimonGUI:
    def __init__(self, brain: SimonBrain) -> None:
        self.brain = brain
        self.root = ctk.CTk()
        self.root.title("Simon AI")
        self.root.geometry("720x820")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.voice_mode = False
        self._queue = queue.Queue()

        self._build_ui()
        self._drain_queue()

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self.root)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(
            container,
            text="SIMON",
            font=("Segoe UI", 26, "bold"),
            text_color="#00d4ff",
        )
        title.pack(pady=(0, 12))

        self.chat = ctk.CTkTextbox(
            container,
            wrap="word",
            font=("Consolas", 12),
            fg_color="#05070a",
            text_color="#e6f1ff",
            border_color="#1f2937",
        )
        self.chat.pack(fill="both", expand=True, padx=8, pady=8)
        self._append_text("Simon: Chào Chủ nhân, Simon đã kết nối. Tôi có thể giúp gì cho bạn?\n")

        input_frame = ctk.CTkFrame(container, fg_color="transparent")
        input_frame.pack(fill="x", padx=8, pady=(8, 0))

        self.entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Nhắn Simon...",
            font=("Consolas", 12),
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry.bind("<Return>", lambda _event: self._on_send())

        send = ctk.CTkButton(
            input_frame,
            text="Gửi",
            command=self._on_send,
            width=72,
            fg_color="#0ea5e9",
            hover_color="#0284c7",
        )
        send.pack(side="right")

        self.voice_btn = ctk.CTkButton(
            container,
            text="Voice: TẮT",
            command=self._toggle_voice,
            width=120,
            fg_color="#111827",
            hover_color="#1f2937",
            border_width=1,
            border_color="#334155",
        )
        self.voice_btn.pack(pady=(8, 0))

        self.status = ctk.CTkLabel(
            container,
            text="Sẵn sàng",
            text_color="#22c55e",
            anchor="w",
        )
        self.status.pack(anchor="w", padx=8, pady=(6, 0))

    def _toggle_voice(self) -> None:
        self.voice_mode = not self.voice_mode
        self.voice_btn.configure(text=f"Voice: {'BẬT' if self.voice_mode else 'TẮT'}")

    def _on_send(self, event=None) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._append_text(f"Bạn: {text}\n")
        self._set_status("Đang suy nghĩ...", "#facc15")
        threading.Thread(target=self._brain_ask, args=(text,), daemon=True).start()

    def _brain_ask(self, text: str) -> None:
        try:
            reply = self.brain.ask(text)
            self._queue.put(("reply", reply))
        except Exception as exc:
            self._queue.put(("error", str(exc)))

    def _drain_queue(self) -> None:
        try:
            while True:
                kind, payload = self._queue.get_nowait()
                if kind == "reply":
                    self._append_text(f"Simon: {payload}\n")
                    self._set_status("Sẵn sàng", "#22c55e")
                    if self.voice_mode:
                        threading.Thread(target=self._speak, args=(payload,), daemon=True).start()
                elif kind == "error":
                    self._set_status(f"Lỗi: {payload}", "#ef4444")
        except queue.Empty:
            pass
        self._after_id = self.root.after(120, self._drain_queue)

    def _speak(self, text: str) -> None:
        try:
            from simon.voice.tts import speak
            speak(text)
        except Exception as exc:
            self._queue.put(("error", str(exc)))

    def _append_text(self, text: str) -> None:
        self.chat.configure(state="normal")
        self.chat.insert("end", text)
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def _set_status(self, text: str, color: str) -> None:
        self.status.configure(text=text, text_color=color)

    def run(self) -> None:
        self.root.mainloop()


def launch_gui(brain: SimonBrain) -> None:
    app = SimonGUI(brain)
    app.run()
