import speech_recognition as sr
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import queue
import time

class AudioTranscriber:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Audio-to-Text Transcriber")
        self.root.geometry("800x600")
        
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Lower threshold for better detection
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Shorter pause detection
        self.text_queue = queue.Queue()
        
        # UI Setup
        self.setup_ui()
        
        # Test microphone on startup
        self.test_microphone()
        
        # Start processing queue
        self.process_queue()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🎤 Automatic Audio Transcriber", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
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
        self.status_label = tk.Label(self.root, text="Status: Idle",
                                     font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Language selection
        lang_frame = tk.Frame(self.root)
        lang_frame.pack(pady=5)
        
        tk.Label(lang_frame, text="Language:").pack(side=tk.LEFT, padx=5)
        self.language_var = tk.StringVar(value="en-US")
        language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var,
                                     values=["en-US", "es-ES", "fr-FR", "de-DE", 
                                            "it-IT", "pt-BR", "ru-RU", "ja-JP", 
                                            "zh-CN", "ar-SA"],
                                     state="readonly", width=15)
        language_combo.pack(side=tk.LEFT, padx=5)
        
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
                       text="Uses Google Speech Recognition API (requires internet)",
                       font=("Arial", 9), fg="gray")
        info.pack(pady=5)
    
    def start_listening(self):
        self.is_listening = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Listening...", fg="green")
        
        # Start listening thread
        thread = threading.Thread(target=self.listen_continuously, daemon=True)
        thread.start()
    
    def stop_listening(self):
        self.is_listening = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped", fg="red")
    
    def clear_text(self):
        self.text_area.delete(1.0, tk.END)
    
    def test_microphone(self):
        """Test if microphone is available"""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            self.text_queue.put(("text", f"[Found {len(mic_list)} microphone(s)]\n"))
            for i, name in enumerate(mic_list):
                self.text_queue.put(("text", f"  {i}: {name}\n"))
            self.text_queue.put(("text", "\n"))
        except Exception as e:
            self.text_queue.put(("error", f"Microphone test failed: {e}"))
    
    def listen_continuously(self):
        try:
            with sr.Microphone() as source:
                self.text_queue.put(("text", "[Adjusting for ambient noise... Please wait]\n"))
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.text_queue.put(("text", f"[Energy threshold set to: {self.recognizer.energy_threshold}]\n"))
                self.text_queue.put(("text", "[Ready! Start speaking...]\n\n"))
                
                while self.is_listening:
                    try:
                        self.text_queue.put(("status", "🎤 Listening..."))
                        
                        # Listen with shorter timeout
                        audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=15)
                        
                        self.text_queue.put(("status", "⚙️ Processing..."))
                        
                        # Try Google recognition
                        try:
                            text = self.recognizer.recognize_google(audio, language=self.language_var.get())
                            timestamp = time.strftime("%H:%M:%S")
                            self.text_queue.put(("text", f"[{timestamp}] {text}\n"))
                        except sr.UnknownValueError:
                            self.text_queue.put(("text", "[Could not understand]\n"))
                        except sr.RequestError as e:
                            self.text_queue.put(("error", f"API error: {e}"))
                            self.text_queue.put(("text", "\n[Trying offline recognition...]\n"))
                            # Try offline as fallback
                            try:
                                text = self.recognizer.recognize_sphinx(audio)
                                timestamp = time.strftime("%H:%M:%S")
                                self.text_queue.put(("text", f"[{timestamp}] {text}\n"))
                            except:
                                self.text_queue.put(("text", "[Offline recognition also failed]\n"))
                        
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        self.text_queue.put(("text", f"[Error: {e}]\n"))
                        
        except Exception as e:
            self.text_queue.put(("error", f"Microphone error: {e}"))
    
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
    app = AudioTranscriber(root)
    root.mainloop()
