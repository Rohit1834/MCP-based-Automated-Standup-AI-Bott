import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List
from mcp.server import Server
from mcp.types import Tool, TextContent

class SQLiteMCPServer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.server = Server("sqlite-server")
        self.setup_database()
        self.register_tools()
    
    def setup_database(self):
        """Initialize database with sample tables"""
        conn = sqlite3.connect(self.db_path)
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value DECIMAL(10,2),
                date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_tools(self):
        """Register MCP tools"""
        
        @self.server.tool()
        async def get_yesterday_metrics() -> str:
            """Get yesterday's business metrics"""
            conn = sqlite3.connect(self.db_path)
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
            
            return json.dumps({
                "sales_count": sales_count or 0,
                "revenue": float(total_revenue or 0),
                "tickets_resolved": tickets_resolved or 0,
                "date": str(yesterday)
            })
        
        @self.server.tool()
        async def get_weekly_trends() -> str:
            """Get weekly business trends"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get 7-day sales trend
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*), SUM(amount)
                FROM sales
                WHERE created_at >= date('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            ''')
            
            trends = cursor.fetchall()
            conn.close()
            
            return json.dumps([{
                "date": row[0],
                "sales": row[1],
                "revenue": float(row[2])
            } for row in trends])
        
        @self.server.tool()
        async def add_sample_data() -> str:
            """Add sample data for testing"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add yesterday's sales
            yesterday = datetime.now() - timedelta(days=1)
            for i in range(45):
                cursor.execute('''
                    INSERT INTO sales (amount, product, customer, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    266.67,  # Total will be ~12K
                    f"Product {i % 5}",
                    f"Customer {i % 20}",
                    yesterday
                ))
            
            # Add resolved tickets
            for i in range(3):
                cursor.execute('''
                    INSERT INTO support_tickets (status, priority, resolved_at)
                    VALUES (?, ?, ?)
                ''', ("resolved", "medium", yesterday))
            
            conn.commit()
            conn.close()
            
            return "Sample data added successfully"
    
    def run(self):
        """Start the MCP server"""
        self.server.run()

# Initialize and run the server
if __name__ == "__main__":
    server = SQLiteMCPServer("database/business_data.db")
    server.run()