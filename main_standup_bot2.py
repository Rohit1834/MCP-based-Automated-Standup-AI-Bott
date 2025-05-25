# #!/usr/bin/env python3
# import asyncio
# import json
# import os
# import schedule
# import time
# from datetime import datetime, timedelta
# from typing import Dict, List
# import sqlite3
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# class DailyStandupBot:
#     def __init__(self):
#         self.slack_token = os.environ.get('SLACK_BOT_TOKEN')
#         self.slack_channel = os.environ.get('SLACK_CHANNEL', '#social')
        
#         if not self.slack_token:
#             raise ValueError("SLACK_BOT_TOKEN not found in environment variables")
        
#         self.slack_client = WebClient(token=self.slack_token)
#         print(f"✅ Initialized Slack client for channel: {self.slack_channel}")
    
#     async def get_metrics_from_db(self) -> Dict:
#         """Get metrics from SQLite database"""
#         conn = sqlite3.connect('database/business_data.db')
#         cursor = conn.cursor()
        
#         yesterday = (datetime.now() - timedelta(days=1)).date()
        
#         # Get sales data
#         cursor.execute('''
#             SELECT COUNT(*), SUM(amount) 
#             FROM sales 
#             WHERE DATE(created_at) = ?
#         ''', (yesterday,))
#         sales_count, total_revenue = cursor.fetchone()
        
#         # Get resolved tickets
#         cursor.execute('''
#             SELECT COUNT(*) 
#             FROM support_tickets 
#             WHERE DATE(resolved_at) = ?
#         ''', (yesterday,))
#         tickets_resolved = cursor.fetchone()[0]
        
#         conn.close()
        
#         return {
#             "sales_count": sales_count or 0,
#             "revenue": float(total_revenue or 0),
#             "tickets_resolved": tickets_resolved or 0
#         }
    
#     async def get_calendar_events(self) -> List[Dict]:
#         """Get calendar events (mock data for demo)"""
#         return [
#             {
#                 "summary": "Sprint Planning",
#                 "start": datetime.now().replace(hour=14, minute=0).isoformat(),
#                 "attendees": 5
#             },
#             {
#                 "summary": "BigCo Demo - API Integration",
#                 "start": datetime.now().replace(hour=11, minute=0).isoformat(),
#                 "attendees": 3
#             },
#             {
#                 "summary": "Team Sync",
#                 "start": datetime.now().replace(hour=16, minute=0).isoformat(),
#                 "attendees": 8
#             }
#         ]
    
#     async def post_to_slack(self, metrics: Dict, events: List[Dict]):
#         """Post the standup message to Slack"""
#         # Create blocks for rich formatting
#         blocks = [
#             {
#                 "type": "header",
#                 "text": {
#                     "type": "plain_text",
#                     "text": f"🌅 Daily Standup - {datetime.now().strftime('%A, %B %d')}"
#                 }
#             },
#             {
#                 "type": "section",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": "*📊 Yesterday's Performance:*"
#                 }
#             },
#             {
#                 "type": "section",
#                 "fields": [
#                     {
#                         "type": "mrkdwn",
#                         "text": f"*Sales:* {metrics['sales_count']} orders"
#                     },
#                     {
#                         "type": "mrkdwn",
#                         "text": f"*Revenue:* ${metrics['revenue']:,.2f}"
#                     },
#                     {
#                         "type": "mrkdwn",
#                         "text": f"*Support:* {metrics['tickets_resolved']} tickets resolved"
#                     },
#                     {
#                         "type": "mrkdwn",
#                         "text": f"*Status:* {'🎉 Record day!' if metrics['sales_count'] > 40 else '✅ Solid performance!'}"
#                     }
#                 ]
#             },
#             {
#                 "type": "divider"
#             },
#             {
#                 "type": "section",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": "*📅 Today's Focus:*"
#                 }
#             }
#         ]
        
#         # Add events
#         if events:
#             event_text = ""
#             for event in events[:3]:
#                 time = datetime.fromisoformat(event['start']).strftime('%I:%M %p')
#                 event_text += f"• {time} - {event['summary']} ({event['attendees']} attendees)\n"
            
#             blocks.append({
#                 "type": "section",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": event_text
#                 }
#             })
        
#         # Add alert if there's a demo
#         if any('demo' in event['summary'].lower() for event in events):
#             blocks.append({
#                 "type": "section",
#                 "text": {
#                     "type": "mrkdwn",
#                     "text": "⚠️ *Important:* Client demo today! Let's bring our A-game!"
#                 }
#             })
        
