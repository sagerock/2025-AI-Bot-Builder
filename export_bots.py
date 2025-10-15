"""
Export all bots, API keys, and conversations to a JSON file
This allows you to backup or transfer bots between systems

Usage:
  python3 export_bots.py                           # Export from local SQLite
  python3 export_bots.py --database "postgres://..." # Export from specific database
  python3 export_bots.py --output my_backup.json   # Custom output file
"""
import json
import argparse
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

def export_database(database_url=None, output_file=None, include_conversations=False):
    """Export all data to JSON"""
    
    # Use provided database URL or default from settings
    db_url = database_url or settings.database_url
    
    # Generate output filename
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"bot_export_{timestamp}.json"
    
    print(f"📦 Exporting from: {db_url.split('@')[0] if '@' in db_url else db_url}")
    print(f"📄 Output file: {output_file}")
    print()
    
    # Connect to database
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        from app.models.bot import Bot
        from app.models.api_key import APIKey
        from app.models.conversation import Conversation, Message
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "source": db_url.split('@')[0] if '@' in db_url else "local",
            "api_keys": [],
            "bots": [],
            "conversations": [],
            "messages": []
        }
        
        # Export API Keys
        print("Exporting API Keys...")
        api_keys = db.query(APIKey).all()
        for key in api_keys:
            export_data["api_keys"].append({
                "id": key.id,
                "name": key.name,
                "provider": key.provider,
                "api_key": key.api_key,  # Note: This is encrypted
                "is_active": key.is_active,
                "created_at": key.created_at.isoformat() if key.created_at else None
            })
        print(f"  ✓ Exported {len(api_keys)} API keys")
        
        # Export Bots
        print("\nExporting Bots...")
        bots = db.query(Bot).all()
        for bot in bots:
            export_data["bots"].append({
                "id": bot.id,
                "name": bot.name,
                "description": bot.description,
                "provider": bot.provider,
                "model": bot.model,
                "api_key_id": bot.api_key_id,
                "api_key": bot.api_key,  # Legacy field
                "system_prompt": bot.system_prompt,
                "temperature": bot.temperature,
                "max_tokens": bot.max_tokens,
                "reasoning_effort": bot.reasoning_effort,
                "text_verbosity": bot.text_verbosity,
                "use_qdrant": bot.use_qdrant,
                "qdrant_collection": bot.qdrant_collection,
                "qdrant_top_k": bot.qdrant_top_k,
                "enable_memory": bot.enable_memory,
                "memory_max_messages": bot.memory_max_messages,
                "enable_suggestions": bot.enable_suggestions,
                "widget_title": bot.widget_title,
                "widget_color": bot.widget_color,
                "widget_greeting": bot.widget_greeting,
                "created_at": bot.created_at.isoformat() if bot.created_at else None,
                "updated_at": bot.updated_at.isoformat() if bot.updated_at else None,
                "is_active": bot.is_active
            })
            print(f"  ✓ {bot.name}")
        
        # Optionally export conversations
        if include_conversations:
            print("\nExporting Conversations...")
            conversations = db.query(Conversation).all()
            for conv in conversations:
                export_data["conversations"].append({
                    "id": conv.id,
                    "bot_id": conv.bot_id,
                    "session_id": conv.session_id,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
                })
            
            print("\nExporting Messages...")
            messages = db.query(Message).all()
            for msg in messages:
                export_data["messages"].append({
                    "id": msg.id,
                    "conversation_id": msg.conversation_id,
                    "role": msg.role,
                    "content": msg.content,
                    "rag_context": msg.rag_context,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                })
            
            print(f"  ✓ Exported {len(conversations)} conversations and {len(messages)} messages")
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Export complete!")
        print(f"\n📊 Summary:")
        print(f"   API Keys: {len(export_data['api_keys'])}")
        print(f"   Bots: {len(export_data['bots'])}")
        if include_conversations:
            print(f"   Conversations: {len(export_data['conversations'])}")
            print(f"   Messages: {len(export_data['messages'])}")
        print(f"\n💾 Saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export bots to JSON file')
    parser.add_argument('--database', help='Database URL (optional, uses default if not provided)')
    parser.add_argument('--output', help='Output JSON file (optional, auto-generated if not provided)')
    parser.add_argument('--include-conversations', action='store_true', 
                       help='Include conversation history in export')
    
    args = parser.parse_args()
    
    export_database(
        database_url=args.database,
        output_file=args.output,
        include_conversations=args.include_conversations
    )
