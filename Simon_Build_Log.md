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

## 2026-07-29
- Fixed broken `get_brain` import and duplicate `BASE_DIR` logic in `simon/main.py`
- Fixed Windows console UTF-8 output for Vietnamese text mode
- Fixed TTS `asyncio.run()` conflict when called from running event loop
- Added CustomTkinter desktop GUI with JARVIS-style dark theme (`simon/gui/app.py`)
- Integrated GUI mode into main launcher
- Added voice toggle and threaded brain/TTS execution in GUI
- Confirmed voice mode works with Groq API using Vietnamese replies
- Removed raw runtime log spam from build log

## 2026-07-29 update
- Added bilingual Vietnamese/English support in brain prompt
- Added language switching via voice/text ("switch to english", "chuyển sang tiếng Anh", etc.)
- Updated TTS to use English or Vietnamese voice based on current language
- Updated STT to listen with correct language setting
- Extended `SimonBrain.ask()` to manage and report current language
