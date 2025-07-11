from src.ConditionalRandomFields.CRF import Predict
import speech_recognition as sr
import threading
import time
import sys

recognizer = sr.Recognizer()

# Global control variables
is_listening = False
stop_listening = False
listener_thread = None
last_recognized_text = ""

def continuous_listen(): #MARK: Continuous listen
    """ 
    Continuously listen for speech in the background.
    This function runs in a separate thread.
    """
    global is_listening, stop_listening, last_recognized_text
    
    print("🎤 Starting continuous listening...")
    print("💡 Say something to test speech recognition")
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=3)
        print("✅ Microphone calibrated, ready to listen!")
    
    while not stop_listening:
        if is_listening:
            try:
                with sr.Microphone() as source:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=10)
                
                try:
                    text = recognizer.recognize_google(audio, language="en-US") #type: ignore
                    if text.strip():  
                        last_recognized_text = text
                        print(f"🗣️  Heard: '{text}'")
                        
                        predicter = Predict(text)
                        labels = predicter.predict()
                        processed_labels = predicter.process_labels(labels)
                        print(f"🔍 Processed labels: {processed_labels}")
                        
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"❌ Speech recognition error: {e}")
                    
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                print(f"❌ Unexpected error in continuous listen: {e}")
                
        else:
            time.sleep(0.1)

def start_listener(): #MARK: Start listener
    """Start the continuous speech listener in a background thread."""
    global is_listening, stop_listening, listener_thread
    
    if listener_thread and listener_thread.is_alive():
        print("⚠️  Listener is already running!")
        return False
    
    is_listening = True
    stop_listening = False
    
    # Start the listener in a separate thread
    listener_thread = threading.Thread(target=continuous_listen, daemon=True)
    listener_thread.start()
    
    print("🚀 Speech listener started!")
    print("💡 Commands:")
    print("   - Type 'pause' to pause listening")
    print("   - Type 'resume' to resume listening") 
    print("   - Type 'stop' to stop the listener")
    print("   - Type 'status' to check listener status")
    print("   - Say 'stop listening' to stop via voice")
    
    return True

def pause_listener(): #MARK: Pause listener
    """Pause the speech listener (keep thread running but stop processing)."""
    global is_listening
    
    if not listener_thread or not listener_thread.is_alive():
        print("❌ No listener thread is running!")
        return False
        
    is_listening = False
    print("⏸️  Speech listener paused")
    return True


def resume_listener(): #MARK: Resume listener
    """Resume the speech listener."""
    global is_listening
    
    if not listener_thread or not listener_thread.is_alive():
        print("❌ No listener thread is running! Use 'start' first.")
        return False
        
    is_listening = True
    print("▶️  Speech listener resumed")
    return True

 
def stop_listener(): #MARK: Stop listener
    """Stop the continuous speech listener completely."""
    global is_listening, stop_listening, listener_thread
    
    if not listener_thread or not listener_thread.is_alive():
        print("❌ No listener thread is running!")
        return False
    
    print("🛑 Stopping speech listener...")
    is_listening = False
    stop_listening = True
    
    # Wait for the thread to finish
    listener_thread.join(timeout=2)
    
    if listener_thread.is_alive():
        print("⚠️  Listener thread didn't stop gracefully")
    else:
        print("✅ Speech listener stopped")
    
    listener_thread = None
    return True


def get_listener_status(): #MARK: Get listener status
    """Get the current status of the speech listener."""
    global is_listening, stop_listening, listener_thread
    
    if not listener_thread or not listener_thread.is_alive():
        return "❌ Stopped"
    elif is_listening:
        return "🎤 Listening"
    else:
        return "⏸️  Paused"


def get_last_text(): #MARK: Get last text
    """Get the last recognized text."""
    global last_recognized_text
    return last_recognized_text


def interactive_voice_control(): #MARK: Interactive voice control
    """
    Interactive terminal interface for controlling the speech listener.
    Run this function to get a command prompt for voice control.
    """
    print("=" * 60)
    print("🎤 INTERACTIVE VOICE CONTROL TERMINAL")
    print("=" * 60)
    print("Available commands:")
    print("  start   - Start continuous speech listening")
    print("  pause   - Pause the listener")
    print("  resume  - Resume listening")
    print("  stop    - Stop the listener completely")
    print("  status  - Check listener status")
    print("  last    - Show last recognized text")
    print("  quit    - Exit the program")
    print("=" * 60)
    
    while True:
        try:
            # Show current status in prompt
            status = get_listener_status()
            command = input(f"\n[{status}] Enter command: ").strip().lower()
            
            if command == "start":
                start_listener()
                
            elif command == "pause":
                pause_listener()
                
            elif command == "resume":
                resume_listener()
                
            elif command == "stop":
                stop_listener()
                
            elif command == "status":
                status = get_listener_status()
                print(f"📊 Listener status: {status}")
                if last_recognized_text:
                    print(f"💬 Last heard: '{last_recognized_text}'")
                
            elif command == "last":
                if last_recognized_text:
                    print(f"💬 Last recognized text: '{last_recognized_text}'")
                else:
                    print("🔇 No text has been recognized yet")
                
            elif command in ["quit", "exit", "q"]:
                if listener_thread and listener_thread.is_alive():
                    print("🛑 Stopping listener before exit...")
                    stop_listener()
                print("👋 Goodbye!")
                break
                
            elif command == "help":
                print("\nAvailable commands:")
                print("  start, pause, resume, stop, status, last, quit")
                
            elif command == "":
                # Empty command, just show status
                continue
                
            else:
                print(f"❌ Unknown command: '{command}'")
                print("💡 Type 'help' to see available commands")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted! Stopping listener...")
            stop_listener()
            print("👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


# Command-line interface function
def main(): #MARK: Main function
    """Main function for command-line usage."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            start_listener()
            try:
                while listener_thread and listener_thread.is_alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")
                stop_listener()
                
        elif command == "interactive":
            interactive_voice_control()
            
        else:
            print("Usage:")
            print("  python SpeechConvert.py start       # Start listener")
            print("  python SpeechConvert.py interactive # Interactive mode")
    else:
        interactive_voice_control()


if __name__ == "__main__":
    main()

