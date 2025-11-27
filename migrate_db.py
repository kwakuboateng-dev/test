"""
Database Migration Script - Add Missing Columns to Users Table

Run this script to add the missing columns to your existing database:
    python3 migrate_db.py

Or if you want a fresh start, you can drop and recreate all tables:
    python3 recreate_db.py
"""

from sqlalchemy import create_engine, text
from database import DATABASE_URL, Base, engine
from models import User, Match, Message, Mission, Block, Report

def migrate_database():
    """Add missing columns to existing users table"""
    print("Running database migration...")
    
    with engine.connect() as conn:
        # Add missing columns if they don't exist
        migrations = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS interests TEXT",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS mood_status VARCHAR(100) DEFAULT 'Open to chat'",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS latitude FLOAT",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS longitude FLOAT",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_location_update TIMESTAMP",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS xp INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 1",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(255)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS photo_verified BOOLEAN DEFAULT FALSE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS push_token VARCHAR(255)",
        ]
        
        for migration in migrations:
            try:
                conn.execute(text(migration))
                print(f"✓ {migration[:50]}...")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        conn.commit()
    
    print("\n✅ Migration complete!")

def recreate_database():
    """Drop all tables and recreate them (WARNING: This will delete all data!)"""
    print("⚠️  WARNING: This will delete all existing data!")
    confirm = input("Type 'yes' to continue: ")
    
    if confirm.lower() != 'yes':
        print("Cancelled.")
        return
    
    print("\n🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("📦 Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ Database recreated!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--recreate":
        recreate_database()
    else:
        migrate_database()
