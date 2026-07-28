# Simon AI

Local AI assistant inspired by JARVIS, built with a 100% free/open-source stack.

- Brain: OpenAI-compatible API (OpenAI, Groq, OpenRouter, etc.)
- Voice: Edge-TTS + SpeechRecognition
- Control: PyAutoGUI / OS automation
- Memory: ChromaDB
- Vision: OpenCV face detection
- Smart Home: Home Assistant local API

## Quick start

1. Set API key and model in `config/settings.yaml`
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python -m simon.main`
