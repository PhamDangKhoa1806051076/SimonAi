# Simon Build Log

## 2026-07-28
- Created project scaffold: folder structure, README, requirements, .gitignore
- Replaced Ollama with OpenAI-compatible API brain (`simon/brain/openai_brain.py`)
- Added config loader with `.env` and environment variable support
- Added main async loop with text and voice modes
- Added Edge-TTS and SpeechRecognition voice modules
- Added system control tools with PyAutoGUI, psutil and webbrowser
- Added ChromaDB memory and OpenCV face detection
- Added Home Assistant integration client
- Added wake-word detector module (`simon/voice/wake_word.py`)
- Added PyInstaller packaging with bundled config and frozen-path support
- Configured secret handling: `.env` preferred, `.env.example` provided, `.gitignore` covers `.env`
2026-07-29 20:39:07,069 | INFO | BUILD_LOG: Project scaffold | Folder structure, brain prompt, config loader
2026-07-29 20:39:07,070 | INFO | BUILD_LOG: GitHub remote | https://github.com/PhamDangKhoa1806051076/SimonAi.git
2026-07-29 20:39:07,070 | INFO | BUILD_LOG: Voice 2-way added | Edge-TTS + SpeechRecognition
2026-07-29 20:50:36,416 | INFO | BUILD_LOG: Project scaffold | Folder structure, brain prompt, config loader
2026-07-29 20:50:36,417 | INFO | BUILD_LOG: GitHub remote | https://github.com/PhamDangKhoa1806051076/SimonAi.git
2026-07-29 20:50:36,417 | INFO | BUILD_LOG: Voice 2-way added | Edge-TTS + SpeechRecognition
2026-07-29 20:52:06,531 | INFO | BUILD_LOG: Project scaffold | Folder structure, brain prompt, config loader
2026-07-29 20:52:06,531 | INFO | BUILD_LOG: GitHub remote | https://github.com/PhamDangKhoa1806051076/SimonAi.git
2026-07-29 20:52:06,531 | INFO | BUILD_LOG: Voice 2-way added | Edge-TTS + SpeechRecognition
2026-07-29 20:52:07,156 | INFO | BUILD_LOG: Brain init | model=llama-3.3-70b-versatile base=https://api.openai.com/v1
2026-07-29 20:52:07,157 | INFO | BUILD_LOG: Main loop started | voice_mode=False
2026-07-29 20:52:07,157 | INFO | BUILD_LOG: Main loop exit | -
2026-07-29 20:52:44,966 | INFO | BUILD_LOG: Project scaffold | Folder structure, brain prompt, config loader
2026-07-29 20:52:44,966 | INFO | BUILD_LOG: GitHub remote | https://github.com/PhamDangKhoa1806051076/SimonAi.git
2026-07-29 20:52:44,966 | INFO | BUILD_LOG: Voice 2-way added | Edge-TTS + SpeechRecognition
2026-07-29 20:52:45,282 | INFO | BUILD_LOG: Brain init | model=llama-3.3-70b-versatile base=https://api.openai.com/v1
2026-07-29 20:52:45,282 | INFO | BUILD_LOG: Main loop started | voice_mode=False
2026-07-29 20:52:45,283 | INFO | BUILD_LOG: Main loop exit | -
