"""
Simon AI – Main Entry Point.
JARVIS-style personal AI assistant with full tool calling, persistent memory,
voice interaction, computer vision, and desktop GUI.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from simon.brain.openai_brain import SimonBrain
from simon.config_loader import get_brain, load_config, validate_config
from simon.hands.tools import TOOL_REGISTRY
from simon.memory.chroma_memory import get_memory
from simon.voice.stt import listen
from simon.voice.tts import speak

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

LOG_PATH = BASE_DIR / "simon.log"
LOGGER = logging.getLogger("simon")

LOGGER.setLevel(logging.INFO)

if not LOGGER.handlers:
    try:
        fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        LOGGER.addHandler(fh)
    except Exception:
        pass
    sh = logging.StreamHandler()
    sh.setLevel(logging.WARNING)
    LOGGER.addHandler(sh)


def build_log(title: str, content: str = "") -> None:
    LOGGER.info("BUILD_LOG: %s | %s", title, content.replace("\n", " ") if content else "-")


def print_banner(model: str, tools_count: int, memory_count: int, lang: str) -> None:
    """Display JARVIS-style startup banner."""
    print()
    print("=" * 60)
    print("      S I M O N   A I  //  J A R V I S   E D I T I O N")
    print("=" * 60)
    print(f" [*] Core Model      : {model}")
    print(f" [*] Tool Registry   : {tools_count} capabilities online")
    print(f" [*] Vector Memory   : {memory_count} entries indexed")
    print(f" [*] Speech Engine   : Edge-TTS + Pygame (Ready)")
    print(f" [*] Primary Lang    : {'Tiếng Việt' if lang == 'vi' else 'English'}")
    print(" [*] Status          : All systems nominal. Standing by.")
    print("=" * 60)
    print(" Lệnh nhanh: /help, /tools, /memory, /clear, /exit")
    print("=" * 60)
    print()


def create_brain() -> SimonBrain:
    """Initialize SimonBrain with tools and configurations."""
    cfg = load_config()
    client, model = get_brain()
    brain = SimonBrain(client=client, model=model)

    # Register all tools into Brain
    brain.register_tools(TOOL_REGISTRY)

    base_url = cfg.get("openai", {}).get("base_url", "https://api.openai.com/v1")
    build_log("Brain init", f"model={model} base={base_url} tools={len(TOOL_REGISTRY)}")
    _validate_api_key(client, base_url, model, cfg)
    return brain


def _validate_api_key(client, base_url: str, model: str, cfg: dict) -> None:
    openai_cfg = cfg.get("openai", {})
    api_key = openai_cfg.get("api_key", "")
    if not api_key or api_key == "YOUR_API_KEY":
        # Check if environment variable has it
        env_key = os.getenv("SIMON_OPENAI_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not env_key:
            print("[Simon] Cảnh báo: Chưa cấu hình API key trong file .env hoặc settings.yaml.")
            return

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Reply OK only."},
                {"role": "user", "content": "Ping"},
            ],
            max_tokens=2,
            timeout=15,
        )
        reply = (completion.choices[0].message.content or "").strip()
        LOGGER.info("API key validated successfully: reply='%s'", reply)
        build_log("API key validation", f"base={base_url} model={model} reply={reply}")
    except Exception as exc:
        print(f"[Simon] Lưu ý: Kiểm tra kết nối AI Core: {exc}")
        LOGGER.warning("API key validation failed: %s", exc)
        build_log("API key validation failed", str(exc))


def handle_internal_command(cmd: str, brain: SimonBrain) -> bool:
    """Handle CLI helper commands. Returns True if handled."""
    cmd = cmd.strip().lower()
    if cmd == "/help":
        print("\n--- Hướng dẫn sử dụng Simon AI ---")
        print(" /tools   : Liệt kê các công cụ Simon có thể tự động gọi")
        print(" /memory  : Xem các ghi nhớ gần đây trong bộ nhớ dài hạn")
        print(" /clear   : Xóa lịch sử hội thoại hiện tại")
        print(" /exit    : Thoát chương trình")
        print(" Bạn cũng có thể ra lệnh trực tiếp bằng tiếng Việt hoặc tiếng Anh:\n"
              " - 'Mở Chrome', 'Thời tiết Hà Nội hôm nay', 'Kiểm tra CPU máy tính'\n"
              " - 'Lưu vào bộ nhớ: Tôi thích uống cafe đá', 'Tôi thích uống gì?'\n")
        return True
    elif cmd == "/tools":
        print(f"\n--- Danh sách công cụ khả dụng ({len(TOOL_REGISTRY)}) ---")
        for name, (_, schema) in TOOL_REGISTRY.items():
            desc = schema["function"].get("description", "")
            print(f"  • {name:<26} : {desc}")
        print()
        return True
    elif cmd == "/memory":
        memory = get_memory()
        recent = memory.get_recent(n=5)
        print(f"\n--- Bộ nhớ Simon ({memory.count} mục) ---")
        if not recent:
            print("  (Chưa có dữ liệu bộ nhớ nào)")
        else:
            for idx, doc in enumerate(recent, 1):
                print(f"  [{idx}] {doc}")
        print()
        return True
    elif cmd == "/clear":
        brain.clear_history()
        print("\n[Simon] Đã làm mới lịch sử hội thoại.\n")
        return True
    return False


async def main_async(voice_mode: bool = False, brain: Optional[SimonBrain] = None) -> None:
    build_log("Main loop started", f"voice_mode={voice_mode}")
    cfg = load_config()
    if brain is None:
        brain = create_brain()
    memory = get_memory()

    # Optional Vision background watcher
    vision_watcher = None
    vision_cfg = cfg.get("vision", {})
    if vision_cfg.get("enabled", False):
        try:
            from simon.vision.face_detection import FaceWatcher

            def on_face_detected():
                greeting = "Chào mừng Chủ nhân đã quay trở lại làm việc."
                print(f"\n[Vision] Phát hiện Chủ nhân! {greeting}")
                if voice_mode:
                    speak(greeting, language=brain.current_language)

            cam_idx = vision_cfg.get("camera_index", 0)
            cooldown = vision_cfg.get("cooldown_seconds", 60)
            vision_watcher = FaceWatcher(
                camera_index=cam_idx,
                on_face_detected=on_face_detected,
                cooldown=cooldown,
            )
            vision_watcher.start()
            print("[Vision] Camera face watcher đã kích hoạt.")
        except Exception as exc:
            LOGGER.warning("Could not start vision watcher: %s", exc)

    print_banner(
        model=brain.model,
        tools_count=len(brain._tools),
        memory_count=memory.count,
        lang=brain.current_language,
    )

    if voice_mode:
        print("[Voice Mode] Hãy nói vào microphone... (Nói 'thoát' hoặc nhấn Ctrl+C để dừng)")

    try:
        while True:
            language = brain.current_language
            if voice_mode:
                print("\n[Đang lắng nghe...]")
                user_input = listen(language=language)
                if user_input:
                    print(f"Chủ nhân: {user_input}")
            else:
                prompt_text = "Chủ nhân: " if language == "vi" else "Sir: "
                try:
                    user_input = input(prompt_text).strip()
                except EOFError:
                    break

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit", "thoát", "/exit"}:
                farewell = "Tạm biệt Chủ nhân, chúc bạn một ngày hiệu quả." if language == "vi" else "Goodbye Sir. All systems powering down."
                print(f"Simon: {farewell}")
                if voice_mode:
                    speak(farewell, language=language)
                build_log("Main loop ended by user request")
                break

            if handle_internal_command(user_input, brain):
                continue

            try:
                # Ask brain with tool execution loop
                reply = brain.ask(user_input)
                print(f"Simon: {reply}\n")
                build_log("User input", user_input)
                build_log("Simon reply", reply)

                # Save to long term memory asynchronously in background
                try:
                    memory.add_conversation(user_input, reply)
                except Exception:
                    pass

                if voice_mode:
                    speak(reply, language=brain.current_language)
            except Exception as exc:
                LOGGER.exception("Brain request failed")
                build_log("Brain error", str(exc))
                print(f"[Simon Error]: {exc}")
    except KeyboardInterrupt:
        print("\n[Simon] Hệ thống đang dừng...")
        build_log("Main loop interrupted")
    finally:
        if vision_watcher:
            vision_watcher.stop()
        build_log("Main loop exit")


if __name__ == "__main__":
    mode = None
    args = sys.argv[1:]
    if "--gui" in args or "-g" in args:
        mode = "3"
    elif "--voice" in args or "-v" in args:
        mode = "2"
    elif "--terminal" in args or "--cli" in args or "-t" in args or "-c" in args:
        mode = "1"

    if not mode:
        print()
        print("┌──────────────────────────────────────────────┐")
        print("│         CHỌN PHƯƠNG THỨC KHỞI ĐỘNG           │")
        print("│  1: Giao diện dòng lệnh (Text Terminal)     │")
        print("│  2: Chế độ giọng nói (Voice Mode)            │")
        print("│  3: Giao diện đồ họa (JARVIS Desktop GUI)    │")
        print("└──────────────────────────────────────────────┘")
        try:
            mode = input("Lựa chọn (1/2/3) [mặc định 3]: ").strip()
        except Exception:
            mode = "3"

    if not mode:
        mode = "3"

    brain = create_brain()

    if mode == "3":
        try:
            from simon.gui.app import launch_gui
            launch_gui(brain)
        except Exception as exc:
            LOGGER.exception("GUI failed to start")
            print(f"Không thể khởi chạy GUI ({exc}), đang chuyển sang Terminal mode...")
            asyncio.run(main_async(voice_mode=False, brain=brain))
    elif mode == "2":
        asyncio.run(main_async(voice_mode=True, brain=brain))
    else:
        asyncio.run(main_async(voice_mode=False, brain=brain))

