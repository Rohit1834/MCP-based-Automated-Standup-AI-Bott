import json
import os
from datetime import datetime
from mcp.server import Server
from mcp.types import Tool
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

print("Starting Slack MCP Server initialization...")

class SlackMCPServer:
    def __init__(self):
        print("Initializing SlackMCPServer...")
        self.server = Server("slack-server")
        load_dotenv()  # Load environment variables
        
        # Use environment variable instead of hardcoded token
        self.slack_token = os.environ.get('SLACK_BOT_TOKEN')
        if not self.slack_token:
            print("Warning: SLACK_BOT_TOKEN not found in environment variables")
        else:
            print("Slack token found in environment variables")
            
        self.client = WebClient(token=self.slack_token)
        self.default_channel = os.environ.get('SLACK_CHANNEL', '#social')
        print(f"Using channel: {self.default_channel}")
        
        self.register_tools()
        print("Tools registered successfully")
    
    def register_tools(self):
        """Register MCP tools for Slack"""
        print("Registering tools...")
        
        @self.server.tool()
        async def post_standup_message(content: str) -> str:
            """Post the daily standup message to Slack"""
            print(f"Attempting to post message: {content}")
            try:
                response = self.client.chat_postMessage(
                    channel=self.default_channel,
                    text=content,
                    parse="full"
                )
                print("Message posted successfully!")
                return json.dumps({
                    "success": True,
                    "timestamp": response['ts'],
                    "channel": response['channel']
                })
            except SlackApiError as e:
                error_message = f"Error posting to Slack: {str(e)}"
                print(error_message)
                return json.dumps({
                    "success": False,
                    "error": error_message
                })
        
        @self.server.tool()
        async def post_formatted_standup(metrics: dict, events: list) -> str:
            """Post a beautifully formatted standup message"""
            print("Posting formatted standup message...")
            # Create formatted message
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
                            "text": f"*Sales:* {metrics.get('sales_count', 0)} orders"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Revenue:* ${metrics.get('revenue', 0):,.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Support:* {metrics.get('tickets_resolved', 0)} tickets resolved"
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
                        "text": "*📅 Today's Focus:*"
                    }
                }
            ]
            
            # Add events
            if events:
                event_text = ""
                for event in events[:3]:  # Show top 3 events
                    time = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                    event_text += f"• {time.strftime('%I:%M %p')} - {event['summary']}\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": event_text
                    }
                })
            
            # Add motivational footer
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_Let's make it a great day, team!_ 💪"
                }
            })
            
            try:
                response = self.client.chat_postMessage(
                    channel=self.default_channel,
                    blocks=blocks,
                    text="Daily Standup"  # Fallback text
                )
                return json.dumps({"success": True})
            except SlackApiError as e:
                return json.dumps({"success": False, "error": str(e)})
    
    def run(self):
        """Start the MCP server"""
        print("Starting MCP server...")
        try:
            self.server.run()
        except Exception as e:
            print(f"Error running server: {str(e)}")

if __name__ == "__main__":
    print("Starting Slack MCP Server...")
    try:
        server = SlackMCPServer()
        print("Server initialized, starting run loop...")
        server.run()
    except Exception as e:
        print(f"Error in main: {str(e)}")