import unittest
import unittest.mock as mock
import datetime
import sys
import os
import logging
from unittest.mock import patch, MagicMock

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from Calendar.add_to_calendar import authorize, add_event, get_calendar_events, logger
from googleapiclient.errors import HttpError

# Set up detailed logging for tests
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
test_logger = logging.getLogger(__name__)


class TestCalendarFunctions(unittest.TestCase):
    """Test cases for the Calendar module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        test_logger.info("Setting up test fixtures")
        
        self.mock_service = MagicMock()
        self.test_start_time = datetime.datetime(2025, 7, 1, 10, 0, 0)
        self.test_end_time = datetime.datetime(2025, 7, 1, 11, 0, 0)
        self.test_task_name = "Test Meeting"
        self.test_description = "This is a test meeting"
        self.test_location = "Conference Room A"
        
        # Mock event response
        self.mock_event_response = {
            'id': 'test_event_123',
            'htmlLink': 'https://calendar.google.com/event?eid=test_event_123',
            'summary': self.test_task_name,
            'start': {'dateTime': self.test_start_time.isoformat()},
            'end': {'dateTime': self.test_end_time.isoformat()}
        }
        
        test_logger.info("Test fixtures set up successfully")

    @patch.dict(os.environ, {'CALENDAR_KEY': '/path/to/credentials.json'}, clear=False)
    @patch('Calendar.add_to_calendar.os.path.exists')
    @patch('Calendar.add_to_calendar.Credentials.from_authorized_user_file')
    @patch('Calendar.add_to_calendar.build')
    def test_authorize_with_valid_credentials(self, mock_build, mock_from_file, mock_exists):
        """Test authorization with valid existing credentials."""
        test_logger.info("Testing authorization with valid credentials")
        
        # Mock valid credentials
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_from_file.return_value = mock_creds
        mock_exists.return_value = True
        
        # Mock service build
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Test the function
        result = authorize()
        
        # Assertions
        self.assertEqual(result, mock_service)
        mock_exists.assert_called_once_with('/path/to/credentials.json')
        mock_from_file.assert_called_once_with('/path/to/credentials.json', ['https://www.googleapis.com/auth/calendar'])
        mock_build.assert_called_once_with("calendar", "v3", credentials=mock_creds)
        
        test_logger.info("Valid credentials test passed")

    @patch.dict(os.environ, {'CALENDAR_KEY': ''}, clear=False)
    def test_authorize_no_calendar_key(self):
        """Test authorization when CALENDAR_KEY is not set."""
        test_logger.info("Testing authorization with missing CALENDAR_KEY")
        
        with self.assertRaises(ValueError) as context:
            authorize()
        
        self.assertIn("CALENDAR_KEY environment variable must be set", str(context.exception))
        test_logger.info("Missing CALENDAR_KEY test passed")

    @patch.dict(os.environ, {'CALENDAR_KEY': '/path/to/credentials.json'}, clear=False)
    @patch('Calendar.add_to_calendar.os.path.exists')
    @patch('Calendar.add_to_calendar.Credentials.from_authorized_user_file')
    @patch('Calendar.add_to_calendar.Request')
    @patch('Calendar.add_to_calendar.build')
    @patch('builtins.open', mock.mock_open())
    def test_authorize_refresh_expired_credentials(self, mock_build, mock_request, mock_from_file, mock_exists):
        """Test authorization with expired credentials that can be refreshed."""
        test_logger.info("Testing authorization with expired credentials")
        
        # Mock expired credentials with refresh token
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token"
        mock_from_file.return_value = mock_creds
        mock_exists.return_value = True
        
        # Mock successful refresh
        def refresh_side_effect(request):
            mock_creds.valid = True
        mock_creds.refresh.side_effect = refresh_side_effect
        
        # Mock service build
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Test the function
        result = authorize()
        
        # Assertions
        self.assertEqual(result, mock_service)
        mock_creds.refresh.assert_called_once()
        
        test_logger.info("Expired credentials refresh test passed")

    def test_add_event_success(self):
        """Test successful event creation."""
        test_logger.info("Testing successful event creation")
        
        # Mock successful API response
        self.mock_service.events.return_value.insert.return_value.execute.return_value = self.mock_event_response
        
        # Test the function
        result = add_event(
            self.mock_service,
            self.test_start_time,
            self.test_end_time,
            self.test_task_name,
            self.test_description,
            self.test_location
        )
        
        # Assertions
        self.assertEqual(result, self.mock_event_response)
        self.mock_service.events.assert_called_once()
        
        # Verify the event data structure
        call_args = self.mock_service.events.return_value.insert.call_args
        self.assertEqual(call_args[1]['calendarId'], 'primary')
        
        event_body = call_args[1]['body']
        self.assertEqual(event_body['summary'], self.test_task_name)
        self.assertEqual(event_body['description'], self.test_description)
        self.assertEqual(event_body['location'], self.test_location)
        
        test_logger.info("Successful event creation test passed")

    def test_add_event_empty_task_name(self):
        """Test event creation with empty task name."""
        test_logger.info("Testing event creation with empty task name")
        
        with self.assertRaises(ValueError) as context:
            add_event(
                self.mock_service,
                self.test_start_time,
                self.test_end_time,
                "",  # Empty task name
                self.test_description,
                self.test_location
            )
        
        self.assertIn("Task name is required", str(context.exception))
        test_logger.info("Empty task name test passed")

    def test_add_event_invalid_start_time(self):
        """Test event creation with invalid start time."""
        test_logger.info("Testing event creation with invalid start time")
        
        with self.assertRaises(ValueError) as context:
            add_event(
                self.mock_service,
                "invalid_datetime",  # Invalid type
                self.test_end_time,
                self.test_task_name
            )
        
        self.assertIn("start_time must be a datetime object", str(context.exception))
        test_logger.info("Invalid start time test passed")

    def test_add_event_end_before_start(self):
        """Test event creation with end time before start time."""
        test_logger.info("Testing event creation with end time before start time")
        
        with self.assertRaises(ValueError) as context:
            add_event(
                self.mock_service,
                self.test_end_time,    # End time as start
                self.test_start_time,  # Start time as end
                self.test_task_name
            )
        
        self.assertIn("End time must be after start time", str(context.exception))
        test_logger.info("End before start test passed")

    def test_add_event_http_error(self):
        """Test event creation with Google API HTTP error."""
        test_logger.info("Testing event creation with HTTP error")
        
        # Mock HTTP error
        mock_error = HttpError(
            resp=MagicMock(status=403),
            content=b'{"error": {"message": "Forbidden"}}'
        )
        self.mock_service.events.return_value.insert.return_value.execute.side_effect = mock_error
        
        with self.assertRaises(HttpError):
            add_event(
                self.mock_service,
                self.test_start_time,
                self.test_end_time,
                self.test_task_name
            )
        
        test_logger.info("HTTP error test passed")

    def test_get_calendar_events_success(self):
        """Test successful retrieval of calendar events."""
        test_logger.info("Testing successful calendar events retrieval")
        
        # Mock events response
        mock_events = [
            {'id': '1', 'summary': 'Event 1'},
            {'id': '2', 'summary': 'Event 2'}
        ]
        mock_response = {'items': mock_events}
        self.mock_service.events.return_value.list.return_value.execute.return_value = mock_response
        
        # Test the function
        result = get_calendar_events(self.mock_service, max_results=5)
        
        # Assertions
        self.assertEqual(result, mock_events)
        self.mock_service.events.return_value.list.assert_called_once()
        
        call_args = self.mock_service.events.return_value.list.call_args[1]
        self.assertEqual(call_args['maxResults'], 5)
        self.assertEqual(call_args['calendarId'], 'primary')
        
        test_logger.info("Calendar events retrieval test passed")

    def test_get_calendar_events_with_time_filter(self):
        """Test calendar events retrieval with time filtering."""
        test_logger.info("Testing calendar events retrieval with time filter")
        
        # Mock events response
        mock_events = [{'id': '1', 'summary': 'Filtered Event'}]
        mock_response = {'items': mock_events}
        self.mock_service.events.return_value.list.return_value.execute.return_value = mock_response
        
        # Test with time filters
        time_min = datetime.datetime(2025, 7, 1, 0, 0, 0)
        time_max = datetime.datetime(2025, 7, 31, 23, 59, 59)
        
        result = get_calendar_events(
            self.mock_service,
            time_min=time_min,
            time_max=time_max,
            max_results=10
        )
        
        # Assertions
        self.assertEqual(result, mock_events)
        
        call_args = self.mock_service.events.return_value.list.call_args[1]
        self.assertIn('timeMin', call_args)
        self.assertIn('timeMax', call_args)
        
        test_logger.info("Time filtered events retrieval test passed")

    def test_get_calendar_events_http_error(self):
        """Test calendar events retrieval with HTTP error."""
        test_logger.info("Testing calendar events retrieval with HTTP error")
        
        # Mock HTTP error
        mock_error = HttpError(
            resp=MagicMock(status=500),
            content=b'{"error": {"message": "Internal Server Error"}}'
        )
        self.mock_service.events.return_value.list.return_value.execute.side_effect = mock_error
        
        with self.assertRaises(HttpError):
            get_calendar_events(self.mock_service)
        
        test_logger.info("Calendar events HTTP error test passed")


class TestCalendarIntegration(unittest.TestCase):
    """Integration tests for Calendar module (requires actual Google Calendar setup)."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        test_logger.info("Setting up integration test fixtures")
        self.skip_integration = not self._credentials_available()
    
    def _credentials_available(self):
        """Check if Google Calendar credentials are available."""
        calendar_key = os.getenv("CALENDAR_KEY")
        return calendar_key and os.path.exists(calendar_key)
    
    @unittest.skipIf(True, "Integration test - requires Google Calendar credentials")
    def test_full_calendar_integration(self):
        """Full integration test for calendar functionality."""
        if self.skip_integration:
            self.skipTest("Google Calendar credentials not available")
        
        test_logger.info("Running full calendar integration test")
        
        try:
            # Test authorization
            service = authorize()
            test_logger.info("Authorization successful")
            
            # Test event creation
            start_time = datetime.datetime.now() + datetime.timedelta(hours=1)
            end_time = start_time + datetime.timedelta(hours=1)
            
            event = add_event(
                service,
                start_time,
                end_time,
                "Integration Test Event",
                "This is a test event created by the integration test",
                "Test Location"
            )
            
            test_logger.info(f"Event created: {event.get('id')}")
            
            # Test event retrieval
            events = get_calendar_events(service, max_results=5)
            test_logger.info(f"Retrieved {len(events)} events")
            
            self.assertIsInstance(event, dict)
            self.assertIn('id', event)
            self.assertIsInstance(events, list)
            
        except Exception as e:
            test_logger.error(f"Integration test failed: {e}")
            raise


if __name__ == '__main__':
    test_logger.info("Starting Calendar module tests")
    
    # Configure logging to show all levels during testing
    logging.getLogger('Calendar.add_to_calendar').setLevel(logging.DEBUG)
    
    # Run the tests
    unittest.main(verbosity=2)
