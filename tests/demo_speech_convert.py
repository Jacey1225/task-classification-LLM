#!/usr/bin/env python3
"""
Demo script for testing SpeechConvert functionality.
This script demonstrates how to use the speech recognition functions,
including the new timeout-controlled version.
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from SpeechConvert.SpeechConvert import convert_speech, convert_speech_with_timeout, convert_speech_from_file


def demo_basic_speech_recognition():
    """Demo the basic speech recognition function."""
    print("=== Basic Speech Recognition Demo ===")
    print("This will listen indefinitely until you speak.")
    print("Press Ctrl+C to cancel.")
    
    try:
        input("Press Enter when ready to start listening...")
        result = convert_speech()
        print(f"Final result: '{result}'\n")
    except KeyboardInterrupt:
        print("\nCancelled by user.\n")


def demo_timeout_speech_recognition():
    """Demo the timeout-controlled speech recognition function."""
    print("=== Timeout-Controlled Speech Recognition Demo ===")
    print("This will listen for 5 seconds maximum.")
    print("Speak within the timeout period, or it will automatically stop.")
    
    try:
        input("Press Enter when ready to start listening...")
        result = convert_speech_with_timeout(timeout=5, phrase_timeout=3)
        print(f"Final result: '{result}'\n")
    except KeyboardInterrupt:
        print("\nCancelled by user.\n")


def demo_quick_speech_recognition():
    """Demo quick speech recognition with short timeout."""
    print("=== Quick Speech Recognition Demo ===")
    print("This will listen for only 2 seconds - speak quickly!")
    
    try:
        input("Press Enter when ready to start listening...")
        result = convert_speech_with_timeout(timeout=2, phrase_timeout=1)
        print(f"Final result: '{result}'\n")
    except KeyboardInterrupt:
        print("\nCancelled by user.\n")


def demo_file_speech_recognition():
    """Demo speech recognition from file."""
    print("=== File-based Speech Recognition Demo ===")
    print("This would convert speech from an audio file.")
    print("(Requires an actual audio file to test)")
    
    # Example usage (would require an actual audio file)
    audio_file_path = input("Enter path to audio file (or press Enter to skip): ").strip()
    
    if audio_file_path and os.path.exists(audio_file_path):
        try:
            result = convert_speech_from_file(audio_file_path)
            print(f"Final result: '{result}'\n")
        except Exception as e:
            print(f"Error processing file: {e}\n")
    else:
        print("No valid file provided, skipping file demo.\n")


def main():
    """Main demo function."""
    print("SpeechConvert Demo Script")
    print("=" * 30)
    print()
    
    while True:
        print("Choose a demo option:")
        print("1. Basic speech recognition (no timeout)")
        print("2. Timeout-controlled speech recognition (5 seconds)")
        print("3. Quick speech recognition (2 seconds)")
        print("4. File-based speech recognition")
        print("5. Exit")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        print()
        
        if choice == "1":
            demo_basic_speech_recognition()
        elif choice == "2":
            demo_timeout_speech_recognition()
        elif choice == "3":
            demo_quick_speech_recognition()
        elif choice == "4":
            demo_file_speech_recognition()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
