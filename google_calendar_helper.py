import os
import pickle
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class GoogleCalendarHelper:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.creds = None
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Calendar"""
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError(
                        "credentials.json not found! Please download it from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('calendar', 'v3', credentials=self.creds)
        print("✅ Successfully authenticated with Google Calendar")
    
    def get_today_events(self):
        """Get today's calendar events"""
        # Get start and end of today in UTC
        today = datetime.now().date()
        start_time = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
        end_time = datetime.combine(today, datetime.max.time()).isoformat() + 'Z'
        
        try:
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId='primary',  # This will use rohitobrai11@gmail.com's calendar
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                print('No events found for today.')
                return []
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                # Parse the start time
                if 'T' in start:  # It's a datetime
                    event_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                else:  # It's an all-day event
                    event_time = datetime.fromisoformat(start)
                
                formatted_events.append({
                    'summary': event.get('summary', 'No title'),
                    'start': event_time.isoformat(),
                    'attendees': len(event.get('attendees', [])),
                    'location': event.get('location', ''),
                    'description': event.get('description', ''),
                    'meeting_link': self._extract_meeting_link(event)
                })
            
            print(f"📅 Found {len(formatted_events)} events for today")
            return formatted_events
            
        except Exception as error:
            print(f'❌ An error occurred: {error}')
            return []
    
    def _extract_meeting_link(self, event):
        """Extract meeting link from event"""
        # Check for Google Meet link
        if 'conferenceData' in event and 'entryPoints' in event['conferenceData']:
            for entry in event['conferenceData']['entryPoints']:
                if entry['entryPointType'] == 'video':
                    return entry['uri']
        
        # Check in description for Zoom or other links
        description = event.get('description', '')
        if 'zoom.us' in description or 'meet.google.com' in description:
            # Simple extraction - you might want to use regex for better extraction
            import re
            urls = re.findall(r'https?://[^\s]+', description)
            for url in urls:
                if 'zoom.us' in url or 'meet.google.com' in url:
                    return url
        
        return None