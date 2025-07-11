#!/usr/bin/env python3
"""
Google Calendar Setup Diagnostic Tool
This script checks your current Google Calendar setup and helps identify issues.
"""

import os
import sys
import json
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Check if environment variables are properly set."""
    logger.info("🔍 Checking environment variables...")
    print("🔍 Checking environment variables...")
    
    # Load .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    print(f"📁 Looking for .env file at: {dotenv_path}")
    
    if os.path.exists(dotenv_path):
        print("✅ .env file found")
        dotenv.load_dotenv(dotenv_path)
    else:
        print("❌ .env file not found")
        print("💡 Create a .env file in your project root with:")
        print("   CALENDAR_KEY=/path/to/your/credentials.json")
        return False
    
    # Check CALENDAR_KEY
    calendar_key = os.getenv("CALENDAR_KEY")
    print(f"📋 CALENDAR_KEY = {calendar_key}")
    
    if not calendar_key:
        print("❌ CALENDAR_KEY environment variable not set")
        return False
    
    if calendar_key.endswith('.apps.googleusercontent.com'):
        print("❌ CALENDAR_KEY looks like a client ID, not a file path")
        print("💡 CALENDAR_KEY should point to your credentials.json file")
        print("   Example: CALENDAR_KEY=/Users/username/credentials.json")
        return False
    
    print("✅ CALENDAR_KEY environment variable is set")
    return True

def check_credentials_file():
    """Check if the credentials file exists and is valid."""
    logger.info("📄 Checking credentials file...")
    print("\n📄 Checking credentials file...")
    
    calendar_key = os.getenv("CALENDAR_KEY")
    if not calendar_key:
        print("❌ Cannot check file - CALENDAR_KEY not set")
        return False
    
    print(f"📁 Checking file: {calendar_key}")
    
    if not os.path.exists(calendar_key):
        print("❌ Credentials file does not exist")
        print("💡 Download credentials.json from Google Cloud Console:")
        print("   1. Go to console.cloud.google.com")
        print("   2. APIs & Services > Credentials")
        print("   3. Create OAuth 2.0 Client ID (Desktop app)")
        print("   4. Download the JSON file")
        return False
    
    print("✅ Credentials file exists")
    
    # Try to parse the JSON
    try:
        with open(calendar_key, 'r') as f:
            creds_data = json.load(f)
        
        print("✅ Credentials file is valid JSON")
        
        # Check if it looks like Google OAuth credentials
        if 'installed' in creds_data:
            print("✅ File appears to be Google OAuth credentials (Desktop app)")
            client_id = creds_data.get('installed', {}).get('client_id', 'Not found')
            print(f"📋 Client ID: {client_id[:20]}...")
            return True
        elif 'web' in creds_data:
            print("⚠️  File appears to be Google OAuth credentials (Web app)")
            client_id = creds_data.get('web', {}).get('client_id', 'Not found')
            print(f"📋 Client ID: {client_id[:20]}...")
            print("💡 NOTE: This is a 'web' application credential.")
            print("   For desktop apps, you should use 'Desktop application' type.")
            print("   However, this might still work for testing.")
            return True
        else:
            print("❌ File doesn't appear to be Google OAuth credentials")
            print("💡 Make sure you downloaded 'OAuth 2.0 Client ID' credentials")
            return False
            
    except json.JSONDecodeError:
        print("❌ Credentials file is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False

def check_python_packages():
    """Check if required Python packages are installed."""
    logger.info("📦 Checking Python packages...")
    print("\n📦 Checking required Python packages...")
    
    required_packages = [
        'google.auth',
        'google.auth.transport.requests',
        'google.oauth2.credentials',
        'google_auth_oauthlib.flow',
        'googleapiclient.discovery',
        'googleapiclient.errors',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n💡 Install missing packages with:")
        print("   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv")
        return False
    
    print("✅ All required packages are installed")
    return True

def test_basic_import():
    """Test if we can import our calendar module."""
    logger.info("🔧 Testing module import...")
    print("\n🔧 Testing calendar module import...")
    
    try:
        from Calendar.add_to_calendar import authorize, add_event, get_calendar_events
        print("✅ Calendar module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Cannot import calendar module: {e}")
        return False

def suggest_next_steps(checks_passed):
    """Suggest next steps based on diagnostic results."""
    print("\n" + "="*50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*50)
    
    if all(checks_passed):
        print("🎉 All checks passed! Your setup looks good.")
        print("\n🚀 Next steps:")
        print("   1. Run: python tests/real_calendar_integration.py")
        print("   2. This will create a real event in your Google Calendar")
        print("   3. Visit calendar.google.com to see the event")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n🔧 Common solutions:")
        if not checks_passed[0]:  # Environment variables
            print("   1. Create a .env file with CALENDAR_KEY=/path/to/credentials.json")
        if not checks_passed[1]:  # Credentials file
            print("   2. Download credentials.json from Google Cloud Console")
        if not checks_passed[2]:  # Python packages
            print("   3. Install required packages with pip")
        print("\n📖 See CALENDAR_SETUP.md for detailed instructions")

def main():
    """Run all diagnostic checks."""
    print("🩺 Google Calendar Setup Diagnostic Tool")
    print("="*50)
    
    # Load environment variables
    dotenv.load_dotenv()
    
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Credentials File", check_credentials_file),
        ("Python Packages", check_python_packages),
        ("Module Import", test_basic_import)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error during {name} check: {e}")
            results.append(False)
    
    suggest_next_steps(results)

if __name__ == "__main__":
    main()
