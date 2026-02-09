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
        self.root.geometry("900x700")
        
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        # FIXED: Set better thresholds
        self.recognizer.energy_threshold = 4000  # Much higher threshold
        self.recognizer.dynamic_energy_threshold = False  # Disable auto-adjustment
        self.recognizer.pause_threshold = 0.8
        self.text_queue = queue.Queue()
        self.selected_mic_index = None
        
        # UI Setup
        self.setup_ui()
        
        # Load microphones
        self.load_microphones()
        
        # Start processing queue
        self.process_queue()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🎤 Automatic Audio Transcriber", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Microphone selection frame
        mic_frame = tk.LabelFrame(self.root, text="Microphone Settings", 
                                 font=("Arial", 10, "bold"), padx=10, pady=10)
        mic_frame.pack(padx=20, pady=10, fill=tk.X)
        
        tk.Label(mic_frame, text="Select Microphone:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mic_combo = ttk.Combobox(mic_frame, width=50, state="readonly")
        self.mic_combo.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(mic_frame, text="Sensitivity:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sensitivity_var = tk.IntVar(value=4000)
        sensitivity_scale = tk.Scale(mic_frame, from_=300, to=8000, 
                                    orient=tk.HORIZONTAL, variable=self.sensitivity_var,
                                    length=300, command=self.update_sensitivity)
        sensitivity_scale.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        self.sensitivity_label = tk.Label(mic_frame, text="4000 (Lower = More Sensitive)")
        self.sensitivity_label.grid(row=1, column=2, padx=5)
        
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
        
        test_btn = tk.Button(control_frame, text="Test Mic",
                            command=self.test_mic,
                            bg="#FF9800", fg="white",
                            font=("Arial", 12), padx=20, pady=10)
        test_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(self.root, text="Status: Select a microphone and click Start",
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
                                                   height=15)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Info
        info = tk.Label(self.root, 
                       text="Tip: If not working, try different microphones or adjust sensitivity",
                       font=("Arial", 9), fg="gray")
        info.pack(pady=5)
    
    def load_microphones(self):
        try:
            mics = sr.Microphone.list_microphone_names()
            # Filter to only input devices (exclude outputs)
            input_mics = []
            for i, name in enumerate(mics):
                if any(keyword in name.lower() for keyword in ['microphone', 'input', 'capture', 'hyperx', 'trust', 'logitech']):
                    if 'output' not in name.lower() and 'speaker' not in name.lower():
                        input_mics.append((i, name))
            
            self.mic_combo['values'] = [f"[{i}] {name}" for i, name in input_mics]
            if input_mics:
                self.mic_combo.current(0)
                self.selected_mic_index = input_mics[0][0]
                self.text_area.insert(tk.END, f"Found {len(input_mics)} input microphone(s)\n")
                self.text_area.insert(tk.END, f"Selected: {input_mics[0][1]}\n\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load microphones: {e}")
    
    def update_sensitivity(self, value):
        self.recognizer.energy_threshold = int(float(value))
        self.sensitivity_label.config(text=f"{int(float(value))} (Lower = More Sensitive)")
    
    def test_mic(self):
        """Test the selected microphone"""
        if self.selected_mic_index is None:
            messagebox.showwarning("Warning", "Please select a microphone first")
            return
        
        self.text_area.insert(tk.END, "\n[TESTING MICROPHONE - Speak now for 3 seconds...]\n")
        self.status_label.config(text="Status: Testing... Speak now!", fg="orange")
        
        def test_thread():
            try:
                with sr.Microphone(device_index=self.selected_mic_index) as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    self.text_queue.put(("text", f"[Ambient noise level: {self.recognizer.energy_threshold:.2f}]\n"))
                    
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    self.text_queue.put(("text", f"[Recorded {len(audio.frame_data)} bytes]\n"))
                    
                    text = self.recognizer.recognize_google(audio, language=self.language_var.get())
                    self.text_queue.put(("text", f"[TEST SUCCESS] You said: '{text}'\n\n"))
                    self.text_queue.put(("status", "Test successful!"))
            except sr.WaitTimeoutError:
                self.text_queue.put(("text", "[TEST FAILED] No speech detected. Try:\n"))
                self.text_queue.put(("text", "  1. Speak louder\n"))
                self.text_queue.put(("text", "  2. Lower the sensitivity slider\n"))
                self.text_queue.put(("text", "  3. Select a different microphone\n\n"))
            except Exception as e:
                self.text_queue.put(("text", f"[TEST ERROR] {e}\n\n"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def start_listening(self):
        selection = self.mic_combo.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a microphone first")
            return
        
        # Extract index from selection
        self.selected_mic_index = int(selection.split(']')[0].replace('[', ''))
        
        self.is_listening = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.mic_combo.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Listening...", fg="green")
        
        # Start listening thread
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
            with sr.Microphone(device_index=self.selected_mic_index) as source:
                self.text_queue.put(("text", "[Adjusting for ambient noise...]\n"))
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.text_queue.put(("text", f"[Energy threshold: {self.recognizer.energy_threshold:.2f}]\n"))
                self.text_queue.put(("text", "[Ready! Start speaking...]\n\n"))
                
                while self.is_listening:
                    try:
                        self.text_queue.put(("status", "🎤 Listening..."))
                        
                        # Listen without timeout
                        audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=15)
                        
                        self.text_queue.put(("status", "⚙️ Processing..."))
                        
                        # Recognize
                        text = self.recognizer.recognize_google(audio, language=self.language_var.get())
                        timestamp = time.strftime("%H:%M:%S")
                        self.text_queue.put(("text", f"[{timestamp}] {text}\n"))
                        
                    except sr.UnknownValueError:
                        self.text_queue.put(("text", "[?]\n"))
                    except sr.RequestError as e:
                        self.text_queue.put(("text", f"[API Error: {e}]\n"))
                        break
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
                    if self.is_listening or "Test" in msg:
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
