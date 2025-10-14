#!/usr/bin/env python3
"""
Test script to verify bot updates work correctly
"""

from app.database import SessionLocal
from app.services.bot_service import BotService
from app.schemas.bot import BotUpdate

def test_bot_update():
    db = SessionLocal()

    try:
        # Get all bots
        bots = BotService.get_all_bots(db)

        if not bots:
            print("❌ No bots found. Create a bot first.")
            return

        bot = bots[0]
        print(f"Testing bot: {bot.name}")
        print(f"  ID: {bot.id}")
        print(f"  Provider: {bot.provider}")
        print(f"  Model: {bot.model}")
        print(f"  Reasoning Effort: {bot.reasoning_effort}")
        print(f"  Text Verbosity: {bot.text_verbosity}")

        # Try updating it
        print("\n🔄 Updating bot...")
        update_data = BotUpdate(
            name=bot.name,
            description="Updated description - test"
        )

        updated_bot = BotService.update_bot(db, bot.id, update_data)

        if updated_bot:
            print("✅ Bot updated successfully")
            print(f"  Reasoning Effort: {updated_bot.reasoning_effort}")
            print(f"  Text Verbosity: {updated_bot.text_verbosity}")

            # Verify fields are still present
            if updated_bot.reasoning_effort is None:
                print("⚠️  WARNING: reasoning_effort became NULL after update!")
            if updated_bot.text_verbosity is None:
                print("⚠️  WARNING: text_verbosity became NULL after update!")
        else:
            print("❌ Bot update failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_bot_update()
