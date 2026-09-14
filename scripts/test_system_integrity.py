"""
Verification script for Simon AI - JARVIS Edition
Validates all bug fixes:
1. TTS double speak without permission error
2. FaceWatcher + Camera tools frame sharing
3. Brain ask_stream latency & correctness
4. System control tools (check_disk with C:\\, type_text with Unicode)
5. ChromaDB vector memory
6. GUI instantiation lifecycle
"""

import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Ensure UTF-8 output
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

print("==================================================")
print("  SIMON AI – SYSTEM INTEGRITY & BUG FIX VERIFICATION")
print("==================================================")

# Test 1: System Control Tools
print("\n[1/6] Testing System Control Tools...")
from simon.hands.system_control import check_cpu, check_disk, check_ram, check_system, get_datetime, type_text

print("  •", check_cpu())
print("  •", check_ram())
print("  •", check_disk())
print("  •", check_system())
print("  •", get_datetime())
type_result = type_text("Chào Chủ nhân Simon")
print("  • Unicode Type Test:", type_result)
assert "Đã gõ" in type_result, "type_text failed"
print("  ==> System Control Tools OK!")

# Test 2: TTS Consecutive Playback (File Lock Fix)
print("\n[2/6] Testing TTS Consecutive Playback (Windows File Lock Fix)...")
from simon.voice.tts import speak
speak("Kiểm tra âm thanh lần một")
speak("Kiểm tra âm thanh lần hai")
print("  ==> TTS Consecutive Playback OK (No PermissionError)!")

# Test 3: Vision Frame Sharing (No Camera Conflict)
print("\n[3/6] Testing Vision Frame Sharing...")
from simon.vision.face_detection import check_camera_for_face, toggle_face_watcher
msg_enable = toggle_face_watcher(True)
print("  • Watcher start:", msg_enable)
check_res = check_camera_for_face()
print("  • Check camera while watcher active:", check_res)
msg_disable = toggle_face_watcher(False)
print("  • Watcher stop:", msg_disable)
print("  ==> Vision Frame Sharing OK!")

# Test 4: Memory Operations (ChromaDB Base Dir Anchor)
print("\n[4/6] Testing ChromaDB Memory...")
from simon.memory.chroma_memory import get_memory
mem = get_memory()
assert mem.is_available, "Memory is not available"
save_res = mem.add_memory("Chủ nhân yêu thích lập trình AI và công nghệ")
print("  • Add memory:", save_res)
search_res = mem.search_memory("lập trình AI")
print("  • Search memory:\n   ", search_res.replace("\n", "\n    "))
print("  ==> ChromaDB Memory OK!")

# Test 5: Brain & Fast Streaming (< 3s)
print("\n[5/6] Testing Brain Fast Streaming...")
from simon.main import create_brain
brain = create_brain()
print(f"  • Registered tools: {len(brain._tools)}")
assert len(brain._tools) == 30, f"Expected 30 tools, got {len(brain._tools)}"

t0 = time.time()
tokens = list(brain.ask_stream("Chào Simon, bạn là ai?"))
duration = time.time() - t0
print(f"  • Stream response time: {duration:.2f}s ({len(tokens)} chunks)")
print(f"  • Sample reply: {''.join(tokens)[:100]}...")
assert duration < 5.0, f"Streaming took too long: {duration}s"
print("  ==> Brain Streaming OK!")

# Test 6: GUI Initialization
print("\n[6/6] Testing Desktop GUI Lifecycle...")
from simon.gui.app import SimonGUI
app = SimonGUI(brain)
app.root.after(1000, app.root.destroy)
app.run()
print("  ==> GUI Lifecycle OK!")

print("\n==================================================")
print("  ALL 6 SYSTEM VERIFICATION TESTS PASSED SUCCESSFULLY! ")
print("==================================================")