#         # Add footer
#         blocks.append({
#             "type": "section",
#             "text": {
#                 "type": "mrkdwn",
#                 "text": "_Let's make it a great day, team!_ 💪"
#             }
#         })
        
#         try:
#             # Actually send to Slack
#             response = self.slack_client.chat_postMessage(
#                 channel=self.slack_channel,
#                 blocks=blocks,
#                 text="Daily Standup"  # Fallback text
#             )
#             print(f"✅ Message posted to Slack successfully! (ts: {response['ts']})")
#             return True
#         except SlackApiError as e:
#             print(f"❌ Error posting to Slack: {e.response['error']}")
#             return False
    
#     async def run_daily_standup(self):
#         """Main standup routine"""
#         print(f"\n🚀 Running Daily Standup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
#         try:
#             # Step 1: Get metrics from database
#             print("📊 Fetching yesterday's metrics...")
#             metrics = await self.get_metrics_from_db()
#             print(f"   Sales: {metrics['sales_count']}, Revenue: ${metrics['revenue']:,.2f}")
            
#             # Step 2: Get today's calendar events
#             print("📅 Checking today's calendar...")
#             events = await self.get_calendar_events()
#             print(f"   Found {len(events)} events")
            
#             # Step 3: Post to Slack
#             print("📮 Posting to Slack...")
#             success = await self.post_to_slack(metrics, events)
            
#             if success:
#                 print("✅ Daily standup completed successfully!")
#             else:
#                 print("❌ Failed to post standup to Slack")
            
#         except Exception as e:
#             print(f"❌ Error during standup: {e}")
#             import traceback
#             traceback.print_exc()
    
#     def schedule_standups(self):
#         """Schedule daily standups"""
#         # Schedule for 9:00 AM every day
#         schedule.every().day.at("09:00").do(
#             lambda: asyncio.run(self.run_daily_standup())
#         )
        
#         # For testing, also run every minute
#         if os.environ.get("TEST_MODE") == "true":
#             schedule.every(1).minutes.do(
#                 lambda: asyncio.run(self.run_daily_standup())
#             )
        
#         print("📅 Standup scheduled for 9:00 AM daily")
#         if os.environ.get("TEST_MODE") == "true":
#             print("🧪 Test mode: Also running every minute")
        
#         print("⏰ Bot is running... Press Ctrl+C to stop")
        
#         # Run immediately for testing
#         asyncio.run(self.run_daily_standup())
        
#         # Keep running
#         try:
#             while True:
#                 schedule.run_pending()
#                 time.sleep(60)
#         except KeyboardInterrupt:
#             print("\n👋 Standup bot stopped")

# def main():
#     try:
#         bot = DailyStandupBot()
#         bot.schedule_standups()
#     except Exception as e:
#         print(f"❌ Failed to start bot: {e}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
import asyncio
import json
import os
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from google_calendar_helper import GoogleCalendarHelper  # Add this import

# Load environment variables
load_dotenv()

