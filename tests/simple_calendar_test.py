#!/usr/bin/env python3
"""
Simple test demo for Google Calendar functionality with comprehensive logging.
This script demonstrates the core calendar functions with detailed logging output.
"""

import sys
import os
import datetime
import logging
from unittest.mock import MagicMock, patch

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from Calendar.add_to_calendar import add_event, get_calendar_events

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('calendar_test_demo.log')
    ]
)

test_logger = logging.getLogger(__name__)


def test_add_event_with_detailed_logging():
    """Test the add_event function with comprehensive logging."""
    test_logger.info("🧪 TESTING: add_event function with detailed logging")
    
    # Create a mock service
    mock_service = MagicMock()
    
    # Set up test data
    start_time = datetime.datetime(2025, 7, 1, 14, 0, 0)  # 2:00 PM
    end_time = datetime.datetime(2025, 7, 1, 15, 30, 0)   # 3:30 PM
    task_name = "Team Standup Meeting"
    description = "Daily team standup to discuss progress and blockers"
    location = "Conference Room B"
    
    # Mock the API response
    mock_event_response = {
        'id': 'test_event_12345',
        'htmlLink': 'https://calendar.google.com/event?eid=test_event_12345',
        'summary': task_name,
        'start': {'dateTime': start_time.isoformat()},
        'end': {'dateTime': end_time.isoformat()},
        'description': description,
        'location': location
    }
    
    mock_service.events.return_value.insert.return_value.execute.return_value = mock_event_response
    
    test_logger.info("📋 Test Parameters:")
    test_logger.info(f"  📅 Start Time: {start_time}")
    test_logger.info(f"  📅 End Time: {end_time}")
    test_logger.info(f"  📝 Task Name: '{task_name}'")
    test_logger.info(f"  📄 Description: '{description}'")
    test_logger.info(f"  📍 Location: '{location}'")
    
    test_logger.info("🚀 Calling add_event function...")
    
    try:
        # Call the function
        result = add_event(
            service=mock_service,
            start_time=start_time,
            end_time=end_time,
            task_name=task_name,
            description=description,
            location=location
        )
        
        test_logger.info("✅ add_event function completed successfully")
        test_logger.info(f"📊 Returned event ID: {result.get('id')}")
        test_logger.info(f"🔗 Event link: {result.get('htmlLink')}")
        
        # Verify the service was called correctly
        test_logger.info("🔍 Verifying function behavior...")
        mock_service.events.assert_called_once()
        
        # Check the call arguments
        call_args = mock_service.events.return_value.insert.call_args
        test_logger.info(f"📞 API was called with calendar ID: {call_args[1]['calendarId']}")
        
        event_body = call_args[1]['body']
        test_logger.info("📋 Event body sent to API:")
        test_logger.info(f"  Summary: {event_body['summary']}")
        test_logger.info(f"  Description: {event_body['description']}")
        test_logger.info(f"  Location: {event_body['location']}")
        test_logger.info(f"  Start Time: {event_body['start']['dateTime']}")
        test_logger.info(f"  End Time: {event_body['end']['dateTime']}")
        test_logger.info(f"  Timezone: {event_body['start']['timeZone']}")
        
        # Validate the data
        assert event_body['summary'] == task_name, "Task name mismatch"
        assert event_body['description'] == description, "Description mismatch"
        assert event_body['location'] == location, "Location mismatch"
        
        test_logger.info("✅ All validations passed!")
        
        return result
        
    except Exception as e:
        test_logger.error(f"❌ Test failed with error: {e}")
        raise


