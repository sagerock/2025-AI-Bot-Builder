"""
Migration script to move bots from SQLite to PostgreSQL
Run this AFTER deploying to Railway and getting your PostgreSQL connection string

Usage:
  python3 migrate_to_postgres.py postgresql://user:pass@host:5432/dbname
"""
import sys
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def migrate_database(postgres_url):
    """Migrate data from SQLite to PostgreSQL"""
    
    # Connect to SQLite
    sqlite_path = "data/botbuilder.db"
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    pg_engine = create_engine(postgres_url)
    
    # Create tables in PostgreSQL
    from app.database import Base
    from app.models.bot import Bot
    from app.models.api_key import APIKey
    from app.models.conversation import Conversation, Message
    
    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(bind=pg_engine)
    
    SessionLocal = sessionmaker(bind=pg_engine)
    pg_session = SessionLocal()
    
    try:
        # Migrate API Keys first
        print("\nMigrating API Keys...")
        sqlite_cursor.execute("SELECT * FROM api_keys")
        api_keys = sqlite_cursor.fetchall()
        
        for row in api_keys:
            # Check if already exists
            existing = pg_session.execute(
                text("SELECT id FROM api_keys WHERE id = :id"),
                {"id": row["id"]}
            ).fetchone()
            
            if not existing:
                pg_session.execute(
                    text("""
                        INSERT INTO api_keys (id, name, provider, api_key, is_active, created_at)
                        VALUES (:id, :name, :provider, :api_key, :is_active, :created_at)
                    """),
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "provider": row["provider"],
                        "api_key": row["api_key"],
                        "is_active": row["is_active"],
                        "created_at": row["created_at"]
                    }
                )
                print(f"  ✓ Migrated API Key: {row['name']}")
        
        pg_session.commit()
        
        # Migrate Bots
        print("\nMigrating Bots...")
        sqlite_cursor.execute("SELECT * FROM bots")
        bots = sqlite_cursor.fetchall()
        
        for row in bots:
            # Check if already exists
            existing = pg_session.execute(
                text("SELECT id FROM bots WHERE id = :id"),
                {"id": row["id"]}
            ).fetchone()
            
            if not existing:
                pg_session.execute(
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
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "description": row["description"],
                        "provider": row["provider"],
                        "model": row["model"],
                        "api_key_id": row["api_key_id"],
                        "api_key": row["api_key"],
                        "system_prompt": row["system_prompt"],
                        "temperature": row["temperature"],
                        "max_tokens": row["max_tokens"],
                        "reasoning_effort": row["reasoning_effort"],
                        "text_verbosity": row["text_verbosity"],
                        "use_qdrant": row["use_qdrant"],
                        "qdrant_collection": row["qdrant_collection"],
                        "qdrant_top_k": row["qdrant_top_k"],
                        "enable_memory": row["enable_memory"],
                        "memory_max_messages": row["memory_max_messages"],
                        "enable_suggestions": row["enable_suggestions"],
                        "widget_title": row["widget_title"],
                        "widget_color": row["widget_color"],
                        "widget_greeting": row["widget_greeting"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                        "is_active": row["is_active"]
                    }
                )
                print(f"  ✓ Migrated Bot: {row['name']}")
        
        pg_session.commit()
        
        # Migrate Conversations
        print("\nMigrating Conversations...")
        sqlite_cursor.execute("SELECT * FROM conversations")
        conversations = sqlite_cursor.fetchall()
        
        for row in conversations:
            existing = pg_session.execute(
                text("SELECT id FROM conversations WHERE id = :id"),
                {"id": row["id"]}
            ).fetchone()
            
            if not existing:
                pg_session.execute(
                    text("""
                        INSERT INTO conversations (id, bot_id, session_id, created_at, updated_at)
                        VALUES (:id, :bot_id, :session_id, :created_at, :updated_at)
                    """),
                    {
                        "id": row["id"],
                        "bot_id": row["bot_id"],
                        "session_id": row["session_id"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    }
                )
        
        pg_session.commit()
        print(f"  ✓ Migrated {len(conversations)} conversations")
        
        # Migrate Messages
        print("\nMigrating Messages...")
        sqlite_cursor.execute("SELECT * FROM messages")
        messages = sqlite_cursor.fetchall()
        
        for row in messages:
            existing = pg_session.execute(
                text("SELECT id FROM messages WHERE id = :id"),
                {"id": row["id"]}
            ).fetchone()
            
            if not existing:
                pg_session.execute(
                    text("""
                        INSERT INTO messages (id, conversation_id, role, content, rag_context, created_at)
                        VALUES (:id, :conversation_id, :role, :content, :rag_context, :created_at)
                    """),
                    {
                        "id": row["id"],
                        "conversation_id": row["conversation_id"],
                        "role": row["role"],
                        "content": row["content"],
                        "rag_context": row["rag_context"],
                        "created_at": row["created_at"]
                    }
                )
        
        pg_session.commit()
        print(f"  ✓ Migrated {len(messages)} messages")
        
        print("\n✅ Migration completed successfully!")
        print(f"\nMigrated:")
        print(f"  - {len(api_keys)} API Keys")
        print(f"  - {len(bots)} Bots")
        print(f"  - {len(conversations)} Conversations")
        print(f"  - {len(messages)} Messages")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        pg_session.rollback()
    finally:
        pg_session.close()
        sqlite_conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 migrate_to_postgres.py postgresql://user:pass@host:5432/dbname")
        print("\nExample:")
        print("  python3 migrate_to_postgres.py postgresql://postgres:password@localhost:5432/botbuilder")
        sys.exit(1)
    
    postgres_url = sys.argv[1]
    print(f"Migrating from SQLite to PostgreSQL...")
    print(f"PostgreSQL URL: {postgres_url.split('@')[0]}@***")
    print()
    
    migrate_database(postgres_url)
