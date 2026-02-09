@echo off
echo Installing Local Whisper (Free, ChatGPT-level accuracy)...
echo This will download ~3GB model on first run
echo.
pip install openai-whisper pyaudio
echo.
echo Done! Now run: python audio_transcriber_whisper_local.py
pause
