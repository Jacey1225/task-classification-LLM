#!/usr/bin/env python3
"""
Speech Control Demo
This script demonstrates the terminal command controls for the speech listener.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from SpeechConvert.SpeechConvert import (
    start_listener, 
    pause_listener, 
    resume_listener, 
    stop_listener,
    get_listener_status,
    get_last_text,
    interactive_voice_control
)

def demo_programmatic_control():
    """Demo of programmatic control (not interactive)."""
    print("🎬 DEMO: Programmatic Speech Control")
    print("=" * 50)
    
    import time
    
    # Start listening
    print("1. Starting listener...")
    start_listener()
    
    # Let it run for a few seconds
    print("2. Listening for 5 seconds... Say something!")
    time.sleep(5)
    
    # Check status
    status = get_listener_status()
    last_text = get_last_text()
    print(f"3. Status: {status}")
    if last_text:
        print(f"   Last heard: '{last_text}'")
    
    # Pause it
    print("4. Pausing listener...")
    pause_listener()
    time.sleep(2)
    
    # Resume it
    print("5. Resuming listener...")
    resume_listener()
    time.sleep(3)
    
    # Stop it
    print("6. Stopping listener...")
    stop_listener()
    
    print("✅ Demo completed!")

def main():
    """Main demo function."""
    print("🎤 Speech Control Demo Options")
    print("=" * 40)
    print("1. Interactive mode (recommended)")
    print("2. Programmatic demo")
    print("3. Command line usage examples")
    
    choice = input("\nChoose an option (1-3): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting interactive mode...")
        interactive_voice_control()
        
    elif choice == "2":
        print("\n🎬 Running programmatic demo...")
        demo_programmatic_control()
        
    elif choice == "3":
        print("\n📖 COMMAND LINE USAGE EXAMPLES:")
        print("=" * 40)
        print("# Start the speech listener and keep it running:")
        print("python src/SpeechConvert/SpeechConvert.py start")
        print()
        print("# Start interactive mode:")
        print("python src/SpeechConvert/SpeechConvert.py interactive")
        print()
        print("# Or just run interactive mode (default):")
        print("python src/SpeechConvert/SpeechConvert.py")
        print()
        print("📝 INTERACTIVE MODE COMMANDS:")
        print("  start   - Start continuous listening")
        print("  pause   - Pause the listener")
        print("  resume  - Resume listening")
        print("  stop    - Stop completely")
        print("  status  - Check current status")
        print("  last    - Show last recognized text")
        print("  quit    - Exit program")
        print()
        print("🗣️ VOICE COMMANDS (while listening):")
        print("  Say 'stop listening' to stop via voice")
        print("  Say 'hello' for a greeting")
        print("  Say 'what time' to get current time")
        print("  Say 'calendar' to trigger calendar detection")
        
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
