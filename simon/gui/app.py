"""
Simon GUI – Premium JARVIS-style desktop interface.
Features:
- Arc reactor-inspired header with glow animations
- Chat with typing indicator and streaming support
- Voice toggle, quick action buttons
- Status bar with system info
- Integrated with all Simon modules
"""

import datetime
import queue
import threading
import time
from typing import Optional

import customtkinter as ctk

from simon.brain.openai_brain import SimonBrain

# Color palette – JARVIS/Iron Man inspired
COLORS = {
    "bg_primary": "#030712",       # Near-black
    "bg_secondary": "#0a0f1e",     # Dark navy
    "bg_card": "#0d1525",          # Card background
    "bg_input": "#111827",         # Input background
    "accent": "#00d4ff",           # Cyan/arc reactor blue
    "accent_dim": "#0891b2",       # Dimmed accent
    "accent_glow": "#22d3ee",      # Bright glow
    "accent_gold": "#f59e0b",      # Gold accent
    "text_primary": "#e2e8f0",     # Primary text
    "text_secondary": "#94a3b8",   # Secondary/muted text
    "text_user": "#38bdf8",        # User message color
    "text_simon": "#a5f3fc",       # Simon message color
    "success": "#22c55e",          # Green
    "warning": "#f59e0b",          # Yellow/amber
    "error": "#ef4444",            # Red
    "border": "#1e293b",           # Border color
    "border_accent": "#164e63",    # Accent border
    "btn_primary": "#0e7490",      # Button primary
    "btn_hover": "#0891b2",        # Button hover
    "btn_danger": "#991b1b",       # Danger button
}


