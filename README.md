# Simon AI

Local AI assistant inspired by JARVIS, built with a 100% free/open-source stack.

- Brain: OpenAI-compatible API (OpenAI, Groq, OpenRouter, etc.)
- Voice: Edge-TTS + SpeechRecognition
- Control: PyAutoGUI / OS automation
- Memory: ChromaDB
- Vision: OpenCV face detection
- Smart Home: Home Assistant local API

## Quick start

1. Install dependencies: `pip install -r requirements.txt`
2. Configure secrets via `.env` or environment variables (recommended) or `config/settings.yaml`
3. Run: `python -m simon.main`

### Config precedence (highest wins)

1. Environment variables:
   - `SIMON_OPENAI_API_KEY`
   - `SIMON_OPENAI_BASE_URL`
   - `SIMON_OPENAI_MODEL`
2. `.env` file in project root
3. `config/settings.yaml`

Example `.env`:
```
SIMON_OPENAI_API_KEY=sk-...
SIMON_OPENAI_BASE_URL=https://api.groq.com/openai/v1
SIMON_OPENAI_MODEL=llama-3.3-70b-versatile
```
