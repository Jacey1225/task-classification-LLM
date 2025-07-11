import datetime
import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

dotenv.load_dotenv()
CALENDAR_KEY = os.getenv("CALENDAR_KEY")

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authorize():
    """
    Authorize and return a Google Calendar service object.
    
    Returns:
        Resource: Google Calendar service object
        
    Raises:
        FileNotFoundError: If credentials file is not found
        Exception: For other authentication errors
    """
    logger.info("Starting Google Calendar authorization process")
    
    if not CALENDAR_KEY:
        logger.error("CALENDAR_KEY environment variable not set")
        raise ValueError("CALENDAR_KEY environment variable must be set")
    
    logger.info(f"Using credentials file: {CALENDAR_KEY}")
    
    creds = None
    try:
        if os.path.exists(CALENDAR_KEY):
            logger.info("Loading existing credentials from file")
            creds = Credentials.from_authorized_user_file(CALENDAR_KEY, SCOPES)
        else:
            logger.warning(f"Credentials file not found: {CALENDAR_KEY}")
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        creds = None
    
    if not creds or not creds.valid:
        logger.info("Credentials are invalid or missing, need to authenticate")
        
        if creds and creds.expired and creds.refresh_token:
            logger.info("Attempting to refresh expired credentials")
            try:
                creds.refresh(Request())
                logger.info("Successfully refreshed credentials")
            except Exception as e:
                logger.error(f"Failed to refresh credentials: {e}")
                creds = None
        
        if not creds:
            logger.info("Starting OAuth flow for new credentials")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CALENDAR_KEY, SCOPES)
                creds = flow.run_local_server(port=8080)
                logger.info("OAuth flow completed successfully")
            except Exception as e:
                logger.error(f"OAuth flow failed: {e}")
                raise
        
        # Save the credentials for the next run
        try:
            with open(CALENDAR_KEY, "w") as token:
                token.write(creds.to_json())
            logger.info(f"Credentials saved to {CALENDAR_KEY}")
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            raise
    else:
        logger.info("Using existing valid credentials")

    try:
        service = build("calendar", "v3", credentials=creds)
        logger.info("Google Calendar service object created successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to build Calendar service: {e}")
        raise

def add_event(service, start_time, end_time, task_name, description=None, location=None):
    """
    Add an event to Google Calendar.
    
    Args:
        service: Google Calendar service object
        start_time (datetime): Event start time
        end_time (datetime): Event end time  
        task_name (str): Event title/summary
        description (str, optional): Event description
        location (str, optional): Event location
        
    Returns:
        dict: Created event details
        
    Raises:
        ValueError: For invalid input parameters
        HttpError: For Google API errors
    """
    logger.info(f"Creating calendar event: '{task_name}'")
    logger.info(f"Event details - Start: {start_time}, End: {end_time}")
    
    # Validate inputs
    if not task_name or not task_name.strip():
        logger.error("Task name is required and cannot be empty")
        raise ValueError("Task name is required")
    
    if not isinstance(start_time, datetime.datetime):
        logger.error(f"Invalid start_time type: {type(start_time)}")
        raise ValueError("start_time must be a datetime object")
        
    if not isinstance(end_time, datetime.datetime):
        logger.error(f"Invalid end_time type: {type(end_time)}")
        raise ValueError("end_time must be a datetime object")
    
    if end_time <= start_time:
        logger.error(f"End time ({end_time}) must be after start time ({start_time})")
        raise ValueError("End time must be after start time")
    
    if description:
        logger.info(f"Event description: {description}")
    if location:
        logger.info(f"Event location: {location}")
    
    event = {
        "summary": task_name.strip(),
        "description": description,
        "location": location,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "America/Los_Angeles",  
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "America/Los_Angeles",
        },
    }
    
    logger.info("Sending event creation request to Google Calendar API")
    
    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        event_id = created_event.get('id')
        event_link = created_event.get('htmlLink')
        
        logger.info(f"Event created successfully!")
        logger.info(f"Event ID: {event_id}")
        logger.info(f"Event link: {event_link}")
        
        return created_event
        
    except HttpError as error:
        logger.error(f"Google Calendar API error: {error}")
        raise
    except Exception as error:
        logger.error(f"Unexpected error creating event: {error}")
        raise


def get_calendar_events(service, time_min=None, time_max=None, max_results=10):
    """
    Get events from Google Calendar.
    
    Args:
        service: Google Calendar service object
        time_min (datetime, optional): Minimum time for events
        time_max (datetime, optional): Maximum time for events
        max_results (int): Maximum number of events to return
        
    Returns:
        list: List of calendar events
    """
    logger.info(f"Fetching calendar events (max: {max_results})")
    
    try:
        if time_min:
            time_min = time_min.isoformat() + 'Z'
            logger.info(f"Filtering events from: {time_min}")
        
        if time_max:
            time_max = time_max.isoformat() + 'Z'  
            logger.info(f"Filtering events until: {time_max}")
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        logger.info(f"Retrieved {len(events)} events")
        
        return events
        
    except HttpError as error:
        logger.error(f"Error fetching calendar events: {error}")
        raise
    except Exception as error:
        logger.error(f"Unexpected error fetching events: {error}")
        raise