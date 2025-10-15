"""
One-time script to update max_tokens for all existing bots
Run this with: python3 update_max_tokens.py
"""
from app.database import SessionLocal, init_db
from app.models.api_key import APIKey  # Import APIKey first
from app.models.bot import Bot

# Initialize database to ensure all tables exist
init_db()

def update_max_tokens():
    db = SessionLocal()
    try:
        # Get all bots with low max_tokens
        bots = db.query(Bot).filter(Bot.max_tokens < 4096).all()

        print(f"Found {len(bots)} bots with max_tokens < 4096")

        for bot in bots:
            old_value = bot.max_tokens
            bot.max_tokens = 8192
            print(f"Updated bot '{bot.name}': {old_value} → 8192 tokens")

        db.commit()
        print("\n✅ All bots updated successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_max_tokens()
