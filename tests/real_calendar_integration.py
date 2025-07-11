#!/usr/bin/env python3
"""
Real Google Calendar Integration Test
This script will actually connect to your Google Calendar and create real events
that you can see at calendar.google.com

WARNING: This will create REAL events in your Google Calendar!
Make sure you have proper credentials set up.
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
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('real_calendar_integration.log')
    ]
)

test_logger = logging.getLogger(__name__)


def create_real_test_event():
    """Create a real test event in your Google Calendar."""
    test_logger.info("🚀 CREATING REAL CALENDAR EVENT")
    print("=" * 60)
    print("🗓️  REAL GOOGLE CALENDAR INTEGRATION TEST")
    print("=" * 60)
    print("⚠️  WARNING: This will create a REAL event in your Google Calendar!")
    print()
    
    # Get user confirmation
    response = input("Do you want to proceed? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("❌ Operation cancelled by user")
        test_logger.info("Operation cancelled by user")
        return None
    
    try:
        # Step 1: Authorize with Google Calendar
        test_logger.info("🔐 Step 1: Authorizing with Google Calendar...")
        print("🔐 Step 1: Authorizing with Google Calendar...")
        
        service = authorize()
        test_logger.info("✅ Authorization successful!")
        print("✅ Authorization successful!")
        
        # Step 2: Create event details
        test_logger.info("📋 Step 2: Preparing event details...")
        print("📋 Step 2: Preparing event details...")
        
        # Create an event for tomorrow at 2:00 PM
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        end_time = start_time + datetime.timedelta(hours=1, minutes=30)
        
        event_details = {
            'task_name': 'TEST EVENT - Calendar Integration Test',
            'description': f'This is a test event created by the calendar integration test on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. You can safely delete this event.',
            'location': 'Test Location - Virtual Meeting',
            'start_time': start_time,
            'end_time': end_time
        }
        
        test_logger.info(f"📅 Event Name: {event_details['task_name']}")
        test_logger.info(f"📅 Start Time: {event_details['start_time']}")
        test_logger.info(f"📅 End Time: {event_details['end_time']}")
        test_logger.info(f"📄 Description: {event_details['description']}")
        test_logger.info(f"📍 Location: {event_details['location']}")
        
        print(f"📅 Event Name: {event_details['task_name']}")
        print(f"📅 Start Time: {event_details['start_time']}")
        print(f"📅 End Time: {event_details['end_time']}")
        print(f"📄 Description: {event_details['description']}")
        print(f"📍 Location: {event_details['location']}")
        print()
        
        # Step 3: Create the event
        test_logger.info("🎯 Step 3: Creating the calendar event...")
        print("🎯 Step 3: Creating the calendar event...")
        
        created_event = add_event(
            service=service,
            start_time=event_details['start_time'],
            end_time=event_details['end_time'],
            task_name=event_details['task_name'],
            description=event_details['description'],
            location=event_details['location']
        )
        
        # Step 4: Display results
        test_logger.info("✅ Step 4: Event created successfully!")
        print("✅ Step 4: Event created successfully!")
        print()
        
        event_id = created_event.get('id')
        event_link = created_event.get('htmlLink')
        
        test_logger.info(f"🆔 Event ID: {event_id}")
        test_logger.info(f"🔗 Event Link: {event_link}")
        
        print("📊 EVENT DETAILS:")
        print(f"🆔 Event ID: {event_id}")
        print(f"🔗 Event Link: {event_link}")
        print()
        print("🌐 You can now see this event at:")
        print("   📱 calendar.google.com")
        print("   📱 Google Calendar mobile app")
        print("   📱 Any device synced with your Google account")
        print()
        print(f"🕐 The event is scheduled for: {start_time.strftime('%A, %B %d, %Y at %I:%M %p')}")
        
        return created_event
        
    except Exception as e:
        test_logger.error(f"❌ Error creating real calendar event: {e}")
        print(f"❌ Error creating real calendar event: {e}")
        raise


def verify_event_in_calendar():
    """Verify the event exists by retrieving recent events."""
    test_logger.info("🔍 VERIFYING EVENT IN CALENDAR")
    print("\n" + "=" * 40)
    print("🔍 VERIFYING EVENT IN CALENDAR")
    print("=" * 40)
    
    try:
        # Authorize again
        service = authorize()
        
        # Get events from today onwards
        time_min = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        time_max = time_min + datetime.timedelta(days=7)  # Next 7 days
        
        test_logger.info(f"📅 Searching for events from {time_min} to {time_max}")
        print(f"📅 Searching for events from {time_min.strftime('%Y-%m-%d')} to {time_max.strftime('%Y-%m-%d')}")
        
        events = get_calendar_events(
            service=service,
            time_min=time_min,
            time_max=time_max,
            max_results=20
        )
        
        test_logger.info(f"📊 Found {len(events)} events in the next 7 days")
        print(f"📊 Found {len(events)} events in the next 7 days")
        print()
        
        # Look for our test event
        test_events = [event for event in events if 'TEST EVENT' in event.get('summary', '')]
        
        if test_events:
            test_logger.info(f"✅ Found {len(test_events)} test event(s):")
            print(f"✅ Found {len(test_events)} test event(s):")
            
            for i, event in enumerate(test_events, 1):
                event_start = event.get('start', {}).get('dateTime', 'No start time')
                test_logger.info(f"   {i}. {event.get('summary')} - {event_start}")
                print(f"   {i}. {event.get('summary')} - {event_start}")
        else:
            test_logger.warning("⚠️ No test events found")
            print("⚠️ No test events found")
        
        # Display all events for reference
        if events:
            print("\n📋 ALL UPCOMING EVENTS:")
            for i, event in enumerate(events, 1):
                summary = event.get('summary', 'No title')
                start_time = event.get('start', {}).get('dateTime', 'No start time')
                if start_time != 'No start time':
                    try:
                        # Parse the datetime string to make it more readable
                        dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        start_time = dt.strftime('%A, %B %d at %I:%M %p')
                    except:
                        pass
                
                print(f"   {i}. {summary} - {start_time}")
                test_logger.info(f"Event {i}: {summary} - {start_time}")
        
        return events
        
    except Exception as e:
        test_logger.error(f"❌ Error verifying events: {e}")
        print(f"❌ Error verifying events: {e}")
        raise


def cleanup_test_events():
    """Offer to clean up test events."""
    print("\n" + "=" * 40)
    print("🧹 CLEANUP TEST EVENTS")
    print("=" * 40)
    
    response = input("Do you want to delete the test events we created? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("🔒 Test events will remain in your calendar")
        test_logger.info("User chose to keep test events")
        return
    
    try:
        service = authorize()
        
        # Get recent events
        time_min = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        time_max = time_min + datetime.timedelta(days=7)
        
        events = get_calendar_events(service, time_min=time_min, time_max=time_max, max_results=50)
        test_events = [event for event in events if 'TEST EVENT' in event.get('summary', '')]
        
        if not test_events:
            print("❌ No test events found to delete")
            test_logger.info("No test events found for cleanup")
            return
        
        print(f"🗑️ Found {len(test_events)} test event(s) to delete:")
        
        for event in test_events:
            event_id = event.get('id')
            event_summary = event.get('summary')
            
            try:
                service.events().delete(calendarId='primary', eventId=event_id).execute()
                print(f"✅ Deleted: {event_summary}")
                test_logger.info(f"Deleted event: {event_summary} (ID: {event_id})")
            except Exception as e:
                print(f"❌ Failed to delete: {event_summary} - {e}")
                test_logger.error(f"Failed to delete event {event_summary}: {e}")
        
        print("🎉 Cleanup completed!")
        
    except Exception as e:
        test_logger.error(f"❌ Error during cleanup: {e}")
        print(f"❌ Error during cleanup: {e}")


def main():
    """Main function to run the real calendar integration test."""
    test_logger.info("🚀 Starting Real Google Calendar Integration Test")
    
    print("🌟 Welcome to the Real Google Calendar Integration Test!")
    print()
    print("This test will:")
    print("1. 🔐 Connect to your actual Google Calendar")
    print("2. 🎯 Create a real test event")
    print("3. 🔍 Verify the event was created")
    print("4. 🧹 Optionally clean up test events")
    print()
    print("You'll be able to see the created event at calendar.google.com")
    print()
    
    try:
        # Step 1: Create a real event
        created_event = create_real_test_event()
        
        if created_event:
            print("\n🎉 SUCCESS! The event has been created in your Google Calendar!")
            print("📱 Go to calendar.google.com to see your new event!")
            
            # Step 2: Verify the event
            print("\nWould you like to verify the event was created?")
            verify_response = input("Verify event? (yes/no): ").lower().strip()
            if verify_response in ['yes', 'y']:
                verify_event_in_calendar()
            
            # Step 3: Offer cleanup
            cleanup_test_events()
        
        print("\n✨ Test completed successfully!")
        test_logger.info("✨ Real calendar integration test completed successfully")
        
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        test_logger.info("Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        test_logger.error(f"Test failed: {e}")
        print("\n🔧 Make sure you have:")
        print("   1. Set up the CALENDAR_KEY environment variable")
        print("   2. Downloaded Google Calendar API credentials")
        print("   3. Enabled the Google Calendar API in Google Cloud Console")


if __name__ == "__main__":
    main()
