import json
from datetime import datetime, timedelta
from typing import List, Dict
from mcp.server import Server
from mcp.types import Tool
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os

class GoogleCalendarMCPServer:
    def __init__(self):
        self.server = Server("gcal-server")
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.creds = None
        self.setup_auth()
        self.register_tools()
    
    def setup_auth(self):
        """Setup Google Calendar authentication"""
        # Token file stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Note: You'll need to create credentials at Google Cloud Console
                # For free tier, use OAuth 2.0 Client ID
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
    
    def register_tools(self):
        """Register MCP tools for calendar"""
        
        @self.server.tool()
        async def get_today_events() -> str:
            """Get today's calendar events"""
            service = build('calendar', 'v3', credentials=self.creds)
            
            # Get today's events
            today = datetime.utcnow().date()
            start_time = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
            end_time = datetime.combine(today, datetime.max.time()).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'summary': event.get('summary', 'No title'),
                    'start': start,
                    'attendees': len(event.get('attendees', [])),
                    'description': event.get('description', '')
                })
            
            return json.dumps(formatted_events)
        
        @self.server.tool()
        async def get_upcoming_important_events() -> str:
            """Get important upcoming events for the week"""
            service = build('calendar', 'v3', credentials=self.creds)
            
            # Get events for next 7 days
            now = datetime.utcnow()
            start_time = now.isoformat() + 'Z'
            end_time = (now + timedelta(days=7)).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Filter for important events (more than 2 attendees or has "important" in title)
            important_events = []
            for event in events:
                if (len(event.get('attendees', [])) > 2 or 
                    'important' in event.get('summary', '').lower() or
                    'demo' in event.get('summary', '').lower() or
                    'sprint' in event.get('summary', '').lower()):
                    important_events.append({
                        'summary': event.get('summary'),
                        'start': event['start'].get('dateTime', event['start'].get('date')),
                        'attendees': len(event.get('attendees', []))
                    })
            
            return json.dumps(important_events[:5])  # Return top 5
    
    def run(self):
        self.server.run()

if __name__ == "__main__":
    server = GoogleCalendarMCPServer()
    server.run()