def test_add_event_validation_with_logging():
    """Test input validation with detailed logging."""
    test_logger.info("🧪 TESTING: Input validation with detailed logging")
    
    mock_service = MagicMock()
    valid_start = datetime.datetime(2025, 7, 1, 10, 0, 0)
    valid_end = datetime.datetime(2025, 7, 1, 11, 0, 0)
    
    # Test 1: Empty task name
    test_logger.info("🔍 Test 1: Empty task name validation")
    try:
        add_event(mock_service, valid_start, valid_end, "")
        test_logger.error("❌ Expected ValueError for empty task name!")
    except ValueError as e:
        test_logger.info(f"✅ Correctly caught ValueError: {e}")
    
    # Test 2: Invalid start time type
    test_logger.info("🔍 Test 2: Invalid start time type validation")
    try:
        add_event(mock_service, "invalid_time", valid_end, "Test Event")
        test_logger.error("❌ Expected ValueError for invalid start time!")
    except ValueError as e:
        test_logger.info(f"✅ Correctly caught ValueError: {e}")
    
    # Test 3: End time before start time
    test_logger.info("🔍 Test 3: End time before start time validation")
    try:
        add_event(mock_service, valid_end, valid_start, "Test Event")  # Swapped times
        test_logger.error("❌ Expected ValueError for end time before start time!")
    except ValueError as e:
        test_logger.info(f"✅ Correctly caught ValueError: {e}")
    
    test_logger.info("✅ All validation tests passed!")


def test_get_calendar_events_with_logging():
    """Test get_calendar_events function with detailed logging."""
    test_logger.info("🧪 TESTING: get_calendar_events function with detailed logging")
    
    mock_service = MagicMock()
    
    # Mock events data
    mock_events = [
        {
            'id': 'event1',
            'summary': 'Morning Meeting',
            'start': {'dateTime': '2025-07-01T09:00:00-07:00'},
            'end': {'dateTime': '2025-07-01T10:00:00-07:00'}
        },
        {
            'id': 'event2', 
            'summary': 'Project Review',
            'start': {'dateTime': '2025-07-01T14:00:00-07:00'},
            'end': {'dateTime': '2025-07-01T15:30:00-07:00'}
        }
    ]
    
    mock_response = {'items': mock_events}
    mock_service.events.return_value.list.return_value.execute.return_value = mock_response
    
    test_logger.info("📋 Test Parameters:")
    test_logger.info("  📊 Max Results: 5")
    test_logger.info("  📅 Time Range: Current test")
    
    test_logger.info("🚀 Calling get_calendar_events function...")
    
    try:
        # Call the function
        result = get_calendar_events(mock_service, max_results=5)
        
        test_logger.info("✅ get_calendar_events function completed successfully")
        test_logger.info(f"📊 Retrieved {len(result)} events")
        
        # Log each event
        for i, event in enumerate(result, 1):
            test_logger.info(f"📅 Event {i}: {event['summary']} (ID: {event['id']})")
        
        # Verify the service was called correctly
        test_logger.info("🔍 Verifying function behavior...")
        mock_service.events.return_value.list.assert_called_once()
        
        call_args = mock_service.events.return_value.list.call_args[1]
        test_logger.info("📞 API was called with parameters:")
        test_logger.info(f"  Calendar ID: {call_args['calendarId']}")
        test_logger.info(f"  Max Results: {call_args['maxResults']}")
        test_logger.info(f"  Single Events: {call_args['singleEvents']}")
        test_logger.info(f"  Order By: {call_args['orderBy']}")
        
        assert len(result) == 2, "Expected 2 events"
        assert result[0]['summary'] == 'Morning Meeting', "First event mismatch"
        
        test_logger.info("✅ All validations passed!")
        
        return result
        
    except Exception as e:
        test_logger.error(f"❌ Test failed with error: {e}")
        raise


