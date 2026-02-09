import pyaudio
import wave
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import queue
import time
import os
import tempfile
import whisper
import torch

class AudioTranscriberWhisperLocal:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Audio-to-Text Transcriber (Whisper Local - FREE)")
        self.root.geometry("900x750")
        
        self.is_listening = False
        self.text_queue = queue.Queue()
        self.selected_mic_index = None
        self.model = None
        self.model_size = "base"  # Start with base model
        
        # UI Setup
        self.setup_ui()
        
        # Load microphones
        self.load_microphones()
        
        # Start processing queue
        self.process_queue()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🎤 Whisper AI Transcriber (FREE - Local)", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Model selection frame
        model_frame = tk.LabelFrame(self.root, text="Model Settings", 
                                   font=("Arial", 10, "bold"), padx=10, pady=10)
        model_frame.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(model_frame, text="Model Size:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var,
                                   values=["tiny", "base", "small", "medium", "large"],
                                   state="readonly", width=15)
        model_combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        self.model_info = tk.Label(model_frame, text="base: ~140MB, Good accuracy, Fast", fg="blue")
        self.model_info.grid(row=0, column=2, padx=10)
        
        model_combo.bind('<<ComboboxSelected>>', self.update_model_info)
        
        tk.Button(model_frame, text="Load Model", command=self.load_model,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=10)
        
        # Microphone selection frame
        mic_frame = tk.LabelFrame(self.root, text="Microphone Settings", 
                                 font=("Arial", 10, "bold"), padx=10, pady=10)
        mic_frame.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(mic_frame, text="Select Microphone:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mic_combo = ttk.Combobox(mic_frame, width=50, state="readonly")
        self.mic_combo.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(mic_frame, text="Language:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.language_var = tk.StringVar(value="auto")
        lang_combo = ttk.Combobox(mic_frame, textvariable=self.language_var,
                                 values=["auto", "en", "bg", "es", "fr", "de", "it", 
                                        "pt", "ru", "ja", "zh", "ar", "tr", "pl", "uk"],
                                 state="readonly", width=20)
        lang_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        tk.Label(mic_frame, text="Chunk Duration:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.chunk_var = tk.IntVar(value=5)
        chunk_scale = tk.Scale(mic_frame, from_=3, to=10, orient=tk.HORIZONTAL,
                              variable=self.chunk_var, length=200)
        chunk_scale.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        tk.Label(mic_frame, text="seconds").grid(row=2, column=2)
        
        # Control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        self.start_btn = tk.Button(control_frame, text="Start Listening",
                                   command=self.start_listening,
                                   bg="#4CAF50", fg="white",
                                   font=("Arial", 12), padx=20, pady=10)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="Stop Listening",
                                  command=self.stop_listening,
                                  bg="#f44336", fg="white",
                                  font=("Arial", 12), padx=20, pady=10,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(control_frame, text="Clear Text",
                             command=self.clear_text,
                             bg="#2196F3", fg="white",
                             font=("Arial", 12), padx=20, pady=10)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(self.root, text="Status: Click 'Load Model' to start",
                                     font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Text area
        text_frame = tk.Frame(self.root)
        text_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(text_frame, text="Transcribed Text:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD,
                                                   font=("Consolas", 11),
                                                   height=16)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Info
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)
        
        tk.Label(info_frame, text="✓ 100% FREE  ✓ Runs locally  ✓ 95%+ accuracy  ✓ Bulgarian support",
                font=("Arial", 9, "bold"), fg="green").pack()
        tk.Label(info_frame, text="GPU recommended for faster processing (CPU works but slower)",
                font=("Arial", 8), fg="gray").pack()
    
    def update_model_info(self, event=None):
        model_info = {
            "tiny": "tiny: ~40MB, Fast but less accurate",
            "base": "base: ~140MB, Good accuracy, Fast",
            "small": "small: ~460MB, Better accuracy, Medium speed",
            "medium": "medium: ~1.5GB, High accuracy, Slower",
            "large": "large: ~3GB, Best accuracy, Slowest"
        }
        self.model_info.config(text=model_info.get(self.model_var.get(), ""))
    
    def load_microphones(self):
        try:
            p = pyaudio.PyAudio()
            input_mics = []
            
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    name = info['name']
                    if any(keyword in name.lower() for keyword in ['microphone', 'input', 'capture', 'hyperx', 'trust', 'logitech']):
                        if 'output' not in name.lower() and 'speaker' not in name.lower():
                            input_mics.append((i, name))
            
            p.terminate()
            
            self.mic_combo['values'] = [f"[{i}] {name}" for i, name in input_mics]
            if input_mics:
                self.mic_combo.current(0)
                self.selected_mic_index = input_mics[0][0]
                self.text_area.insert(tk.END, f"Found {len(input_mics)} microphone(s)\n")
                self.text_area.insert(tk.END, f"Selected: {input_mics[0][1]}\n\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load microphones: {e}")
    
    def load_model(self):
        """Load Whisper model"""
        model_size = self.model_var.get()
        
        self.text_area.insert(tk.END, f"[Loading Whisper {model_size} model...]\n")
        self.text_area.insert(tk.END, "[First time will download the model]\n")
        self.status_label.config(text="Status: Loading model...", fg="orange")
        
        def load_thread():
            try:
                # Check if CUDA is available
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.text_queue.put(("text", f"[Using device: {device.upper()}]\n"))
                
                if device == "cpu":
                    self.text_queue.put(("text", "[Running on CPU - will be slower]\n"))
                else:
                    self.text_queue.put(("text", "[GPU detected - will be fast!]\n"))
                
                self.text_queue.put(("text", "[Downloading/Loading model...]\n"))
                self.model = whisper.load_model(model_size, device=device)
                
                self.text_queue.put(("text", f"[✓ Model loaded successfully!]\n"))
                self.text_queue.put(("text", "[Ready to transcribe]\n\n"))
                self.text_queue.put(("status", "Ready - Click Start Listening"))
                
            except Exception as e:
                self.text_queue.put(("error", f"Model load error: {e}"))
                self.text_queue.put(("text", f"\n[ERROR] {e}\n"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def start_listening(self):
        if self.model is None:
            messagebox.showwarning("Warning", "Please load the model first")
            return
        
        selection = self.mic_combo.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a microphone first")
            return
        
        self.selected_mic_index = int(selection.split(']')[0].replace('[', ''))
        
        self.is_listening = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.mic_combo.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Listening...", fg="green")
        
        thread = threading.Thread(target=self.listen_continuously, daemon=True)
        thread.start()
    
    def stop_listening(self):
        self.is_listening = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.mic_combo.config(state="readonly")
        self.status_label.config(text="Status: Stopped", fg="red")
    
    def clear_text(self):
        self.text_area.delete(1.0, tk.END)
    
    def listen_continuously(self):
        try:
            p = pyaudio.PyAudio()
            
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          input_device_index=self.selected_mic_index,
                          frames_per_buffer=CHUNK)
            
            self.text_queue.put(("text", "[Listening... Speak now!]\n\n"))
            
            while self.is_listening:
                frames = []
                chunk_duration = self.chunk_var.get()
                
                # Record for specified duration
                self.text_queue.put(("status", "🎤 Recording..."))
                
                for _ in range(0, int(RATE / CHUNK * chunk_duration)):
                    if not self.is_listening:
                        break
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                
                if not self.is_listening:
                    break
                
                # Save to temp file
                self.text_queue.put(("status", "⚙️ Transcribing..."))
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                    temp_path = temp_audio.name
                    wf = wave.open(temp_path, 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                
                # Transcribe with Whisper
                try:
                    language = self.language_var.get()
                    if language == "auto":
                        result = self.model.transcribe(temp_path, fp16=False)
                    else:
                        result = self.model.transcribe(temp_path, language=language, fp16=False)
                    
                    text = result["text"].strip()
                    detected_lang = result.get("language", "unknown")
                    
                    if text:
                        timestamp = time.strftime("%H:%M:%S")
                        if language == "auto":
                            self.text_queue.put(("text", f"[{timestamp}] [{detected_lang}] {text}\n"))
                        else:
                            self.text_queue.put(("text", f"[{timestamp}] {text}\n"))
                    
                except Exception as e:
                    self.text_queue.put(("text", f"[Transcription error: {e}]\n"))
                
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            self.text_queue.put(("error", f"Error: {e}"))
    
    def process_queue(self):
        try:
            while True:
                msg_type, msg = self.text_queue.get_nowait()
                
                if msg_type == "text":
                    self.text_area.insert(tk.END, msg)
                    self.text_area.see(tk.END)
                elif msg_type == "status":
                    if self.is_listening or "Loading" in msg or "Ready" in msg:
                        self.status_label.config(text=f"Status: {msg}", fg="green")
                elif msg_type == "error":
                    self.status_label.config(text=msg, fg="red")
                    self.stop_listening()
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioTranscriberWhisperLocal(root)
    root.mainloop()
