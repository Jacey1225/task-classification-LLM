#!/usr/bin/env python3
"""
Quick Google Calendar Access Test
This script tests basic Google Calendar API access with detailed error reporting.
"""

import sys
import os
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_calendar_access():
    """Test basic Google Calendar API access."""
    print("🧪 Testing Google Calendar API Access")
    print("=" * 50)
    
    try:
        # Load environment
        dotenv.load_dotenv()
        
        # Import calendar functions
        from Calendar.add_to_calendar import authorize, get_calendar_events
        
        print("🔐 Step 1: Testing authorization...")
        logger.info("Attempting to authorize with Google Calendar")
        
        # Try to authorize
        service = authorize()
        print("✅ Authorization successful!")
        
        print("\n📅 Step 2: Testing calendar access...")
        logger.info("Attempting to fetch calendar events")
        
        # Try to get calendar events (this tests API access)
        events = get_calendar_events(service, max_results=5)
        print(f"✅ Successfully retrieved {len(events)} events from your calendar!")
        
        if events:
            print("\n📋 Your recent events:")
            for i, event in enumerate(events[:3], 1):
                summary = event.get('summary', 'No title')
                start = event.get('start', {}).get('dateTime', 'No start time')
                print(f"   {i}. {summary} - {start}")
        else:
            print("📅 No recent events found (this is normal for empty calendars)")
        
        print("\n🎉 SUCCESS! Your Google Calendar API access is working!")
        print("🚀 You can now run the full calendar integration test:")
        print("   python tests/real_calendar_integration.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Calendar access test failed: {e}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        
        if "access_denied" in error_str or "access blocked" in error_str:
            print("\n🔧 ACCESS BLOCKED - Follow these steps:")
            print("1. Go to console.cloud.google.com")
            print("2. Enable Google Calendar API")
            print("3. Configure OAuth consent screen")
            print("4. Add yourself as a test user")
            print("\n📖 See CALENDAR_ACCESS_FIX.md for detailed instructions")
            
        elif "file not found" in error_str or "no such file" in error_str:
            print("\n🔧 CREDENTIALS FILE ISSUE:")
            print("1. Check your .env file points to correct credentials.json")
            print("2. Make sure the credentials file exists")
            print("3. Run: python tests/calendar_setup_diagnostic.py")
            
        elif "redirect_uri_mismatch" in error_str:
            print("\n🔧 REDIRECT URI MISMATCH:")
            print("1. Use 'Desktop application' credentials instead of 'Web application'")
            print("2. Or add 'http://localhost' to authorized redirect URIs")
            
        elif "invalid_scope" in error_str or "insufficient_scope" in error_str:
            print("\n🔧 SCOPE ISSUE:")
            print("1. Add Calendar scope in OAuth consent screen")
            print("2. Delete any existing token files and re-authenticate")
            
        else:
            print(f"\n🔧 GENERAL ERROR: {e}")
            print("📖 See CALENDAR_ACCESS_FIX.md for troubleshooting steps")
        
        return False

def main():
    """Main function."""
    print("🌟 Google Calendar Access Verification Tool")
    print("This tool tests if your Google Calendar API setup is working correctly.\n")
    
    success = test_calendar_access()
    
    if success:
        print("\n✨ All tests passed! Your calendar integration is ready to use.")
    else:
        print("\n⚠️  Please fix the issues above and try again.")
        print("📖 Detailed setup instructions: CALENDAR_ACCESS_FIX.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
        sys.exit(0)
