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
