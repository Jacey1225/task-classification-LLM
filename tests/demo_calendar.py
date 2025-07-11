#!/usr/bin/env python3
"""
Demo script for testing Google Calendar functionality.
This script demonstrates how to use the calendar functions with comprehensive logging.
"""

import sys
import os
import datetime
import logging

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from Calendar.add_to_calendar import authorize, add_event, get_calendar_events

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('calendar_demo.log')
    ]
)

demo_logger = logging.getLogger(__name__)


def demo_authorization():
    """Demo the Google Calendar authorization process."""
    demo_logger.info("=== DEMO: Google Calendar Authorization ===")
    
    try:
        demo_logger.info("Attempting to authorize with Google Calendar...")
        service = authorize()
        demo_logger.info("✅ Authorization successful!")
        return service
        
    except ValueError as e:
        demo_logger.error(f"❌ Configuration error: {e}")
        demo_logger.error("Make sure CALENDAR_KEY environment variable is set")
        return None
        
    except FileNotFoundError as e:
        demo_logger.error(f"❌ Credentials file not found: {e}")
        demo_logger.error("Make sure your Google Calendar credentials file exists")
        return None
        
    except Exception as e:
        demo_logger.error(f"❌ Authorization failed: {e}")
        return None


def demo_create_test_event(service):
    """Demo creating a test event."""
    demo_logger.info("=== DEMO: Creating Test Event ===")
    
    if not service:
        demo_logger.error("❌ Cannot create event - no valid service object")
        return None
    
    try:
        # Create test event for 1 hour from now
        now = datetime.datetime.now()
        start_time = now + datetime.timedelta(hours=1)
        end_time = start_time + datetime.timedelta(hours=1)
        
        demo_logger.info(f"Creating test event scheduled for: {start_time.strftime('%Y-%m-%d %H:%M')}")
        
        event = add_event(
            service=service,
            start_time=start_time,
            end_time=end_time,
            task_name="Calendar Demo Test Event",
            description="This is a test event created by the calendar demo script. You can safely delete this event.",
            location="Demo Location - Virtual"
        )
        
        demo_logger.info("✅ Test event created successfully!")
        demo_logger.info(f"Event ID: {event.get('id')}")
        demo_logger.info(f"Event Link: {event.get('htmlLink')}")
        
        return event
        
    except ValueError as e:
        demo_logger.error(f"❌ Invalid input for event creation: {e}")
        return None
        
    except Exception as e:
        demo_logger.error(f"❌ Failed to create event: {e}")
        return None


