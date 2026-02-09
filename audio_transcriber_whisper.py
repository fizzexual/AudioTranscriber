import pyaudio
import wave
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import queue
import time
import os
import tempfile
from openai import OpenAI

class AudioTranscriberWhisper:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Audio-to-Text Transcriber (Whisper AI)")
        self.root.geometry("900x750")
        
        self.is_listening = False
        self.text_queue = queue.Queue()
        self.selected_mic_index = None
        self.client = None
        
        # UI Setup
        self.setup_ui()
        
        # Load microphones
        self.load_microphones()
        
        # Start processing queue
        self.process_queue()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🎤 Whisper AI Transcriber (ChatGPT-Level)", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # API Key frame
        api_frame = tk.LabelFrame(self.root, text="OpenAI API Key", 
                                 font=("Arial", 10, "bold"), padx=10, pady=10)
        api_frame.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar()
        api_entry = tk.Entry(api_frame, textvariable=self.api_key_var, width=50, show="*")
        api_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Button(api_frame, text="Set Key", command=self.set_api_key,
                 bg="#4CAF50", fg="white").grid(row=0, column=2, padx=5)
        
        tk.Label(api_frame, text="Get your key at: https://platform.openai.com/api-keys",
                fg="blue", cursor="hand2").grid(row=1, column=0, columnspan=3, pady=5)
        
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
        tk.Label(mic_frame, text="seconds (shorter = faster response)").grid(row=2, column=2)
        
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
        self.status_label = tk.Label(self.root, text="Status: Enter API key to start",
                                     font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Text area
        text_frame = tk.Frame(self.root)
        text_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(text_frame, text="Transcribed Text:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD,
                                                   font=("Consolas", 11),
                                                   height=18)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Info
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)
        
        tk.Label(info_frame, text="✓ 95%+ accuracy  ✓ 99 languages  ✓ Same as ChatGPT voice",
                font=("Arial", 9, "bold"), fg="green").pack()
        tk.Label(info_frame, text="Cost: ~$0.006 per minute (~$0.36/hour)",
                font=("Arial", 8), fg="gray").pack()
    
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
    
    def set_api_key(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showwarning("Warning", "Please enter your OpenAI API key")
            return
        
        try:
            self.client = OpenAI(api_key=api_key)
            # Test the key
            self.client.models.list()
            self.status_label.config(text="Status: API key validated ✓", fg="green")
            self.text_area.insert(tk.END, "[API key set successfully!]\n")
            self.text_area.insert(tk.END, "[Ready to transcribe with Whisper AI]\n\n")
            messagebox.showinfo("Success", "API key validated! You can now start listening.")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid API key: {e}")
            self.status_label.config(text="Status: Invalid API key", fg="red")
    
    def start_listening(self):
        if self.client is None:
            messagebox.showwarning("Warning", "Please set your OpenAI API key first")
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
                
                # Create temp file and close it immediately to avoid locking issues on Windows
                temp_fd, temp_path = tempfile.mkstemp(suffix=".wav")
                os.close(temp_fd)  # Close the file descriptor immediately
                
                wf = wave.open(temp_path, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                # Transcribe with Whisper
                try:
                    with open(temp_path, 'rb') as audio_file:
                        language = self.language_var.get()
                        if language == "auto":
                            transcript = self.client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                response_format="text"
                            )
                        else:
                            transcript = self.client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                language=language,
                                response_format="text"
                            )
                    
                    text = transcript.strip()
                    
                    if text:
                        timestamp = time.strftime("%H:%M:%S")
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
                    if self.is_listening:
                        self.status_label.config(text=f"Status: {msg}", fg="green")
                elif msg_type == "error":
                    self.status_label.config(text=msg, fg="red")
                    self.stop_listening()
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioTranscriberWhisper(root)
    root.mainloop()
