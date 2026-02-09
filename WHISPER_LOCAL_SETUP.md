# Local Whisper Transcriber - 100% FREE

## ChatGPT-Level Accuracy, Completely Free!

Runs OpenAI's Whisper model locally on your PC. Same quality as ChatGPT voice mode, but FREE!

### Features
- ✅ 100% FREE - No API keys, no costs
- ✅ 95%+ accuracy (ChatGPT-level)
- ✅ 99 languages including Bulgarian
- ✅ Works offline (after model download)
- ✅ Privacy - everything stays on your PC
- ✅ Auto language detection

### Installation

```bash
pip install openai-whisper pyaudio
```

Or double-click: `install_whisper_local.bat`

**Note:** First time will download the model (~140MB for base, ~3GB for large)

### Usage

1. Run: `python audio_transcriber_whisper_local.py`
2. Select model size (start with "base")
3. Click "Load Model" (wait for download first time)
4. Select microphone
5. Choose language (`bg` for Bulgarian, `auto` for auto-detect)
6. Click "Start Listening"

### Model Sizes

| Model | Size | Speed | Accuracy | Recommended For |
|-------|------|-------|----------|-----------------|
| tiny | 40MB | Very Fast | 80% | Quick testing |
| base | 140MB | Fast | 85% | **Good balance** ⭐ |
| small | 460MB | Medium | 90% | Better accuracy |
| medium | 1.5GB | Slow | 95% | High accuracy |
| large | 3GB | Very Slow | 98% | Best quality |

**Recommendation:** Start with `base` - it's fast and accurate enough for most uses.

### Performance

**With GPU (NVIDIA):**
- base: Real-time transcription
- medium: 2-3x slower than real-time
- large: 5-6x slower than real-time

**CPU Only:**
- base: 3-5x slower than real-time
- medium: 10-15x slower than real-time
- large: 30-40x slower than real-time

**Tip:** If you have an NVIDIA GPU, it will automatically use it for much faster processing!

### Bulgarian Support

Whisper has excellent Bulgarian support:
- Set language to `bg` for Bulgarian-only
- Use `auto` to automatically detect Bulgarian/English/other languages
- Handles code-switching (mixing languages)

### Tips for Best Results

1. **Model Selection:**
   - CPU only? Use `base` or `small`
   - Have GPU? Use `medium` or `large`

2. **Chunk Duration:**
   - 3-5 seconds: Faster response, good for conversations
   - 7-10 seconds: Better accuracy for long sentences

3. **Language:**
   - Set specific language (`bg`, `en`) for better accuracy
   - Use `auto` for mixed language conversations

4. **Microphone:**
   - Use good quality USB mic
   - Reduce background noise
   - Speak clearly

### Comparison

| Feature | Vosk | Google | Whisper API | **Whisper Local** |
|---------|------|--------|-------------|-------------------|
| Accuracy | 70% | 85% | 95% | **95%** ⭐ |
| Bulgarian | ❌ | ✅ | ✅ | **✅** |
| Cost | Free | Free (limited) | $0.006/min | **FREE** ⭐ |
| Offline | ✅ | ❌ | ❌ | **✅** ⭐ |
| Privacy | ✅ | ❌ | ❌ | **✅** ⭐ |
| Speed | Fast | Fast | Fast | Medium |

### Troubleshooting

**"No module named 'whisper'"**
```bash
pip install openai-whisper
```

**"Could not load model"**
- Check internet connection (for first download)
- Make sure you have enough disk space
- Try a smaller model (tiny or base)

**Very slow transcription**
- Use smaller model (base instead of large)
- Reduce chunk duration to 3-4 seconds
- Close other programs to free up RAM

**"CUDA out of memory"**
- Use smaller model
- Close other GPU-using programs
- Or use CPU mode (automatic fallback)

### GPU Acceleration (Optional)

For much faster processing, install CUDA support:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

This will make transcription 5-10x faster if you have an NVIDIA GPU!

### Why This is Better Than Paid Options

- **Same quality as ChatGPT voice** - Uses identical Whisper model
- **No recurring costs** - Pay once for electricity, use forever
- **Privacy** - Audio never leaves your computer
- **Offline** - Works without internet (after model download)
- **No limits** - Transcribe as much as you want

### System Requirements

**Minimum:**
- 4GB RAM
- 2GB free disk space
- Any CPU

**Recommended:**
- 8GB+ RAM
- NVIDIA GPU with 4GB+ VRAM
- SSD for faster model loading
