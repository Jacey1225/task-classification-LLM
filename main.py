from src.Calendar.add_to_calendar import authorize, add_event, get_calendar_events
import src.SpeechConvert.SpeechConvert as SpeechConvert

def main():
    try:
        SpeechConvert.interactive_voice_control()
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure your microphone is set up correctly and try again.")


if __name__ == "__main__":
    main()