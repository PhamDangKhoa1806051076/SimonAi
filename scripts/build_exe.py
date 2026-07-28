import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ENTRY = str(HERE / "simon" / "main.py")
DIST = HERE / "dist"
BUILD = HERE / "build"
SPEC = HERE / "Simon.spec"

hidden_imports = [
    "simon",
    "simon.brain",
    "simon.voice",
    "simon.hands",
    "simon.memory",
    "simon.vision",
    "simon.smart_home",
    "edge_tts",
    "edge_tts.voice",
    "edge_tts.voices",
    "edge_tts.submaker",
    "edge_tts.warns",
    "chromadb",
    "chromadb.api",
    "chromadb.db",
    "chromadb.embedding",
    "cv2",
    "pyautogui",
    "psutil",
    "PIL",
    "PIL._tkinter_finder",
]

cmd = (
    [sys.executable, "-m", "PyInstaller"]
    + [
        "--name",
        "Simon",
        "--console",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--distpath",
        str(DIST),
        "--workpath",
        str(BUILD),
        "--specpath",
        str(HERE),
    ]
    + [f"--hidden-import={name}" for name in hidden_imports]
    + [ENTRY]
)

print("Running:", " ".join(cmd))
subprocess.check_call(cmd)