class SimonGUI:
    """Premium JARVIS-style GUI for Simon AI."""

    def __init__(self, brain: SimonBrain) -> None:
        self.brain = brain
        self.root = ctk.CTk()
        self.root.title("Simon AI – Personal Assistant")
        self.root.geometry("880x920")
        self.root.minsize(700, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root.configure(fg_color=COLORS["bg_primary"])

        self.voice_mode = False
        self.vision_mode = False
        self._face_watcher = None
        self._queue: queue.Queue = queue.Queue()
        self._is_thinking = False
        self._thinking_dots = 0
        self._voice_listening = False

        self._build_ui()
        self._drain_queue()
        self._animate_status_dot()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Show boot message
        self._show_boot_sequence()


    # ==================================================================
    # UI Construction
    # ==================================================================

    def _build_ui(self) -> None:
        """Build the complete JARVIS-style interface."""

        # Main container
        main = ctk.CTkFrame(self.root, fg_color=COLORS["bg_primary"], corner_radius=0)
        main.pack(fill="both", expand=True)

        # --- Header ---
        self._build_header(main)

        # --- Chat Area ---
        self._build_chat_area(main)

        # --- Input Area ---
        self._build_input_area(main)

        # --- Control Bar ---
        self._build_control_bar(main)

        # --- Status Bar ---
        self._build_status_bar(main)

    def _build_header(self, parent) -> None:
        """Build the JARVIS-style header with glow effect."""
        header = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_secondary"],
            corner_radius=0,
            height=80,
        )
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # Inner container with padding
        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=8)

        # Left: Arc reactor icon + title
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        # Arc reactor indicator (animated dot)
        self.arc_reactor = ctk.CTkLabel(
            left,
            text="◉",
            font=("Segoe UI", 28),
            text_color=COLORS["accent"],
        )
        self.arc_reactor.pack(side="left", padx=(0, 12))

        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(side="left")

        title = ctk.CTkLabel(
            title_frame,
            text="S I M O N",
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["accent"],
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Personal AI Assistant",
            font=("Segoe UI", 10),
            text_color=COLORS["text_secondary"],
        )
        subtitle.pack(anchor="w")

        # Right: model info + language
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", fill="y")

        self.model_label = ctk.CTkLabel(
            right,
            text=f"Model: {self.brain.model}",
            font=("Consolas", 10),
            text_color=COLORS["text_secondary"],
        )
        self.model_label.pack(anchor="e")

        self.lang_label = ctk.CTkLabel(
            right,
            text=f"Language: {'Tiếng Việt' if self.brain.current_language == 'vi' else 'English'}",
            font=("Consolas", 10),
            text_color=COLORS["text_secondary"],
        )
        self.lang_label.pack(anchor="e")

        # Separator line
        sep = ctk.CTkFrame(parent, fg_color=COLORS["accent_dim"], height=1)
        sep.pack(fill="x")

    def _build_chat_area(self, parent) -> None:
        """Build the chat display area."""
        chat_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_primary"],
            corner_radius=0,
        )
        chat_frame.pack(fill="both", expand=True, padx=16, pady=(12, 8))

        self.chat = ctk.CTkTextbox(
            chat_frame,
            wrap="word",
            font=("Consolas", 12),
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent_dim"],
        )
        self.chat.pack(fill="both", expand=True)

        # Configure text tags for coloring
        self.chat._textbox.tag_configure("user_name", foreground=COLORS["text_user"])
        self.chat._textbox.tag_configure("simon_name", foreground=COLORS["accent"])
        self.chat._textbox.tag_configure("system_msg", foreground=COLORS["text_secondary"])
        self.chat._textbox.tag_configure("error_msg", foreground=COLORS["error"])
        self.chat._textbox.tag_configure("tool_msg", foreground=COLORS["accent_gold"])
        self.chat._textbox.tag_configure("timestamp", foreground="#475569")

    def _build_input_area(self, parent) -> None:
        """Build the input area with send button."""
        input_container = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_secondary"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        input_container.pack(fill="x", padx=16, pady=(0, 8))

        inner = ctk.CTkFrame(input_container, fg_color="transparent")
        inner.pack(fill="x", padx=8, pady=8)

        self.entry = ctk.CTkEntry(
            inner,
            placeholder_text="Nhắn Simon... (Enter để gửi)",
            font=("Consolas", 13),
            height=40,
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["border_accent"],
            border_width=1,
            corner_radius=6,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry.bind("<Return>", lambda _e: self._on_send())

        self.send_btn = ctk.CTkButton(
            inner,
            text="⚡ Gửi",
            command=self._on_send,
            width=80,
            height=40,
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["btn_primary"],
            hover_color=COLORS["btn_hover"],
            corner_radius=6,
        )
        self.send_btn.pack(side="right")

    def _build_control_bar(self, parent) -> None:
        """Build control buttons bar."""
        control = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        control.pack(fill="x", padx=16, pady=(0, 8))

        # Voice toggle
        self.voice_btn = ctk.CTkButton(
            control,
            text="🎤 Voice: TẮT",
            command=self._toggle_voice,
            width=120,
            height=32,
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["border"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=6,
        )
        self.voice_btn.pack(side="left", padx=(0, 6))

        # Vision toggle
        self.vision_btn = ctk.CTkButton(
            control,
            text="👁️ Vision: TẮT",
            command=self._toggle_vision,
            width=120,
            height=32,
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["border"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=6,
        )
        self.vision_btn.pack(side="left", padx=(0, 6))

        # Quick actions
        quick_actions = [
            ("📊 Hệ Thống", self._quick_system),
            ("🌤 Thời Tiết", self._quick_weather),
            ("📸 Chụp Màn Hình", self._quick_screenshot),
            ("📷 Quét Camera", self._quick_face_check),
            ("🗑 Xóa Chat", self._clear_chat),
        ]

        for text, cmd in quick_actions:
            btn = ctk.CTkButton(
                control,
                text=text,
                command=cmd,
                width=96,
                height=32,
                font=("Segoe UI", 10),
                fg_color=COLORS["bg_card"],
                hover_color=COLORS["border"],
                border_width=1,
                border_color=COLORS["border"],
                corner_radius=6,
            )
            btn.pack(side="left", padx=(0, 5))


    def _build_status_bar(self, parent) -> None:
        """Build the bottom status bar."""
        status_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_secondary"],
            corner_radius=0,
            height=32,
        )
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)

        inner = ctk.CTkFrame(status_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16)

        # Status indicator dot
        self.status_dot = ctk.CTkLabel(
            inner,
            text="●",
            font=("Segoe UI", 10),
            text_color=COLORS["success"],
        )
        self.status_dot.pack(side="left")

        self.status_label = ctk.CTkLabel(
            inner,
            text="Sẵn sàng",
            font=("Consolas", 10),
            text_color=COLORS["text_secondary"],
        )
        self.status_label.pack(side="left", padx=(4, 16))

        # Memory count
        self.memory_label = ctk.CTkLabel(
            inner,
            text="Memory: --",
            font=("Consolas", 10),
            text_color=COLORS["text_secondary"],
        )
        self.memory_label.pack(side="right", padx=(16, 0))

        # History count
        self.history_label = ctk.CTkLabel(
            inner,
            text=f"History: {self.brain.history_count}",
            font=("Consolas", 10),
            text_color=COLORS["text_secondary"],
        )
        self.history_label.pack(side="right")

    # ==================================================================
    # Boot Sequence
    # ==================================================================

    def _show_boot_sequence(self) -> None:
        """Show JARVIS-style boot messages."""
        boot_msgs = [
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "  S I M O N  A I  –  Initializing...",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"  ▸ Brain: {self.brain.model} ✓",
            f"  ▸ Language: {'Tiếng Việt' if self.brain.current_language == 'vi' else 'English'} ✓",
            f"  ▸ Tools: {len(self.brain._tools)} loaded ✓",
            "  ▸ All systems operational",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        ]
        for msg in boot_msgs:
            self._append_tagged(msg + "\n", "system_msg")

        self._append_tagged("Simon", "simon_name")
        self._append_text(": Chào Chủ nhân! Tôi là Simon, hệ thống đã sẵn sàng phục vụ. ")
        self._append_text("Tôi có thể giúp gì cho bạn hôm nay?\n\n")

    # ==================================================================
    # Chat Display
    # ==================================================================

    def _append_text(self, text: str) -> None:
        """Append plain text to chat."""
        self.chat.configure(state="normal")
        self.chat.insert("end", text)
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def _append_tagged(self, text: str, tag: str) -> None:
        """Append text with a specific tag (color)."""
        self.chat.configure(state="normal")
        self.chat._textbox.insert("end", text, tag)
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def _append_timestamp(self) -> None:
        """Append a timestamp."""
        ts = datetime.datetime.now().strftime("%H:%M")
        self._append_tagged(f"[{ts}] ", "timestamp")

    def _show_user_message(self, text: str) -> None:
        """Display a user message in chat."""
        self._append_timestamp()
        self._append_tagged("Bạn", "user_name")
        self._append_text(f": {text}\n")

    def _show_simon_message(self, text: str) -> None:
        """Display a Simon message in chat."""
        self._append_timestamp()
        self._append_tagged("Simon", "simon_name")
        self._append_text(f": {text}\n\n")

    def _show_error(self, text: str) -> None:
        """Display an error message."""
        self._append_tagged(f"⚠ {text}\n", "error_msg")

    # ==================================================================
    # Event Handlers
    # ==================================================================

    def _on_send(self, event=None) -> None:
        """Handle send button click or Enter key."""
        text = self.entry.get().strip()
        if not text or self._is_thinking:
            return

        self.entry.delete(0, "end")
        self._show_user_message(text)
        self._set_thinking(True)

        threading.Thread(target=self._brain_ask, args=(text,), daemon=True).start()

    def _brain_ask(self, text: str) -> None:
        """Run brain.ask in background thread."""
        try:
            # Use streaming if possible
            try:
                full_reply = []
                for token in self.brain.ask_stream(text):
                    full_reply.append(token)
                    self._queue.put(("stream_token", token))
                self._queue.put(("stream_end", "".join(full_reply)))
            except Exception:
                # Fallback to non-streaming
                reply = self.brain.ask(text)
                self._queue.put(("reply", reply))
        except Exception as exc:
            self._queue.put(("error", str(exc)))

    def _drain_queue(self) -> None:
        """Process queued messages from background threads."""
        try:
            while True:
                kind, payload = self._queue.get_nowait()

                if kind == "stream_token":
                    if self._is_thinking:
                        # First token – show Simon label
                        self._set_thinking(False, update_status=False)
                        self._append_timestamp()
                        self._append_tagged("Simon", "simon_name")
                        self._append_text(": ")
                    self._append_text(payload)

                elif kind == "stream_end":
                    self._append_text("\n\n")
                    self._set_status("Sẵn sàng", COLORS["success"])
                    self._update_info_labels()
                    if self.voice_mode and payload:
                        threading.Thread(target=self._speak, args=(payload,), daemon=True).start()

                elif kind == "reply":
                    self._set_thinking(False)
                    self._show_simon_message(payload)
                    self._set_status("Sẵn sàng", COLORS["success"])
                    self._update_info_labels()
                    if self.voice_mode and payload:
                        threading.Thread(target=self._speak, args=(payload,), daemon=True).start()

                elif kind == "face_detected":
                    self._append_timestamp()
                    self._append_tagged("Simon (Vision)", "simon_name")
                    self._append_text(f": {payload}\n\n")
                    if self.voice_mode:
                        threading.Thread(target=self._speak, args=(payload,), daemon=True).start()

                elif kind == "voice_command":
                    if not self._is_thinking:
                        self._inject_command(payload)

                elif kind == "error":
                    self._set_thinking(False)
                    self._show_error(payload)
                    self._set_status("Lỗi", COLORS["error"])


        except queue.Empty:
            pass

        self.root.after(80, self._drain_queue)

    # ==================================================================
    # Voice
    # ==================================================================

    def _toggle_voice(self) -> None:
        """Toggle voice mode on/off."""
        self.voice_mode = not self.voice_mode
        if self.voice_mode:
            self.voice_btn.configure(
                text="🎤 Voice: BẬT",
                fg_color=COLORS["btn_primary"],
                border_color=COLORS["accent_dim"],
            )
            self._set_status("Voice mode BẬT (Đang lắng nghe mic...)", COLORS["accent"])
            self._start_voice_listener()
        else:
            self._stop_voice_listener()
            self.voice_btn.configure(
                text="🎤 Voice: TẮT",
                fg_color=COLORS["bg_card"],
                border_color=COLORS["border"],
            )
            self._set_status("Voice mode TẮT", COLORS["text_secondary"])

    def _start_voice_listener(self) -> None:
        """Start continuous speech-to-text listening thread."""
        self._voice_stop_event = threading.Event()
        self._voice_thread = threading.Thread(
            target=self._voice_listen_loop,
            daemon=True,
            name="simon-gui-voice",
        )
        self._voice_thread.start()

    def _stop_voice_listener(self) -> None:
        """Stop speech-to-text listening thread."""
        if hasattr(self, "_voice_stop_event") and self._voice_stop_event:
            self._voice_stop_event.set()
            self._voice_stop_event = None
            self._voice_thread = None

    def _voice_listen_loop(self) -> None:
        """Continuous background listening loop for GUI voice mode."""
        from simon.voice.stt import listen
        from simon.voice.tts import is_speaking

        while hasattr(self, "_voice_stop_event") and self._voice_stop_event and not self._voice_stop_event.is_set():
            if self._is_thinking or is_speaking():
                time.sleep(0.4)
                continue
            try:
                text = listen(
                    timeout=5,
                    phrase_time_limit=12,
                    language=self.brain.current_language,
                    calibrate=False,
                    calibration_duration=0.3,
                )
                if (
                    text
                    and hasattr(self, "_voice_stop_event")
                    and self._voice_stop_event
                    and not self._voice_stop_event.is_set()
                    and not is_speaking()
                ):
                    self._queue.put(("voice_command", text))
            except Exception:
                time.sleep(0.5)

    def _speak(self, text: str) -> None:
        """Speak text using TTS in background."""
        try:
            from simon.voice.tts import speak
            speak(text, language=self.brain.current_language)
        except Exception as exc:
            self._queue.put(("error", f"TTS error: {exc}"))

    # ==================================================================
    # Vision
    # ==================================================================

    def _toggle_vision(self) -> None:
        """Toggle face watcher vision mode on/off."""
        self.vision_mode = not self.vision_mode
        if self.vision_mode:
            try:
                from simon.vision.face_detection import FaceWatcher

                def on_face_detected():
                    greeting = "Chào mừng Chủ nhân đã quay trở lại làm việc!"
                    self._queue.put(("face_detected", greeting))

                self._face_watcher = FaceWatcher(
                    on_face_detected=on_face_detected,
                    camera_index=0,
                    cooldown=60.0,
                )
                self._face_watcher.start()
                self.vision_btn.configure(
                    text="👁️ Vision: BẬT",
                    fg_color=COLORS["btn_primary"],
                    border_color=COLORS["accent_dim"],
                )
                self._set_status("Vision mode BẬT (Đang quan sát)", COLORS["accent"])
            except Exception as exc:
                self.vision_mode = False
                self._show_error(f"Không thể bật Vision: {exc}")
        else:
            if self._face_watcher:
                self._face_watcher.stop()
                self._face_watcher = None
            self.vision_btn.configure(
                text="👁️ Vision: TẮT",
                fg_color=COLORS["bg_card"],
                border_color=COLORS["border"],
            )
            self._set_status("Vision mode TẮT", COLORS["text_secondary"])

    def _quick_face_check(self) -> None:
        """Quick action: check camera for face right now."""
        self._inject_command("Quét camera xem có ai trước máy tính không")

    # ==================================================================
    # Quick Actions
    # ==================================================================

    def _quick_system(self) -> None:
        """Quick action: check system info."""
        self._inject_command("Kiểm tra thông tin hệ thống")

    def _quick_weather(self) -> None:
        """Quick action: check weather."""
        self._inject_command("Thời tiết hôm nay tại Hồ Chí Minh")

    def _quick_screenshot(self) -> None:
        """Quick action: take screenshot."""
        self._inject_command("Chụp màn hình giúp tôi")

    def _clear_chat(self) -> None:
        """Clear the chat display."""
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self.brain.clear_history()
        self._show_boot_sequence()
        self._update_info_labels()

    def _on_close(self) -> None:
        """Clean shutdown when closing the window."""
        self._stop_voice_listener()
        if self._face_watcher:
            try:
                self._face_watcher.stop()
            except Exception:
                pass
        self.root.destroy()


    def _inject_command(self, cmd: str) -> None:
        """Inject a command as if the user typed it."""
        if self._is_thinking:
            return
        self._show_user_message(cmd)
        self._set_thinking(True)
        threading.Thread(target=self._brain_ask, args=(cmd,), daemon=True).start()

    # ==================================================================
    # Status & Animations
    # ==================================================================

    def _set_thinking(self, thinking: bool, update_status: bool = True) -> None:
        """Set thinking state and update UI."""
        self._is_thinking = thinking
        if thinking:
            self.send_btn.configure(state="disabled", text="⏳")
            if update_status:
                self._set_status("Đang suy nghĩ...", COLORS["warning"])
        else:
            self.send_btn.configure(state="normal", text="⚡ Gửi")

    def _set_status(self, text: str, color: str) -> None:
        """Update status bar text and color."""
        self.status_label.configure(text=text, text_color=color)
        self.status_dot.configure(text_color=color)

    def _update_info_labels(self) -> None:
        """Update the info labels in status bar."""
        self.history_label.configure(text=f"History: {self.brain.history_count}")
        self.lang_label.configure(
            text=f"Language: {'Tiếng Việt' if self.brain.current_language == 'vi' else 'English'}"
        )

    def _animate_status_dot(self) -> None:
        """Animate the status dot when thinking."""
        if self._is_thinking:
            self._thinking_dots = (self._thinking_dots + 1) % 4
            dots = "." * self._thinking_dots
            self.status_label.configure(text=f"Đang suy nghĩ{dots}")
            # Pulse arc reactor
            colors = [COLORS["accent"], COLORS["accent_glow"], COLORS["accent"], COLORS["accent_dim"]]
            self.arc_reactor.configure(text_color=colors[self._thinking_dots])

        self.root.after(400, self._animate_status_dot)

    # ==================================================================
    # Run
    # ==================================================================

    def run(self) -> None:
        """Start the GUI main loop."""
        self.root.mainloop()


def launch_gui(brain: SimonBrain) -> None:
    """Launch the Simon GUI."""
    app = SimonGUI(brain)
    app.run()