def test_time_filtering_with_logging():
    """Test calendar events with time filtering and detailed logging."""
    test_logger.info("🧪 TESTING: Calendar events with time filtering")
    
    mock_service = MagicMock()
    
    # Set up time range
    time_min = datetime.datetime(2025, 7, 1, 0, 0, 0)
    time_max = datetime.datetime(2025, 7, 31, 23, 59, 59)
    
    mock_events = [{'id': 'filtered_event', 'summary': 'Filtered Event'}]
    mock_response = {'items': mock_events}
    mock_service.events.return_value.list.return_value.execute.return_value = mock_response
    
    test_logger.info("📋 Test Parameters:")
    test_logger.info(f"  📅 Time Min: {time_min}")
    test_logger.info(f"  📅 Time Max: {time_max}")
    test_logger.info("  📊 Max Results: 10")
    
    test_logger.info("🚀 Calling get_calendar_events with time filtering...")
    
    try:
        result = get_calendar_events(
            service=mock_service,
            time_min=time_min,
            time_max=time_max,
            max_results=10
        )
        
        test_logger.info("✅ Time filtering test completed successfully")
        test_logger.info(f"📊 Retrieved {len(result)} filtered events")
        
        # Verify time parameters were included
        call_args = mock_service.events.return_value.list.call_args[1]
        test_logger.info("🔍 Verifying time filtering parameters:")
        test_logger.info(f"  Time Min in call: {call_args.get('timeMin')}")
        test_logger.info(f"  Time Max in call: {call_args.get('timeMax')}")
        
        assert 'timeMin' in call_args, "timeMin parameter missing"
        assert 'timeMax' in call_args, "timeMax parameter missing"
        
        test_logger.info("✅ Time filtering validation passed!")
        
        return result
        
    except Exception as e:
        test_logger.error(f"❌ Time filtering test failed: {e}")
        raise


def main():
    """Run all tests with comprehensive logging."""
    test_logger.info("🚀 Starting Google Calendar Function Tests")
    print("=" * 80)
    print("🗓️  Google Calendar Function Test Suite")
    print("=" * 80)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Basic event creation
    try:
        test_logger.info("\n" + "="*50)
        test_add_event_with_detailed_logging()
        tests_passed += 1
        print("✅ Test 1: Basic event creation - PASSED")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 1: Basic event creation - FAILED: {e}")
    
    # Test 2: Input validation
    try:
        test_logger.info("\n" + "="*50)
        test_add_event_validation_with_logging()
        tests_passed += 1
        print("✅ Test 2: Input validation - PASSED")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 2: Input validation - FAILED: {e}")
    
    # Test 3: Event retrieval
    try:
        test_logger.info("\n" + "="*50)
        test_get_calendar_events_with_logging()
        tests_passed += 1
        print("✅ Test 3: Event retrieval - PASSED")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 3: Event retrieval - FAILED: {e}")
    
    # Test 4: Time filtering
    try:
        test_logger.info("\n" + "="*50)
        test_time_filtering_with_logging()
        tests_passed += 1
        print("✅ Test 4: Time filtering - PASSED")
    except Exception as e:
        tests_failed += 1
        print(f"❌ Test 4: Time filtering - FAILED: {e}")
    
    # Summary
    test_logger.info("\n" + "="*50)
    test_logger.info("📊 TEST SUMMARY")
    test_logger.info(f"✅ Tests Passed: {tests_passed}")
    test_logger.info(f"❌ Tests Failed: {tests_failed}")
    test_logger.info(f"📊 Total Tests: {tests_passed + tests_failed}")
    
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print(f"✅ Tests Passed: {tests_passed}")
    print(f"❌ Tests Failed: {tests_failed}")
    print(f"📊 Total Tests: {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        test_logger.info("🎉 All tests passed! Calendar functions are working correctly.")
        print("🎉 All tests passed! Calendar functions are working correctly.")
    else:
        test_logger.warning(f"⚠️ {tests_failed} test(s) failed. Check the logs for details.")
        print(f"⚠️ {tests_failed} test(s) failed. Check the logs for details.")
    
    test_logger.info("📁 Detailed logs saved to: calendar_test_demo.log")
    print("📁 Detailed logs saved to: calendar_test_demo.log")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted by user")
        sys.exit(0)
