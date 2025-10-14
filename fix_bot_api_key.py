#!/usr/bin/env python3
"""
Quick fix script to:
1. Add a valid API key to the system
2. Update your existing bot to use it
"""

from app.database import SessionLocal
from app.services.bot_service import BotService
from app.services.api_key_service import APIKeyService
from app.schemas.api_key import APIKeyCreate
from app.schemas.bot import BotUpdate

print("🔧 Bot API Key Fix Script")
print("=" * 50)

# Get the API key from user
print("\n⚠️  Your bot has a corrupted API key and needs to be fixed.")
print("\nPlease enter a valid Anthropic API key:")
print("(Get one from: https://console.anthropic.com/settings/keys)")
api_key = input("\nAPI Key (sk-ant-...): ").strip()

if not api_key or not api_key.startswith('sk-ant-'):
    print("❌ Invalid API key format. Must start with 'sk-ant-'")
    exit(1)

db = SessionLocal()

try:
    # Step 1: Create an APIKey entry
    print("\n1️⃣ Creating API key entry...")
    api_key_data = APIKeyCreate(
        name="Genghis Khan Bot API Key",
        provider="anthropic",
        api_key=api_key
    )

    saved_key = APIKeyService.create_api_key(db, api_key_data)
    print(f"✅ API key created: {saved_key.name}")
    print(f"   ID: {saved_key.id}")

    # Step 2: Update the bot to use this API key
    print("\n2️⃣ Updating bot to use new API key...")
    bot_id = "eef34087-2222-4c6d-a9ab-1ccba4bb93e5"

    update_data = BotUpdate(
        api_key_id=saved_key.id,
        api_key=None  # Clear the old corrupted key
    )

    updated_bot = BotService.update_bot(db, bot_id, update_data)

    if updated_bot:
        print(f"✅ Bot updated: {updated_bot.name}")
        print(f"   Now using API key: {saved_key.name}")
        print(f"   API Key ID: {updated_bot.api_key_id}")
    else:
        print("❌ Failed to update bot")

    print("\n" + "=" * 50)
    print("✅ Fix complete! Your bot should now work.")
    print("\nNext steps:")
    print("1. Restart your server (if it's running)")
    print("2. Hard refresh your browser (Ctrl+Shift+R)")
    print("3. Try chatting with the bot!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
