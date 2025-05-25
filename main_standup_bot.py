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
from whatsapp_helper import WhatsAppHelper  # Changed import

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
        
        # Initialize WhatsApp
        try:
            self.whatsapp = WhatsAppHelper()
            if self.whatsapp.login():
                print("✅ WhatsApp connected")
            else:
                print("⚠️ WhatsApp connection failed")
                self.whatsapp = None
        except Exception as e:
            print(f"⚠️ WhatsApp not connected: {e}")
            self.whatsapp = None
    
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
    
    async def get_whatsapp_updates(self) -> List[Dict]:
        """Get important updates from WhatsApp groups"""
        if self.whatsapp:
            try:
                # Customize these group names to match your WhatsApp groups
                group_names = [
                    "QA issues"          # Your development team group
                          # Customer support group
                ]
                
                updates = self.whatsapp.get_important_updates(group_names)
                return updates
            except Exception as e:
                print(f"❌ Error fetching WhatsApp updates: {e}")
                return []
        else:
            # Fallback mock data if WhatsApp not connected
            print("⚠️ Using mock WhatsApp data")
            return [
                {
                    "group": "Dev Team",
                    "sender": "John",
                    "message": "API integration completed for payment module",
                    "time": "11:30 PM"
                },
                {
                    "group": "Support Team",
                    "sender": "Sarah",
                    "message": "Urgent: Customer facing login issues",
                    "time": "10:45 PM"
                }
            ]
    
    async def post_to_slack(self, metrics: Dict, whatsapp_updates: List[Dict]):
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
                    "text": "*💬 Key WhatsApp Updates (Last 24h):*"
                }
            }
        ]
        
        # Add WhatsApp updates
        if whatsapp_updates:
            update_text = ""
            for update in whatsapp_updates[:5]:  # Show top 5 updates
                update_text += f"• *[{update['group']}]* {update['sender']}: {update['message']}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": update_text
                }
            })
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_No important updates from WhatsApp groups_"
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
            
            # Step 2: Get WhatsApp updates
            print("💬 Fetching WhatsApp group updates...")
            whatsapp_updates = await self.get_whatsapp_updates()
            print(f"   Found {len(whatsapp_updates)} important updates")
            
            # Step 3: Post to Slack
            print("📮 Posting to Slack...")
            success = await self.post_to_slack(metrics, whatsapp_updates)
            
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
            if self.whatsapp:
                self.whatsapp.close()
    
    def __del__(self):
        """Cleanup on exit"""
        if hasattr(self, 'whatsapp') and self.whatsapp:
            self.whatsapp.close()

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