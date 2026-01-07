"""
Database migration script to add sodium column to foods table
Run this once to update the database schema
"""

import sqlite3
import os

# Get the database path - it's in the root directory
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nutrition.db")

def migrate():
    print(f"Looking for database at: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(foods)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'sodium' not in columns:
            print("Adding sodium column to foods table...")
            cursor.execute("ALTER TABLE foods ADD COLUMN sodium REAL")
            conn.commit()
            print("✅ Migration successful! Sodium column added.")
        else:
            print("✅ Sodium column already exists. No migration needed.")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
