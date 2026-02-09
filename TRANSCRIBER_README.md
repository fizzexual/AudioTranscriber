# Automatic Audio-to-Text Transcriber

Real-time speech-to-text transcription that continuously listens and converts speech to text.

## Features

- ✅ Continuous automatic transcription
- ✅ Real-time speech recognition
- ✅ Multiple language support
- ✅ Start/Stop controls
- ✅ Uses Google Speech Recognition API

## Quick Start

### Python Version (Recommended - Easiest)

```bash
# Install dependencies
pip install SpeechRecognition pyaudio

# Run
python audio_transcriber.py
```

**Note:** On Windows, if PyAudio fails to install:
```bash
pip install pipwin
pipwin install pyaudio
```

### Java Version

```bash
# Compile
javac AudioTranscriberApp.java

# Run
java AudioTranscriberApp
```

## How to Use

1. Click "Start Listening"
2. Speak into your microphone
3. Watch text appear automatically
4. Click "Stop Listening" when done
5. Select different languages from dropdown

## Supported Languages

- English (en-US)
- Spanish (es-ES)
- French (fr-FR)
- German (de-DE)
- Italian (it-IT)
- Portuguese (pt-BR)
- Russian (ru-RU)
- Japanese (ja-JP)
- Chinese (zh-CN)
- Arabic (ar-SA)

## Requirements

- Working microphone
- Internet connection (uses Google Speech API)
- Python 3.7+ or Java 11+

## Troubleshooting

**No microphone detected:**
- Check microphone permissions
- Ensure microphone is plugged in and set as default

**API errors:**
- Check internet connection
- Google API has rate limits (free tier)

**Poor recognition:**
- Speak clearly and at normal pace
- Reduce background noise
- Adjust microphone volume

## Advanced Usage

### Offline Recognition (Python)

For offline recognition, install:
```bash
pip install pocketsphinx
```

Then modify the code to use `recognize_sphinx()` instead of `recognize_google()`.

### Custom API Keys

The Java version uses a demo API key. For production, get your own key from:
https://cloud.google.com/speech-to-text

## Use Cases

- Meeting transcription
- Voice notes
- Accessibility tool
- Language learning
- Dictation software
- Interview recording
