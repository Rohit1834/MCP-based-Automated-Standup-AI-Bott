import os
from google_calendar_helper import GoogleCalendarHelper

def test_calendar():
    print("Testing Google Calendar connection...")
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ ERROR: credentials.json not found!")
        print("   Please download it from Google Cloud Console and place it in the project root")
        return
    
    print("✅ credentials.json found")
    
    try:
        # Try to initialize calendar
        calendar = GoogleCalendarHelper()
        print("✅ Calendar helper initialized")
        
        # Try to get events
        events = calendar.get_today_events()
        print(f"✅ Successfully fetched {len(events)} events")
        
        if events:
            print("\nToday's events:")
            for event in events:
                print(f"  - {event['summary']} at {event['start']}")
        else:
            print("\nNo events found for today")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calendar()