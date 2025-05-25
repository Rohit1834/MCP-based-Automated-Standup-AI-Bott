import os
import time
import pickle
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import re

class WhatsAppHelper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with persistent session"""
        chrome_options = webdriver.ChromeOptions()
        
        # Create a user data directory to persist WhatsApp Web login
        user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
        os.makedirs(user_data_dir, exist_ok=True)
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        
        # Other options
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    
    def login(self):
        """Open WhatsApp Web and wait for login"""
        print("📱 Opening WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        
        # Check if already logged in
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="application"]'))
            )
            print("✅ Already logged in to WhatsApp")
            time.sleep(3)  # Give it time to fully load
            return True
        except:
            print("📲 Please scan the QR code with your phone...")
            
        # Wait for login (up to 60 seconds)
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="application"]'))
            )
            print("✅ Successfully logged in to WhatsApp")
            time.sleep(3)  # Give it time to fully load
            return True
        except:
            print("❌ Login timeout")
            return False
    
    def get_group_messages(self, group_name, hours_back=24):
        """Get messages from a specific WhatsApp group"""
        try:
            print(f"🔍 Searching for group: {group_name}")
            
            # Click on search
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="chat-list-search"]'))
            )
            search_button.click()
            time.sleep(1)
            
            # Type group name
            search_input = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="search-input"]')
            search_input.clear()
            search_input.send_keys(group_name)
            time.sleep(2)
            
            # Try to find and click the group
            try:
                # Try multiple selectors
                group_element = None
                
                # Method 1: By title
                try:
                    group_element = self.driver.find_element(By.XPATH, f'//span[@title="{group_name}"]')
                except:
                    pass
                
                # Method 2: By partial text
                if not group_element:
                    try:
                        group_element = self.driver.find_element(By.XPATH, f'//span[contains(@title, "{group_name}")]')
                    except:
                        pass
                
                if group_element:
                    group_element.click()
                    print(f"✅ Opened group: {group_name}")
                    time.sleep(2)
                else:
                    print(f"❌ Group not found: {group_name}")
                    return []
                
            except Exception as e:
                print(f"❌ Could not open group: {e}")
                return []
            
            # Extract messages
            messages = self.extract_recent_messages(hours_back)
            return messages
            
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def extract_recent_messages(self, hours_back):
        """Extract messages from the current chat"""
        messages = []
        
        try:
            # Wait for messages to load
            time.sleep(2)
            
            # Try to find message containers
            msg_containers = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="msg-container"]')
            
            if not msg_containers:
                # Try alternative selector
                msg_containers = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="message-in"], div[class*="message-out"]')
            
            print(f"📨 Found {len(msg_containers)} message containers")
            
            for msg in msg_containers:
                try:
                    # Get message text - try multiple methods
                    text = ""
                    
                    # Method 1: data-testid
                    try:
                        text_element = msg.find_element(By.CSS_SELECTOR, 'span[data-testid="msg-text"]')
                        text = text_element.text
                    except:
                        pass
                    
                    # Method 2: class selectors
                    if not text:
                        try:
                            text_element = msg.find_element(By.CSS_SELECTOR, 'span.selectable-text')
                            text = text_element.text
                        except:
                            pass
                    
                    # Method 3: any span with text
                    if not text:
                        try:
                            spans = msg.find_elements(By.TAG_NAME, 'span')
                            for span in spans:
                                if span.text and len(span.text) > 5:
                                    text = span.text
                                    break
                        except:
                            pass
                    
                    if not text:
                        continue
                    
                    # Get sender name
                    sender = "Unknown"
                    try:
                        # For incoming messages
                        sender_element = msg.find_element(By.CSS_SELECTOR, 'span[data-testid="msg-author"]')
                        sender = sender_element.text
                    except:
                        try:
                            # Alternative method
                            sender_element = msg.find_element(By.CSS_SELECTOR, 'span[aria-label*="You:"]')
                            sender = "You"
                        except:
                            pass
                    
                    # Get time
                    msg_time = ""
                    try:
                        time_element = msg.find_element(By.CSS_SELECTOR, 'span[data-testid="msg-time"]')
                        msg_time = time_element.text
                    except:
                        try:
                            time_element = msg.find_element(By.CSS_SELECTOR, 'div[data-testid="msg-meta"] span')
                            msg_time = time_element.text
                        except:
                            pass
                    
                    if text:  # Only add if we found text
                        messages.append({
                            'sender': sender,
                            'text': text,
                            'time': msg_time
                        })
                        print(f"   📝 Message: {sender}: {text[:50]}...")
                    
                except Exception as e:
                    continue
            
            print(f"✅ Extracted {len(messages)} messages")
            return messages
            
        except Exception as e:
            print(f"❌ Error extracting messages: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_important_updates(self, group_names=None):
        """Get important updates from multiple groups"""
        if not group_names:
            group_names = ["Dev_Team", "Project Updates", "Support Team"]  # Updated default
        
        all_updates = []
        
        for group in group_names:
            print(f"\n📝 Checking group: {group}")
            messages = self.get_group_messages(group, hours_back=24)
            
            if not messages:
                print(f"   No messages found in {group}")
                continue
            
            # Filter for important messages
            important_keywords = [
                'completed', 'done', 'finished', 'deployed', 'released',
                'blocked', 'issue', 'problem', 'urgent', 'help',
                'meeting', 'demo', 'presentation', 'review',
                'milestone', 'deadline', 'update', 'api', 'integration',
                'standup', 'working', 'progress'
            ]
            
            for msg in messages:
                # Check if message contains important keywords
                if any(keyword in msg['text'].lower() for keyword in important_keywords):
                    all_updates.append({
                        'group': group,
                        'sender': msg['sender'],
                        'message': msg['text'],
                        'time': msg['time']
                    })
            
            # If no important messages, just get the last few messages
            if not all_updates and messages:
                for msg in messages[-3:]:  # Last 3 messages
                    all_updates.append({
                        'group': group,
                        'sender': msg['sender'],
                        'message': msg['text'],
                        'time': msg['time']
                    })
        
        return all_updates
    
    def send_test_message(self, group_name, message):
        """Send a test message to a group"""
        try:
            # First navigate to the group
            self.get_group_messages(group_name, hours_back=1)
            
            # Find message input
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="conversation-compose-box-input"]'))
            )
            
            # Type and send message
            message_input.send_keys(message)
            message_input.send_keys(Keys.ENTER)
            
            print(f"✅ Sent message to {group_name}")
            return True
            
        except Exception as e:
            print(f"❌ Could not send message: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

# Test function
if __name__ == "__main__":
    whatsapp = WhatsAppHelper()
    if whatsapp.login():
        # Send a test message first
        whatsapp.send_test_message("Dev_Team", "Testing bot - API integration call at 4:30 PM")
        time.sleep(2)
        
        # Then fetch messages
        updates = whatsapp.get_important_updates(["Dev_Team"])
        print("\nImportant updates found:")
        for update in updates:
            print(f"- {update['sender']}: {update['message']}")
    
    input("\nPress Enter to close...")
    whatsapp.close()