class DailyStandupBot:
    def __init__(self):
        self.slack_token = os.environ.get('SLACK_BOT_TOKEN')
        self.slack_channel = os.environ.get('SLACK_CHANNEL', '#social')
        
        if not self.slack_token:
            raise ValueError("SLACK_BOT_TOKEN not found in environment variables")
        
        self.slack_client = WebClient(token=self.slack_token)
        print(f"✅ Initialized Slack client for channel: {self.slack_channel}")
        
        # Initialize Google Calendar
        try:
            self.calendar = GoogleCalendarHelper()
            print("✅ Google Calendar connected")
        except Exception as e:
            print(f"⚠️ Google Calendar not connected: {e}")
            self.calendar = None
    
    async def get_metrics_from_db(self) -> Dict:
        """Get metrics from SQLite database"""
        conn = sqlite3.connect('database/business_data.db')
        cursor = conn.cursor()
        
        yesterday = (datetime.now() - timedelta(days=1)).date()
        
        # Get sales data
        cursor.execute('''
            SELECT COUNT(*), SUM(amount) 
            FROM sales 
            WHERE DATE(created_at) = ?
        ''', (yesterday,))
        sales_count, total_revenue = cursor.fetchone()
        
        # Get resolved tickets
        cursor.execute('''
            SELECT COUNT(*) 
            FROM support_tickets 
            WHERE DATE(resolved_at) = ?
        ''', (yesterday,))
        tickets_resolved = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "sales_count": sales_count or 0,
            "revenue": float(total_revenue or 0),
            "tickets_resolved": tickets_resolved or 0
        }
    
    async def get_calendar_events(self) -> List[Dict]:
        """Get real calendar events from Google Calendar"""
        if self.calendar:
            try:
                events = self.calendar.get_today_events()
                return events
            except Exception as e:
                print(f"❌ Error fetching calendar events: {e}")
                return []
        else:
            # Fallback to mock data if calendar not connected
            print("⚠️ Using mock calendar data (Google Calendar not connected)")
            return [
                {
                    "summary": "Sprint Planning",
                    "start": datetime.now().replace(hour=14, minute=0).isoformat(),
                    "attendees": 5
                }
            ]
    
    async def post_to_slack(self, metrics: Dict, events: List[Dict]):
        """Post the standup message to Slack"""
        # Create blocks for rich formatting
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🌅 Daily Standup - {datetime.now().strftime('%A, %B %d')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 Yesterday's Performance:*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Sales:* {metrics['sales_count']} orders"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Revenue:* ${metrics['revenue']:,.2f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Support:* {metrics['tickets_resolved']} tickets resolved"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:* {'🎉 Record day!' if metrics['sales_count'] > 40 else '✅ Solid performance!'}"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📅 Today's Schedule:*"
                }
            }
        ]
        
        # Add events
        if events:
            event_text = ""
            for event in events[:5]:  # Show up to 5 events
                time = datetime.fromisoformat(event['start'].replace('Z', '+00:00')).strftime('%I:%M %p')
                event_text += f"• {time} - *{event['summary']}*"
                
                # Add attendees count if available
                if event.get('attendees', 0) > 0:
                    event_text += f" ({event['attendees']} attendees)"
                
                # Add meeting link if available
                if event.get('meeting_link'):
                    event_text += f" <{event['meeting_link']}|Join>"
                
                event_text += "\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": event_text
                }
            })
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_No meetings scheduled for today_ 🎉"
                }
            })
        
        # Add alerts for important events
        important_keywords = ['demo', 'client', 'presentation', 'interview', 'sprint']
        important_events = [e for e in events if any(keyword in e['summary'].lower() for keyword in important_keywords)]
        
        if important_events:
            alert_text = "⚠️ *Important events today:*\n"
            for event in important_events:
                time = datetime.fromisoformat(event['start'].replace('Z', '+00:00')).strftime('%I:%M %p')
                alert_text += f"• {event['summary']} at {time}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": alert_text
                }
            })
        
        # Add footer
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "_Let's make it a great day, team!_ 💪"
            }
        })
        
        try:
            # Actually send to Slack
            response = self.slack_client.chat_postMessage(
                channel=self.slack_channel,
                blocks=blocks,
                text="Daily Standup"  # Fallback text
            )
            print(f"✅ Message posted to Slack successfully! (ts: {response['ts']})")
            return True
        except SlackApiError as e:
            print(f"❌ Error posting to Slack: {e.response['error']}")
            return False
    
    async def run_daily_standup(self):
        """Main standup routine"""
        print(f"\n🚀 Running Daily Standup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Step 1: Get metrics from database
            print("📊 Fetching yesterday's metrics...")
            metrics = await self.get_metrics_from_db()
            print(f"   Sales: {metrics['sales_count']}, Revenue: ${metrics['revenue']:,.2f}")
            
            # Step 2: Get today's calendar events
            print("📅 Fetching today's calendar events from rohitobrai11@gmail.com...")
            events = await self.get_calendar_events()
            print(f"   Found {len(events)} events")
            
            # Step 3: Post to Slack
            print("📮 Posting to Slack...")
            success = await self.post_to_slack(metrics, events)
            
            if success:
                print("✅ Daily standup completed successfully!")
            else:
                print("❌ Failed to post standup to Slack")
            
        except Exception as e:
            print(f"❌ Error during standup: {e}")
            import traceback
            traceback.print_exc()
    
    def schedule_standups(self):
        """Schedule daily standups"""
        # Schedule for 9:00 AM every day
        schedule.every().day.at("09:00").do(
            lambda: asyncio.run(self.run_daily_standup())
        )
        
        # For testing, also run every minute
        if os.environ.get("TEST_MODE") == "true":
            schedule.every(1).minutes.do(
                lambda: asyncio.run(self.run_daily_standup())
            )
        
        print("📅 Standup scheduled for 9:00 AM daily")
        if os.environ.get("TEST_MODE") == "true":
            print("🧪 Test mode: Also running every minute")
        
        print("⏰ Bot is running... Press Ctrl+C to stop")
        
        # Run immediately for testing
        asyncio.run(self.run_daily_standup())
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Standup bot stopped")

def main():
    try:
        bot = DailyStandupBot()
        bot.schedule_standups()
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()