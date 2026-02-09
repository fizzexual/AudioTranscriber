import speech_recognition as sr
import time

print("=" * 60)
print("MICROPHONE TEST & TRANSCRIPTION")
print("=" * 60)

# Initialize recognizer
r = sr.Recognizer()

# List all microphones
print("\n1. Available Microphones:")
print("-" * 60)
try:
    mics = sr.Microphone.list_microphone_names()
    for i, mic in enumerate(mics):
        print(f"   [{i}] {mic}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test microphone
print("\n2. Testing Microphone...")
print("-" * 60)
try:
    with sr.Microphone() as source:
        print("   ✓ Microphone opened successfully")
        print("   Adjusting for ambient noise... (please be quiet)")
        r.adjust_for_ambient_noise(source, duration=2)
        print(f"   ✓ Energy threshold: {r.energy_threshold}")
        print(f"   ✓ Dynamic threshold: {r.dynamic_energy_threshold}")
        
        print("\n3. Recording Test (3 seconds)...")
        print("-" * 60)
        print("   SAY SOMETHING NOW!")
        audio = r.listen(source, timeout=5, phrase_time_limit=3)
        print(f"   ✓ Recorded {len(audio.frame_data)} bytes of audio")
        
        print("\n4. Transcription Test...")
        print("-" * 60)
        
        # Try Google
        try:
            print("   Trying Google Speech Recognition...")
            text = r.recognize_google(audio)
            print(f"   ✓ SUCCESS: '{text}'")
        except sr.UnknownValueError:
            print("   ✗ Google could not understand audio")
        except sr.RequestError as e:
            print(f"   ✗ Google API error: {e}")
        
        # Try Sphinx (offline)
        try:
            print("\n   Trying Sphinx (offline)...")
            text = r.recognize_sphinx(audio)
            print(f"   ✓ SUCCESS: '{text}'")
        except sr.UnknownValueError:
            print("   ✗ Sphinx could not understand audio")
        except Exception as e:
            print(f"   ✗ Sphinx not available: {e}")
            
except Exception as e:
    print(f"   ✗ ERROR: {e}")

print("\n" + "=" * 60)
print("CONTINUOUS LISTENING TEST")
print("=" * 60)
print("Speak continuously. Press Ctrl+C to stop.\n")

try:
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print(f"Energy threshold: {r.energy_threshold}")
        print("Ready! Start speaking...\n")
        
        while True:
            try:
                print("[Listening...]", end=" ", flush=True)
                audio = r.listen(source, timeout=None, phrase_time_limit=10)
                
                print("[Processing...]", end=" ", flush=True)
                text = r.recognize_google(audio)
                
                timestamp = time.strftime("%H:%M:%S")
                print(f"\n[{timestamp}] {text}\n")
                
            except sr.UnknownValueError:
                print("[?]")
            except sr.RequestError as e:
                print(f"\n[API Error: {e}]")
                break
            except KeyboardInterrupt:
                print("\n\nStopped by user.")
                break
                
except Exception as e:
    print(f"\nError: {e}")

print("\nTest complete!")
