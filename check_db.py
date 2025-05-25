import sqlite3
from datetime import datetime

def check_database():
    conn = sqlite3.connect('database/business_data.db')
    cursor = conn.cursor()
    
    print("📊 DATABASE CONTENTS:\n")
    
    # Check sales table
    print("SALES TABLE:")
    cursor.execute("SELECT COUNT(*) FROM sales")
    count = cursor.fetchone()[0]
    print(f"Total sales records: {count}")
    
    cursor.execute("SELECT * FROM sales ORDER BY created_at DESC LIMIT 5")
    sales = cursor.fetchall()
    print("\nLast 5 sales:")
    for sale in sales:
        print(f"  ID: {sale[0]}, Amount: ${sale[1]}, Product: {sale[2]}, Date: {sale[4]}")
    
    print("\n" + "="*50 + "\n")
    
    # Check support tickets
    print("SUPPORT TICKETS TABLE:")
    cursor.execute("SELECT COUNT(*) FROM support_tickets")
    count = cursor.fetchone()[0]
    print(f"Total tickets: {count}")
    
    cursor.execute("SELECT * FROM support_tickets WHERE status='resolved' LIMIT 5")
    tickets = cursor.fetchall()
    print("\nResolved tickets:")
    for ticket in tickets:
        print(f"  ID: {ticket[0]}, Status: {ticket[1]}, Resolved: {ticket[3]}")
    
    conn.close()

if __name__ == "__main__":
    check_database()