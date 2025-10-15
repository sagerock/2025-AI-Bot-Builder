# Import/Export Guide 📦

Easily backup and transfer your bots between systems using these scripts!

## Quick Start

### Export Your Bots (Backup)

```bash
# Export all bots from local database
python3 export_bots.py

# Creates: bot_export_20241015_143022.json
```

### Import Bots to Another System

```bash
# Import to local database
python3 import_bots.py my_bots_backup.json

# Import to Railway PostgreSQL
python3 import_bots.py my_bots_backup.json --database "postgresql://..."
```

---

## Use Cases

### 🔄 Migrate Local Bots to Railway

**Step 1: Export from local**
```bash
python3 export_bots.py --output my_bots.json
```

**Step 2: Get Railway PostgreSQL URL**
- Go to https://railway.app/dashboard
- Click your PostgreSQL service
- Copy "Postgres Connection URL"

**Step 3: Import to Railway**
```bash
python3 import_bots.py my_bots.json --database "postgresql://postgres:xxx@xxx.rlwy.net:12345/railway"
```

**Done!** Your bots are now on Railway permanently! 🎉

---

### 💾 Daily Backup

Create a backup of all your bots:

```bash
# Backup with custom name
python3 export_bots.py --output backups/daily_backup_$(date +%Y%m%d).json

# Include conversation history too
python3 export_bots.py --output full_backup.json --include-conversations
```

---

### 🔄 Sync Between Environments

**From Local to Production:**
```bash
# Export local
python3 export_bots.py --output local_bots.json

# Import to production
python3 import_bots.py local_bots.json --database "$PRODUCTION_DATABASE_URL"
```

**From Production to Local:**
```bash
# Export from production
python3 export_bots.py --database "$PRODUCTION_DATABASE_URL" --output prod_bots.json

# Import to local
python3 import_bots.py prod_bots.json
```

---

### 👥 Share Bots with Team

**Export specific bot for sharing:**
1. Export all bots: `python3 export_bots.py`
2. Edit the JSON file to keep only the bots you want to share
3. Share the JSON file with your team
4. They import: `python3 import_bots.py shared_bots.json`

---

### 🔧 Clone Bot to Different Environment

```bash
# Export from dev
python3 export_bots.py --database "sqlite:///dev.db" --output dev_bots.json

# Import to staging
python3 import_bots.py dev_bots.json --database "postgresql://staging..."

# Import to production
python3 import_bots.py dev_bots.json --database "postgresql://production..."
```

---

## Export Options

### Basic Export
```bash
python3 export_bots.py
```
Exports:
- ✅ All bots
- ✅ API keys (encrypted)
- ⊘ No conversation history

### Full Export (with conversations)
```bash
python3 export_bots.py --include-conversations
```
Exports:
- ✅ All bots
- ✅ API keys (encrypted)
- ✅ All conversations
- ✅ All messages

### Custom Output File
```bash
python3 export_bots.py --output my_backup.json
```

### Export from Specific Database
```bash
# From Railway
python3 export_bots.py --database "postgresql://..." --output railway_bots.json

# From local SQLite
python3 export_bots.py --database "sqlite:///./data/botbuilder.db"
```

---

## Import Options

### Basic Import (Update Existing)
```bash
python3 import_bots.py my_bots.json
```
- Updates existing bots with same ID
- Creates new bots if they don't exist

### Skip Existing Bots
```bash
python3 import_bots.py my_bots.json --skip-existing
```
- Only imports new bots
- Skips bots that already exist

### Import to Specific Database
```bash
# To Railway PostgreSQL
python3 import_bots.py my_bots.json --database "postgresql://..."

# To different SQLite file
python3 import_bots.py my_bots.json --database "sqlite:///other.db"
```

---

## JSON File Format

The export file is a simple JSON format you can view/edit:

```json
{
  "export_date": "2024-10-15T14:30:22",
  "source": "local",
  "api_keys": [
    {
      "id": "...",
      "name": "Anthropic Main",
      "provider": "anthropic",
      "api_key": "encrypted...",
      "is_active": true
    }
  ],
  "bots": [
    {
      "id": "...",
      "name": "Personal Jurisdiction Bot",
      "description": "Legal assistant...",
      "provider": "anthropic",
      "model": "claude-sonnet-4-5-20250929",
      "system_prompt": "You are a...",
      "temperature": 70,
      "max_tokens": 8192,
      ...
    }
  ]
}
```

You can manually edit this file to:
- Remove bots you don't want to import
- Change bot names or settings
- Update model versions
- etc.

---

## Automated Backup Script

Create a cron job or scheduled task:

**backup_bots.sh:**
```bash
#!/bin/bash
cd "/Volumes/T7/Scripts/AI Bot Builder"
python3 export_bots.py --output "backups/backup_$(date +%Y%m%d_%H%M%S).json"

# Keep only last 30 days
find backups/ -name "backup_*.json" -mtime +30 -delete
```

Make it executable and add to crontab:
```bash
chmod +x backup_bots.sh

# Run daily at 2am
crontab -e
# Add: 0 2 * * * /path/to/backup_bots.sh
```

---

## Troubleshooting

### "Database connection failed"
- Check your database URL is correct
- For Railway, make sure you're using the **public** URL (ends with `.rlwy.net`)
- Test connection: `railway variables` to see your DATABASE_URL

### "Bot already exists"
- Use `--skip-existing` to skip duplicates
- Or the default behavior will **update** existing bots

### "Missing API key"
- API keys are exported as encrypted strings
- They'll work when imported to new system
- You may need to recreate API keys if encryption key differs

### "Large JSON file"
- If you included conversations (`--include-conversations`)
- Consider exporting without history for faster transfers
- Or split into multiple files

---

## Best Practices

### ✅ DO:
- **Backup regularly** - Run export daily/weekly
- **Test imports** - Try importing to test database first
- **Version control** - Keep exports in git (remove API keys first!)
- **Document changes** - Add notes to JSON exports

### ⚠️ DON'T:
- Share exports with API keys publicly
- Forget to backup before major changes
- Import without testing first
- Delete original database until import verified

---

## Quick Reference

| Task | Command |
|------|---------|
| Backup local bots | `python3 export_bots.py` |
| Backup with conversations | `python3 export_bots.py --include-conversations` |
| Import to local | `python3 import_bots.py file.json` |
| Import to Railway | `python3 import_bots.py file.json --database "postgresql://..."` |
| Skip duplicates | `python3 import_bots.py file.json --skip-existing` |
| Custom filename | `python3 export_bots.py --output myfile.json` |

---

## Example Workflows

### Daily Backup
```bash
python3 export_bots.py --output "backups/daily_$(date +%Y%m%d).json"
```

### Deploy to Railway
```bash
# 1. Export local
python3 export_bots.py --output prod_ready.json

# 2. Import to Railway
python3 import_bots.py prod_ready.json --database "$RAILWAY_DATABASE_URL"
```

### Clone Production to Staging
```bash
# Export from prod
python3 export_bots.py --database "$PROD_DB" --output prod_bots.json

# Import to staging
python3 import_bots.py prod_bots.json --database "$STAGING_DB"
```

### Share Single Bot
```bash
# 1. Export all
python3 export_bots.py --output all_bots.json

# 2. Edit all_bots.json - keep only the bot you want to share

# 3. Share the edited file
# Team member imports:
python3 import_bots.py all_bots.json
```

---

Need help? Check the scripts' help:
```bash
python3 export_bots.py --help
python3 import_bots.py --help
```
