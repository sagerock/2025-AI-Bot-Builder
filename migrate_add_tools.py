"""
Migration: add tools_enabled, tool_config, suggested_prompts to bots table.

Run with: python migrate_add_tools.py
"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bots.db")


def migrate():
    print(f"Connecting to {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)

    is_sqlite = DATABASE_URL.startswith("sqlite")
    json_type = "TEXT" if is_sqlite else "JSONB"
    default_array = "'[]'"
    default_object = "'{}'"

    with engine.connect() as conn:
        try:
            print("Adding columns to bots table...")
            for col, default in [
                ("tools_enabled", default_array),
                ("tool_config", default_object),
                ("suggested_prompts", default_array),
            ]:
                # Use IF NOT EXISTS where possible; SQLite needs try/except
                try:
                    conn.execute(text(
                        f"ALTER TABLE bots ADD COLUMN {col} {json_type} "
                        f"DEFAULT {default} NOT NULL"
                    ))
                    print(f"  + {col}")
                except Exception as e:
                    if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                        print(f"  = {col} (already exists)")
                    else:
                        raise
            conn.commit()
            print("Migration complete.")
        except Exception as e:
            print(f"Migration failed: {e}")
            raise


if __name__ == "__main__":
    migrate()
