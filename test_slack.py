# test_slack_connection.py
from dotenv import load_dotenv
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def test_slack():
    load_dotenv()
    
    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_CHANNEL", "#social")
    
    if not token:
        print("❌ No SLACK_BOT_TOKEN found in .env")
        return
    
    client = WebClient(token=token)
    
    try:
        # Test auth
        auth_result = client.auth_test()
        print(f"✅ Connected as: {auth_result['user']}")
        print(f"   Team: {auth_result['team']}")
        
        # Test posting
        result = client.chat_postMessage(
            channel=channel,
            text="🧪 Test message from Daily Standup Bot - Connection successful!"
        )
        print(f"✅ Test message posted to {channel}")
        
    except SlackApiError as e:
        print(f"❌ Slack Error: {e.response['error']}")
        if e.response['error'] == 'invalid_auth':
            print("   Your token appears to be invalid")
        elif e.response['error'] == 'channel_not_found':
            print(f"   Channel {channel} not found or bot not added to channel")

if __name__ == "__main__":
    test_slack()