def demo_create_custom_event(service):
    """Demo creating a custom event with user input."""
    demo_logger.info("=== DEMO: Creating Custom Event ===")
    
    if not service:
        demo_logger.error("❌ Cannot create event - no valid service object")
        return None
    
    try:
        print("\n--- Create Your Own Calendar Event ---")
        
        # Get event details from user
        task_name = input("Enter event title: ").strip()
        if not task_name:
            demo_logger.warning("⚠️ No event title provided, using default")
            task_name = "Custom Demo Event"
        
        description = input("Enter event description (optional): ").strip()
        location = input("Enter event location (optional): ").strip()
        
        # Get date and time
        print("\nWhen should the event start?")
        date_str = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
        
        if not date_str:
            start_date = datetime.date.today()
            demo_logger.info(f"Using today's date: {start_date}")
        else:
            try:
                start_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                demo_logger.info(f"Using provided date: {start_date}")
            except ValueError:
                demo_logger.warning("⚠️ Invalid date format, using today")
                start_date = datetime.date.today()
        
        time_str = input("Enter start time (HH:MM) or press Enter for next hour: ").strip()
        
        if not time_str:
            start_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
            demo_logger.info(f"Using next hour: {start_time.strftime('%H:%M')}")
        else:
            try:
                time_obj = datetime.datetime.strptime(time_str, '%H:%M').time()
                start_time = datetime.datetime.combine(start_date, time_obj)
                demo_logger.info(f"Using provided time: {start_time}")
            except ValueError:
                demo_logger.warning("⚠️ Invalid time format, using next hour")
                start_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        
        duration_str = input("Enter duration in minutes (default: 60): ").strip()
        
        try:
            duration = int(duration_str) if duration_str else 60
            demo_logger.info(f"Event duration: {duration} minutes")
        except ValueError:
            demo_logger.warning("⚠️ Invalid duration, using 60 minutes")
            duration = 60
        
        end_time = start_time + datetime.timedelta(minutes=duration)
        
        demo_logger.info(f"Creating custom event: '{task_name}'")
        demo_logger.info(f"Start: {start_time}, End: {end_time}")
        
        event = add_event(
            service=service,
            start_time=start_time,
            end_time=end_time,
            task_name=task_name,
            description=description if description else None,
            location=location if location else None
        )
        
        demo_logger.info("✅ Custom event created successfully!")
        print(f"\n✅ Event '{task_name}' created!")
        print(f"📅 Date: {start_time.strftime('%Y-%m-%d')}")
        print(f"⏰ Time: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        print(f"🔗 Link: {event.get('htmlLink')}")
        
        return event
        
    except KeyboardInterrupt:
        demo_logger.info("❌ Custom event creation cancelled by user")
        print("\nEvent creation cancelled.")
        return None
        
    except Exception as e:
        demo_logger.error(f"❌ Failed to create custom event: {e}")
        return None


def demo_get_upcoming_events(service):
    """Demo retrieving upcoming calendar events."""
    demo_logger.info("=== DEMO: Retrieving Upcoming Events ===")
    
    if not service:
        demo_logger.error("❌ Cannot retrieve events - no valid service object")
        return None
    
    try:
        demo_logger.info("Fetching upcoming events from your calendar...")
        
        # Get events from now until 30 days from now
        now = datetime.datetime.now()
        future = now + datetime.timedelta(days=30)
        
        events = get_calendar_events(
            service=service,
            time_min=now,
            time_max=future,
            max_results=10
        )
        
        if not events:
            demo_logger.info("📅 No upcoming events found")
            print("No upcoming events found.")
            return []
        
        demo_logger.info(f"✅ Found {len(events)} upcoming events")
        print(f"\n📅 Found {len(events)} upcoming events:")
        print("-" * 50)
        
        for i, event in enumerate(events, 1):
            start = event.get('start', {})
            summary = event.get('summary', 'No Title')
            
            # Parse start time
            start_datetime = start.get('dateTime', start.get('date'))
            if start_datetime:
                try:
                    if 'T' in start_datetime:  # DateTime
                        start_dt = datetime.datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
                        time_str = start_dt.strftime('%Y-%m-%d %H:%M')
                    else:  # Date only
                        time_str = start_datetime
                except:
                    time_str = start_datetime
            else:
                time_str = "No time specified"
            
            print(f"{i}. {summary}")
            print(f"   📅 {time_str}")
            
            description = event.get('description')
            if description:
                print(f"   📝 {description[:100]}{'...' if len(description) > 100 else ''}")
            
            location = event.get('location')
            if location:
                print(f"   📍 {location}")
            
            print()
        
        return events
        
    except Exception as e:
        demo_logger.error(f"❌ Failed to retrieve events: {e}")
        return None


def demo_validate_environment():
    """Demo environment validation."""
    demo_logger.info("=== DEMO: Environment Validation ===")
    
    # Check environment variables
    calendar_key = os.getenv("CALENDAR_KEY")
    
    if not calendar_key:
        demo_logger.error("❌ CALENDAR_KEY environment variable not set")
        print("❌ Error: CALENDAR_KEY environment variable not set")
        print("Please set it to the path of your Google Calendar credentials file.")
        return False
    
    demo_logger.info(f"✅ CALENDAR_KEY is set: {calendar_key}")
    print(f"✅ CALENDAR_KEY is set: {calendar_key}")
    
    # Check if credentials file exists
    if not os.path.exists(calendar_key):
        demo_logger.error(f"❌ Credentials file not found: {calendar_key}")
        print(f"❌ Error: Credentials file not found: {calendar_key}")
        print("Please make sure the file exists and the path is correct.")
        return False
    
    demo_logger.info(f"✅ Credentials file found: {calendar_key}")
    print(f"✅ Credentials file found: {calendar_key}")
    
    return True


def main():
    """Main demo function."""
    demo_logger.info("🚀 Starting Google Calendar Demo Script")
    print("=" * 60)
    print("🗓️  Google Calendar Demo Script")
    print("=" * 60)
    
    # Validate environment
    if not demo_validate_environment():
        demo_logger.error("❌ Environment validation failed, exiting")
        return
    
    service = None
    
    while True:
        print("\nChoose a demo option:")
        print("1. Test authorization")
        print("2. Create a test event")
        print("3. Create a custom event")
        print("4. View upcoming events")
        print("5. Run all demos")
        print("6. Exit")
        print()
        
        choice = input("Enter your choice (1-6): ").strip()
        print()
        
        try:
            if choice == "1":
                service = demo_authorization()
                
            elif choice == "2":
                if not service:
                    print("⚠️ Please authorize first (option 1)")
                    continue
                demo_create_test_event(service)
                
            elif choice == "3":
                if not service:
                    print("⚠️ Please authorize first (option 1)")
                    continue
                demo_create_custom_event(service)
                
            elif choice == "4":
                if not service:
                    print("⚠️ Please authorize first (option 1)")
                    continue
                demo_get_upcoming_events(service)
                
            elif choice == "5":
                demo_logger.info("🔄 Running all demos")
                print("🔄 Running all demos...")
                
                service = demo_authorization()
                if service:
                    demo_create_test_event(service)
                    demo_get_upcoming_events(service)
                    print("✅ All demos completed!")
                else:
                    print("❌ Authorization failed, skipping other demos")
                
            elif choice == "6":
                demo_logger.info("👋 Demo script ended by user")
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            demo_logger.info("❌ Demo interrupted by user")
            print("\n❌ Demo interrupted.")
            break
            
        except Exception as e:
            demo_logger.error(f"❌ Unexpected error: {e}")
            print(f"❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
        sys.exit(0)
