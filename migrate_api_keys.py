#!/usr/bin/env python3
"""
Migration script to add API key management feature
This will:
1. Create the api_keys table
2. Add api_key_id column to bots table
3. Migrate existing bot API keys to the new system
"""

from app.database import engine, SessionLocal
from app.models.api_key import APIKey
from app.models.bot import Bot
from sqlalchemy import text
import uuid

def migrate():
    """Run the migration"""
    db = SessionLocal()

    try:
        print("🔄 Starting migration...")

        # Create api_keys table
        print("\n1. Creating api_keys table...")
        APIKey.__table__.create(engine, checkfirst=True)
        print("✅ api_keys table created")

        # Add api_key_id column to bots table if it doesn't exist
        print("\n2. Adding api_key_id column to bots table...")
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE bots ADD COLUMN api_key_id VARCHAR(36)"))
                conn.commit()
            print("✅ api_key_id column added")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  api_key_id column already exists, skipping")
            else:
                raise

        # Migrate existing bot API keys to new system
        print("\n3. Migrating existing bot API keys...")
        bots = db.query(Bot).filter(Bot.is_active == True).all()

        migrated_count = 0
        for bot in bots:
            # Skip if already migrated or no API key
            if bot.api_key_id or not bot.api_key:
                continue

            # Check if API key is not already masked (length check)
            if len(bot.api_key) < 20:  # Masked keys are only 15 chars
                print(f"⚠️  Bot '{bot.name}' has a masked/invalid API key, skipping migration")
                continue

            # Create an APIKey entry for this bot
            api_key_entry = APIKey(
                id=str(uuid.uuid4()),
                name=f"{bot.name} API Key",
                provider=bot.provider,
                api_key=bot.api_key
            )
            db.add(api_key_entry)
            db.flush()  # Get the ID

            # Update bot to reference the new API key
            bot.api_key_id = api_key_entry.id

            migrated_count += 1
            print(f"✅ Migrated API key for bot: {bot.name}")

        db.commit()
        print(f"\n✅ Migration complete! Migrated {migrated_count} bot(s)")

        # Show summary
        print("\n📊 Summary:")
        total_api_keys = db.query(APIKey).filter(APIKey.is_active == True).count()
        total_bots = db.query(Bot).filter(Bot.is_active == True).count()
        bots_with_new_system = db.query(Bot).filter(Bot.api_key_id != None).count()
        bots_with_legacy = db.query(Bot).filter(Bot.api_key_id == None, Bot.api_key != None).count()

        print(f"  Total API keys: {total_api_keys}")
        print(f"  Total bots: {total_bots}")
        print(f"  Bots using new system: {bots_with_new_system}")
        print(f"  Bots using legacy system: {bots_with_legacy}")

        if bots_with_legacy > 0:
            print(f"\n⚠️  {bots_with_legacy} bot(s) still using legacy API key storage")
            print("   These bots may have masked/invalid API keys that need to be updated manually")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
