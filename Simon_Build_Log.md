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
2026-07-29 20:57:28,789 | INFO | BUILD_LOG: Project scaffold | Folder structure, brain prompt, config loader
2026-07-29 20:57:28,790 | INFO | BUILD_LOG: GitHub remote | https://github.com/PhamDangKhoa1806051076/SimonAi.git
2026-07-29 20:57:28,790 | INFO | BUILD_LOG: Voice 2-way added | Edge-TTS + SpeechRecognition
2026-07-29 20:57:29,108 | INFO | BUILD_LOG: Brain init | model=llama-3.3-70b-versatile base=https://api.openai.com/v1
2026-07-29 20:57:29,108 | INFO | BUILD_LOG: Main loop started | voice_mode=True
2026-07-29 20:57:53,682 | INFO | BUILD_LOG: User input | Hey Simone
2026-07-29 20:57:53,682 | INFO | BUILD_LOG: Simon reply | Chủ nhân ơi! Tôi là Simon, trợ lý AI của cậu. Cậu cần gì hôm nay? Hãy cho tôi biết để tôi có thể giúp đỡ kịp thời nhé!
2026-07-29 20:57:53,683 | ERROR | Brain request failed
Traceback (most recent call last):
  File "D:\Project ca nhan\Simon\simon\main.py", line 75, in main_async
    speak(reply)
    ~~~~~^^^^^^^
  File "D:\Project ca nhan\Simon\simon\voice\tts.py", line 21, in speak
    asyncio.run(_synthesize_to_file(text, output_file))
    ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\asyncio\runners.py", line 192, in run
    raise RuntimeError(
        "asyncio.run() cannot be called from a running event loop")
RuntimeError: asyncio.run() cannot be called from a running event loop
2026-07-29 20:57:53,684 | INFO | BUILD_LOG: Brain error | asyncio.run() cannot be called from a running event loop
2026-07-29 20:58:00,475 | WARNING | Speech not understood
2026-07-29 20:58:19,140 | INFO | BUILD_LOG: User input | Bạn có thể giúp tôi mở lại YouTube không
2026-07-29 20:58:19,141 | INFO | BUILD_LOG: Simon reply | Chủ nhân ạ! Dĩ nhiên rồi, tôi có thể giúp Chủ nhân mở lại YouTube. Tuy nhiên, tôi là trợ lý ảo, không có khả năng truy cập trực tiếp vào thiết bị của Chủ nhân. Nếu Chủ nhân đang sử dụng thiết bị di động hoặc máy tính, Chủ nhân có thể thử các bước sau:  - Đối với thiết bị di động: Chủ nhân hãy kiểm tra xem ứng dụng YouTube đã được cài đặt trên thiết bị chưa, sau đó hãy mở ứng dụng YouTube. - Đối với máy tính: Chủ nhân hãy nhập địa chỉ website YouTube vào trình duyệt web và nhấn Enter.  Nếu Chủ nhân cần thêm hỗ trợ hoặc có vấn đề khác, hãy cho tôi biết ngay, tôi luôn sẵn sàng giúp đỡ!
2026-07-29 20:58:19,142 | ERROR | Brain request failed
Traceback (most recent call last):
  File "D:\Project ca nhan\Simon\simon\main.py", line 75, in main_async
    speak(reply)
    ~~~~~^^^^^^^
  File "D:\Project ca nhan\Simon\simon\voice\tts.py", line 21, in speak
    asyncio.run(_synthesize_to_file(text, output_file))
    ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\asyncio\runners.py", line 192, in run
    raise RuntimeError(
        "asyncio.run() cannot be called from a running event loop")
RuntimeError: asyncio.run() cannot be called from a running event loop
2026-07-29 20:58:19,145 | INFO | BUILD_LOG: Brain error | asyncio.run() cannot be called from a running event loop
2026-07-29 20:58:21,052 | WARNING | Speech not understood
2026-07-29 20:58:30,445 | INFO | BUILD_LOG: User input | giúp tôi kiểm tra xem
2026-07-29 20:58:30,446 | INFO | BUILD_LOG: Simon reply | Chủ nhân cần kiểm tra điều gì ạ? Hãy cho Simon biết để tôi có thể hỗ trợ chính xác và nhanh chóng!
2026-07-29 20:58:30,447 | ERROR | Brain request failed
Traceback (most recent call last):
  File "D:\Project ca nhan\Simon\simon\main.py", line 75, in main_async
    speak(reply)
    ~~~~~^^^^^^^
  File "D:\Project ca nhan\Simon\simon\voice\tts.py", line 21, in speak
    asyncio.run(_synthesize_to_file(text, output_file))
    ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\asyncio\runners.py", line 192, in run
    raise RuntimeError(
        "asyncio.run() cannot be called from a running event loop")
RuntimeError: asyncio.run() cannot be called from a running event loop
2026-07-29 20:58:30,450 | INFO | BUILD_LOG: Brain error | asyncio.run() cannot be called from a running event loop
2026-07-29 20:58:36,152 | WARNING | Speech not understood
2026-07-29 20:58:40,822 | INFO | BUILD_LOG: User input | Ngày mai có mưa
2026-07-29 20:58:40,822 | INFO | BUILD_LOG: Simon reply | Dường như dự báo thời tiết cho ngày mai không mấy thuận lợi, Chủ nhân ạ. Nếu có mưa, Chủ nhân nên chuẩn bị sẵn kế hoạch và trang bị cần thiết để không bị ảnh hưởng bởi thời tiết. Có điều gì khác mà Simon có thể giúp đỡ để Chủ nhân chuẩn bị cho ngày mai không ạ?
2026-07-29 20:58:40,823 | ERROR | Brain request failed
Traceback (most recent call last):
  File "D:\Project ca nhan\Simon\simon\main.py", line 75, in main_async
    speak(reply)
    ~~~~~^^^^^^^
  File "D:\Project ca nhan\Simon\simon\voice\tts.py", line 21, in speak
    asyncio.run(_synthesize_to_file(text, output_file))
    ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\asyncio\runners.py", line 192, in run
    raise RuntimeError(
        "asyncio.run() cannot be called from a running event loop")
RuntimeError: asyncio.run() cannot be called from a running event loop
2026-07-29 20:58:40,823 | INFO | BUILD_LOG: Brain error | asyncio.run() cannot be called from a running event loop
2026-07-29 20:58:49,507 | WARNING | Speech not understood
2026-07-29 20:59:06,654 | WARNING | Speech not understood
2026-07-29 20:59:11,155 | WARNING | Speech not understood
2026-07-29 20:59:26,181 | WARNING | Speech not understood
2026-07-29 20:59:29,892 | WARNING | Speech not understood
2026-07-29 20:59:33,981 | WARNING | Speech not understood
