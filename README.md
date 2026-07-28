# Simon AI

Local AI assistant inspired by JARVIS, built with a 100% free/open-source stack.

- Brain: Ollama local model (e.g. qwen2.5:3b)
- Voice: Edge-TTS + SpeechRecognition
- Control: PyAutoGUI / OS automation
- Memory: ChromaDB
- Vision: OpenCV face detection
- Smart Home: Home Assistant local API

## Quick start

1. Install Ollama and pull model: `ollama pull qwen2.5:3b`
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python -m simon.main`
