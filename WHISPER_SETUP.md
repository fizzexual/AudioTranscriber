# Whisper AI Transcriber Setup

## ChatGPT-Level Accuracy (95%+)

This uses OpenAI's Whisper API - the same technology powering ChatGPT voice mode.

### Features
- ✅ 95%+ accuracy (same as ChatGPT voice)
- ✅ 99 languages including Bulgarian (bg)
- ✅ Auto language detection
- ✅ Handles accents, background noise, multiple speakers
- ✅ Real-time continuous transcription

### Installation

```bash
pip install openai pyaudio
```

Or double-click: `install_whisper.bat`

### Get API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign up / Log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

### Cost

- **$0.006 per minute** (~$0.36 per hour)
- Much cheaper than human transcription
- Pay only for what you use

### Usage

1. Run: `python audio_transcriber_whisper.py`
2. Paste your API key
3. Click "Set Key"
4. Select microphone
5. Choose language:
   - `auto` - Auto-detect (recommended)
   - `en` - English
   - `bg` - Bulgarian
   - `es` - Spanish
   - etc.
6. Click "Start Listening"

### Tips for Best Accuracy

- **Chunk Duration**: 
  - 3-5 seconds = faster response, good for conversations
  - 7-10 seconds = better accuracy for long sentences
  
- **Language Setting**:
  - Use `auto` for mixed languages
  - Set specific language (e.g., `bg`) for better accuracy in that language

- **Microphone**:
  - Use a good quality mic (HyperX, Trust USB)
  - Speak clearly at normal pace
  - Reduce background noise

### Supported Languages

English, Bulgarian, Spanish, French, German, Italian, Portuguese, Russian, 
Japanese, Chinese, Arabic, Turkish, Polish, Ukrainian, and 90+ more!

### Comparison

| Feature | Vosk (Free) | Google API | Whisper AI |
|---------|-------------|------------|------------|
| Accuracy | 70% | 85% | 95%+ |
| Bulgarian | ❌ | ✅ | ✅ |
| Offline | ✅ | ❌ | ❌ |
| Cost | Free | Free (limited) | $0.006/min |
| Quality | Basic | Good | ChatGPT-level |

### Troubleshooting

**"Invalid API key"**
- Make sure you copied the full key (starts with `sk-`)
- Check you have credits in your OpenAI account

**"Insufficient quota"**
- Add payment method at: https://platform.openai.com/account/billing
- New accounts get $5 free credit

**Slow transcription**
- Lower chunk duration to 3-4 seconds
- Check your internet connection

**Poor accuracy**
- Set specific language instead of `auto`
- Speak closer to microphone
- Reduce background noise
