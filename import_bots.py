"""
Import bots, API keys, and conversations from a JSON export file
Supports importing into SQLite or PostgreSQL

Usage:
  python3 import_bots.py bot_export.json                    # Import to local SQLite
  python3 import_bots.py bot_export.json --database "postgres://..." # Import to specific database
  python3 import_bots.py bot_export.json --skip-existing    # Skip bots that already exist
"""
import json
import argparse
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

def import_database(json_file, database_url=None, skip_existing=False):
    """Import data from JSON file"""
    
    # Use provided database URL or default from settings
    db_url = database_url or settings.database_url
    
    print(f"📦 Importing to: {db_url.split('@')[0] if '@' in db_url else db_url}")
    print(f"📄 Source file: {json_file}")
    print()
    
    # Load JSON file
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File '{json_file}' not found")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file - {e}")
        return
    
    print(f"📊 Import file contains:")
    print(f"   API Keys: {len(import_data.get('api_keys', []))}")
    print(f"   Bots: {len(import_data.get('bots', []))}")
    print(f"   Conversations: {len(import_data.get('conversations', []))}")
    print(f"   Messages: {len(import_data.get('messages', []))}")
    print(f"   Export date: {import_data.get('export_date', 'Unknown')}")
    print()
    
    # Connect to database
    engine = create_engine(db_url)
    
    # Create tables if they don't exist
    from app.database import Base
    from app.models.bot import Bot
    from app.models.api_key import APIKey
    from app.models.conversation import Conversation, Message
    
    print("Creating tables if needed...")
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    stats = {
        "api_keys_imported": 0,
        "api_keys_skipped": 0,
        "bots_imported": 0,
        "bots_skipped": 0,
        "conversations_imported": 0,
        "messages_imported": 0
    }
    
    try:
        # Import API Keys
        print("\nImporting API Keys...")
        for key_data in import_data.get('api_keys', []):
            # Check if exists
            existing = db.execute(
                text("SELECT id FROM api_keys WHERE id = :id"),
                {"id": key_data["id"]}
            ).fetchone()
            
            if existing and skip_existing:
                print(f"  ⊘ Skipped (exists): {key_data['name']}")
                stats["api_keys_skipped"] += 1
                continue
            elif existing:
                # Update existing
                db.execute(
                    text("""
                        UPDATE api_keys 
                        SET name = :name, provider = :provider, api_key = :api_key, 
                            is_active = :is_active
                        WHERE id = :id
                    """),
                    key_data
                )
                print(f"  ↻ Updated: {key_data['name']}")
            else:
                # Insert new
                db.execute(
                    text("""
                        INSERT INTO api_keys (id, name, provider, api_key, is_active, created_at)
                        VALUES (:id, :name, :provider, :api_key, :is_active, :created_at)
                    """),
                    key_data
                )
                print(f"  ✓ Imported: {key_data['name']}")
                stats["api_keys_imported"] += 1
        
        db.commit()
        
        # Import Bots
        print("\nImporting Bots...")
        for bot_data in import_data.get('bots', []):
            # Check if exists
            existing = db.execute(
                text("SELECT id FROM bots WHERE id = :id"),
                {"id": bot_data["id"]}
            ).fetchone()
            
            if existing and skip_existing:
                print(f"  ⊘ Skipped (exists): {bot_data['name']}")
                stats["bots_skipped"] += 1
                continue
            elif existing:
                # Update existing
                db.execute(
                    text("""
                        UPDATE bots SET 
                            name = :name, description = :description, provider = :provider,
                            model = :model, api_key_id = :api_key_id, api_key = :api_key,
                            system_prompt = :system_prompt, temperature = :temperature,
                            max_tokens = :max_tokens, reasoning_effort = :reasoning_effort,
                            text_verbosity = :text_verbosity, use_qdrant = :use_qdrant,
                            qdrant_collection = :qdrant_collection, qdrant_top_k = :qdrant_top_k,
                            enable_memory = :enable_memory, memory_max_messages = :memory_max_messages,
                            enable_suggestions = :enable_suggestions, widget_title = :widget_title,
                            widget_color = :widget_color, widget_greeting = :widget_greeting,
                            is_active = :is_active
                        WHERE id = :id
                    """),
                    bot_data
                )
                print(f"  ↻ Updated: {bot_data['name']}")
            else:
                # Insert new
                db.execute(
                    text("""
                        INSERT INTO bots (
                            id, name, description, provider, model, api_key_id, api_key,
                            system_prompt, temperature, max_tokens, reasoning_effort, text_verbosity,
                            use_qdrant, qdrant_collection, qdrant_top_k,
                            enable_memory, memory_max_messages, enable_suggestions,
                            widget_title, widget_color, widget_greeting,
                            created_at, updated_at, is_active
                        ) VALUES (
                            :id, :name, :description, :provider, :model, :api_key_id, :api_key,
                            :system_prompt, :temperature, :max_tokens, :reasoning_effort, :text_verbosity,
                            :use_qdrant, :qdrant_collection, :qdrant_top_k,
                            :enable_memory, :memory_max_messages, :enable_suggestions,
                            :widget_title, :widget_color, :widget_greeting,
                            :created_at, :updated_at, :is_active
                        )
                    """),
                    bot_data
                )
                print(f"  ✓ Imported: {bot_data['name']}")
                stats["bots_imported"] += 1
        
        db.commit()
        
        # Import Conversations (if present)
        if import_data.get('conversations'):
            print("\nImporting Conversations...")
            for conv_data in import_data['conversations']:
                existing = db.execute(
                    text("SELECT id FROM conversations WHERE id = :id"),
                    {"id": conv_data["id"]}
                ).fetchone()
                
                if not existing:
                    db.execute(
                        text("""
                            INSERT INTO conversations (id, bot_id, session_id, created_at, updated_at)
                            VALUES (:id, :bot_id, :session_id, :created_at, :updated_at)
                        """),
                        conv_data
                    )
                    stats["conversations_imported"] += 1
            db.commit()
            print(f"  ✓ Imported {stats['conversations_imported']} conversations")
        
        # Import Messages (if present)
        if import_data.get('messages'):
            print("\nImporting Messages...")
            for msg_data in import_data['messages']:
                existing = db.execute(
                    text("SELECT id FROM messages WHERE id = :id"),
                    {"id": msg_data["id"]}
                ).fetchone()
                
                if not existing:
                    db.execute(
                        text("""
                            INSERT INTO messages (id, conversation_id, role, content, rag_context, created_at)
                            VALUES (:id, :conversation_id, :role, :content, :rag_context, :created_at)
                        """),
                        msg_data
                    )
                    stats["messages_imported"] += 1
            db.commit()
            print(f"  ✓ Imported {stats['messages_imported']} messages")
        
        print(f"\n✅ Import complete!")
        print(f"\n📊 Summary:")
        print(f"   API Keys imported: {stats['api_keys_imported']}")
        if stats['api_keys_skipped']:
            print(f"   API Keys skipped: {stats['api_keys_skipped']}")
        print(f"   Bots imported: {stats['bots_imported']}")
        if stats['bots_skipped']:
            print(f"   Bots skipped: {stats['bots_skipped']}")
        if stats['conversations_imported']:
            print(f"   Conversations imported: {stats['conversations_imported']}")
        if stats['messages_imported']:
            print(f"   Messages imported: {stats['messages_imported']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import bots from JSON file')
    parser.add_argument('json_file', help='JSON file to import')
    parser.add_argument('--database', help='Database URL (optional, uses default if not provided)')
    parser.add_argument('--skip-existing', action='store_true',
                       help='Skip items that already exist (default: update existing)')
    
    args = parser.parse_args()
    
    import_database(
        json_file=args.json_file,
        database_url=args.database,
        skip_existing=args.skip_existing
    )
