#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime, timedelta
import random

def setup_database():
    """Initialize database with sample data"""
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect('database/business_data.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount DECIMAL(10,2),
            product TEXT,
            customer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT,
            priority TEXT,
            resolved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add sample data for yesterday
    yesterday = datetime.now() - timedelta(days=1)
    
    # Add 45 sales for yesterday
    products = ['Basic Plan', 'Pro Plan', 'Enterprise Plan', 'Add-on', 'Consulting']
    for i in range(45):
        amount = random.uniform(100, 500)
        cursor.execute('''
            INSERT INTO sales (amount, product, customer, created_at)
            VALUES (?, ?, ?, ?)
        ''', (amount, random.choice(products), f"Customer{i}", yesterday))
    
    # Add 3 resolved tickets
    for i in range(3):
        cursor.execute('''
            INSERT INTO support_tickets (status, priority, resolved_at, created_at)
            VALUES ('resolved', 'medium', ?, ?)
        ''', (yesterday, yesterday - timedelta(hours=random.randint(1, 8))))
    
    conn.commit()
    conn.close()
    print("Database setup complete!")

def create_env_file():
    """Create .env file template"""
    env_content = """# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL=#general

# Testing
TEST_MODE=true

# Google Calendar (optional)
# Follow https://developers.google.com/calendar/quickstart/python
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("Created .env file - Please add your Slack token!")

def create_mcp_config():
    """Create MCP configuration"""
    os.makedirs('config', exist_ok=True)
    config = {
        "servers": {
            "sqlite": {
                "command": "python mcp_servers/sqlite_server.py",
                "args": ["database/business_data.db"]
            },
            "gcal": {
                "command": "python mcp_servers/gcal_server.py"
            },
            "slack": {
                "command": "python mcp_servers/slack_server.py"
            }
        }
    }
    
    import json
    with open('config/mcp_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(" Created MCP configuration!")

if __name__ == "__main__":
    print("Setting up Daily Standup Bot...")
    setup_database()
    create_env_file()
    create_mcp_config()
    print("\n Setup complete! Next steps:")
    print("1. Add your Slack bot token to .env file")
    print("2. (Optional) Set up Google Calendar credentials")
    print("3. Run: python main_standup_bot.py")


from setuptools import setup, find_packages

setup(
    name="mcp",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "slack-sdk",
        "python-dotenv",
    ],
)    