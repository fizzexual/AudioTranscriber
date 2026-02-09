import pyaudio
import json
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import queue
import time
from vosk import Model, KaldiRecognizer

class AudioTranscriberVosk:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Audio-to-Text Transcriber (Offline)")
        self.root.geometry("900x700")
        
        self.is_listening = False
        self.text_queue = queue.Queue()
        self.selected_mic_index = None
        self.model = None
        
        # UI Setup
        self.setup_ui()
        
        # Load microphones
        self.load_microphones()
        
        # Load model
        self.load_model()
        
        # Start processing queue
        self.process_queue()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🎤 Automatic Audio Transcriber (Offline)", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Microphone selection frame
        mic_frame = tk.LabelFrame(self.root, text="Microphone Settings", 
                                 font=("Arial", 10, "bold"), padx=10, pady=10)
        mic_frame.pack(padx=20, pady=10, fill=tk.X)
        
        tk.Label(mic_frame, text="Select Microphone:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mic_combo = ttk.Combobox(mic_frame, width=50, state="readonly")
        self.mic_combo.grid(row=0, column=1, padx=10, pady=5)
        
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
        self.status_label = tk.Label(self.root, text="Status: Loading...",
                                     font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Text area
        text_frame = tk.Frame(self.root)
        text_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(text_frame, text="Transcribed Text:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD,
                                                   font=("Consolas", 11),
                                                   height=20)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Info
        info = tk.Label(self.root, 
                       text="Using Vosk offline speech recognition - No internet required!",
                       font=("Arial", 9), fg="green")
        info.pack(pady=5)
    
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
                self.text_area.insert(tk.END, f"Found {len(input_mics)} input microphone(s)\n")
                self.text_area.insert(tk.END, f"Selected: {input_mics[0][1]}\n\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load microphones: {e}")
    
    def load_model(self):
        """Load Vosk model"""
        self.text_area.insert(tk.END, "[Loading speech recognition model...]\n")
        self.text_area.insert(tk.END, "[This may take a moment on first run]\n\n")
        
        def load_thread():
            try:
                # Try to load model from current directory
                import os
                model_path = "vosk-model-small-en-us-0.15"
                
                if not os.path.exists(model_path):
                    self.text_queue.put(("text", "[Downloading model... Please wait]\n"))
                    self.text_queue.put(("text", "[This is a one-time download (~40MB)]\n\n"))
                    
                    import urllib.request
                    import zipfile
                    
                    url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
                    zip_path = "vosk-model.zip"
                    
                    self.text_queue.put(("text", "[Downloading...]\n"))
                    urllib.request.urlretrieve(url, zip_path)
                    
                    self.text_queue.put(("text", "[Extracting...]\n"))
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(".")
                    
                    os.remove(zip_path)
                    self.text_queue.put(("text", "[Download complete!]\n\n"))
                
                self.model = Model(model_path)
                self.text_queue.put(("text", "[Model loaded successfully!]\n"))
                self.text_queue.put(("text", "[Ready to transcribe]\n\n"))
                self.text_queue.put(("status", "Ready - Click Start Listening"))
                
            except Exception as e:
                self.text_queue.put(("error", f"Model load error: {e}"))
                self.text_queue.put(("text", f"\n[ERROR] {e}\n"))
                self.text_queue.put(("text", "[Install Vosk: pip install vosk]\n"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def start_listening(self):
        if self.model is None:
            messagebox.showwarning("Warning", "Model not loaded yet. Please wait.")
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
            stream = p.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=16000,
                          input=True,
                          input_device_index=self.selected_mic_index,
                          frames_per_buffer=8000)
            
            stream.start_stream()
            
            rec = KaldiRecognizer(self.model, 16000)
            rec.SetWords(True)
            
            self.text_queue.put(("text", "[Listening... Speak now!]\n\n"))
            
            while self.is_listening:
                data = stream.read(4000, exception_on_overflow=False)
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text', '')
                    
                    if text:
                        timestamp = time.strftime("%H:%M:%S")
                        self.text_queue.put(("text", f"[{timestamp}] {text}\n"))
                else:
                    # Partial result
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get('partial', '')
                    if partial_text:
                        self.text_queue.put(("status", f"🎤 {partial_text}..."))
            
            # Final result
            final = json.loads(rec.FinalResult())
            text = final.get('text', '')
            if text:
                timestamp = time.strftime("%H:%M:%S")
                self.text_queue.put(("text", f"[{timestamp}] {text}\n"))
            
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
                    self.status_label.config(text=f"Status: {msg}", fg="green")
                elif msg_type == "error":
                    self.status_label.config(text=msg, fg="red")
                    self.stop_listening()
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioTranscriberVosk(root)
    root.mainloop()
