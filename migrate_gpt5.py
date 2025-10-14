#!/usr/bin/env python3
"""
Migration script to add GPT-5 fields to existing Bot table.

Run this if you already have a database and want to add GPT-5 support.

Usage:
    python migrate_gpt5.py
"""

from sqlalchemy import text
from app.database import engine
from app.config import settings


def migrate():
    """Add GPT-5 fields to bots table"""
    print("🚀 Starting GPT-5 migration...")
    print(f"📊 Database: {settings.database_url}")

    with engine.connect() as conn:
        try:
            # Check if columns already exist
            if 'sqlite' in settings.database_url.lower():
                result = conn.execute(text("PRAGMA table_info(bots)"))
                columns = {row[1] for row in result}
            else:  # PostgreSQL
                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='bots'
                """))
                columns = {row[0] for row in result}

            if 'reasoning_effort' in columns:
                print("✅ GPT-5 fields already exist. No migration needed.")
                return

            # Add new columns
            print("➕ Adding reasoning_effort column...")
            conn.execute(text("""
                ALTER TABLE bots
                ADD COLUMN reasoning_effort VARCHAR(20) DEFAULT 'medium'
            """))
            conn.commit()

            print("➕ Adding text_verbosity column...")
            conn.execute(text("""
                ALTER TABLE bots
                ADD COLUMN text_verbosity VARCHAR(20) DEFAULT 'medium'
            """))
            conn.commit()

            # Update existing bots with default values
            print("🔄 Updating existing bots with default values...")
            conn.execute(text("""
                UPDATE bots
                SET reasoning_effort = 'medium',
                    text_verbosity = 'medium'
                WHERE reasoning_effort IS NULL
            """))
            conn.commit()

            print("✅ Migration completed successfully!")
            print("🎉 Your database is now ready for GPT-5!")

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure your database is accessible")
            print("2. Check DATABASE_URL in .env file")
            print("3. Ensure you have write permissions")
            print("4. If using PostgreSQL, make sure the user has ALTER TABLE privileges")
            raise


if __name__ == "__main__":
    migrate()
