#!/usr/bin/env python3
"""
Database migration script to add new columns to existing tables.
Run this script after deploying code changes that add new model fields.
"""
import sys
from sqlalchemy import inspect, text
from app.database import engine
from app.config import settings


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def table_exists(table_name: str) -> bool:
    """Check if a table exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def run_migrations():
    """Run database migrations"""
    print(f"🔄 Running database migrations...")
    print(f"📊 Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'local'}")

    migrations_run = 0

    with engine.connect() as conn:
        # Migration: Add enable_suggestions column to bots table
        if not column_exists('bots', 'enable_suggestions'):
            print("  ➕ Adding enable_suggestions column to bots table...")
            conn.execute(text(
                "ALTER TABLE bots ADD COLUMN enable_suggestions BOOLEAN DEFAULT FALSE"
            ))
            conn.commit()
            migrations_run += 1
            print("     ✅ Done")
        else:
            print("  ⏭️  enable_suggestions column already exists")

        # Migration: Add enable_full_document column to bots table
        if not column_exists('bots', 'enable_full_document'):
            print("  ➕ Adding enable_full_document column to bots table...")
            conn.execute(text(
                "ALTER TABLE bots ADD COLUMN enable_full_document BOOLEAN DEFAULT TRUE"
            ))
            conn.commit()
            migrations_run += 1
            print("     ✅ Done")
        else:
            print("  ⏭️  enable_full_document column already exists")

        # Migration: Add reasoning_effort column to bots table (for GPT-5)
        if not column_exists('bots', 'reasoning_effort'):
            print("  ➕ Adding reasoning_effort column to bots table...")
            conn.execute(text(
                "ALTER TABLE bots ADD COLUMN reasoning_effort VARCHAR(20) DEFAULT 'medium'"
            ))
            conn.commit()
            migrations_run += 1
            print("     ✅ Done")
        else:
            print("  ⏭️  reasoning_effort column already exists")

        # Migration: Add text_verbosity column to bots table (for GPT-5)
        if not column_exists('bots', 'text_verbosity'):
            print("  ➕ Adding text_verbosity column to bots table...")
            conn.execute(text(
                "ALTER TABLE bots ADD COLUMN text_verbosity VARCHAR(20) DEFAULT 'medium'"
            ))
            conn.commit()
            migrations_run += 1
            print("     ✅ Done")
        else:
            print("  ⏭️  text_verbosity column already exists")

        # Migration: Add tools_enabled / tool_config / suggested_prompts to bots table (Cairn)
        # JSON columns: JSONB on Postgres, TEXT on SQLite.
        is_sqlite = engine.dialect.name == 'sqlite'
        json_type = "TEXT" if is_sqlite else "JSONB"

        if not column_exists('bots', 'tools_enabled'):
            print("  ➕ Adding tools_enabled column to bots table...")
            conn.execute(text(
                f"ALTER TABLE bots ADD COLUMN tools_enabled {json_type} DEFAULT '[]' NOT NULL"
            ))
            conn.commit()
            migrations_run += 1
            print("     ✅ Done")
        else:
            print("  ⏭️  tools_enabled column already exists")

        if not column_exists('bots', 'tool_config'):
            print("  ➕ Adding tool_config column to bots table...")
            conn.execute(text(
                f"ALTER TABLE bots ADD COLUMN tool_config {json_type} DEFAULT '{{}}' NOT NULL"
            ))
            conn.commit()
            migrations_run += 1
            print("     ✅ Done")
        else:
            print("  ⏭️  tool_config column already exists")

        if not column_exists('bots', 'suggested_prompts'):
            print("  ➕ Adding suggested_prompts column to bots table...")
            conn.execute(text(
                f"ALTER TABLE bots ADD COLUMN suggested_prompts {json_type} DEFAULT '[]' NOT NULL"
            ))
            conn.commit()
            migrations_run += 1
            print("     ✅ Done")
        else:
            print("  ⏭️  suggested_prompts column already exists")

        # Migration: Create webhooks table
        if not table_exists('webhooks'):
            print("  ➕ Creating webhooks table...")
            conn.execute(text("""
                CREATE TABLE webhooks (
                    id VARCHAR PRIMARY KEY,
                    bot_id VARCHAR NOT NULL,
                    url VARCHAR NOT NULL,
                    events TEXT NOT NULL,
                    secret VARCHAR,
                    is_active BOOLEAN DEFAULT TRUE,
                    description VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    total_calls VARCHAR DEFAULT '0',
                    last_called_at TIMESTAMP,
                    last_status_code VARCHAR,
                    last_error TEXT,
                    FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
                )
            """))
            conn.commit()
            migrations_run += 1
            print("     ✅ Done")
        else:
            print("  ⏭️  webhooks table already exists")

    if migrations_run > 0:
        print(f"\n✅ Successfully ran {migrations_run} migration(s)")
    else:
        print(f"\n✨ Database is up to date (0 migrations needed)")

    return migrations_run


if __name__ == "__main__":
    try:
        migrations_count = run_migrations()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
