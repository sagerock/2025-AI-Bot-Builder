#!/bin/bash
# Simple script to push your local bots to Railway PostgreSQL

echo "🚀 Pushing Bots to Railway"
echo "=========================="
echo ""

# Step 1: Export local bots
echo "📦 Step 1: Exporting local bots..."
python3 export_bots.py --output railway_upload.json

if [ $? -ne 0 ]; then
    echo "❌ Export failed!"
    exit 1
fi

echo ""
echo "✅ Export complete: railway_upload.json"
echo ""

# Step 2: Get Railway PostgreSQL URL
echo "🔗 Step 2: Getting Railway database URL..."
RAILWAY_DB_URL=$(railway variables --json | python3 -c "import sys, json; data = json.load(sys.stdin); print([v['value'] for v in data if v['name'] == 'DATABASE_URL'][0] if any(v['name'] == 'DATABASE_URL' for v in data) else '')" 2>/dev/null)

if [ -z "$RAILWAY_DB_URL" ]; then
    echo "⚠️  Could not auto-detect Railway database URL"
    echo ""
    echo "Please get your PostgreSQL URL from Railway:"
    echo "1. Go to https://railway.app/dashboard"
    echo "2. Click on PostgreSQL service"
    echo "3. Copy the 'Postgres Connection URL'"
    echo ""
    read -p "Paste Railway PostgreSQL URL here: " RAILWAY_DB_URL
fi

# Convert internal URL to external if needed
if [[ $RAILWAY_DB_URL == *"railway.internal"* ]]; then
    echo "⚠️  Detected internal URL. Please provide the PUBLIC PostgreSQL URL"
    echo "   (It should contain '.rlwy.net' or similar, not '.railway.internal')"
    echo ""
    read -p "Paste PUBLIC Railway PostgreSQL URL: " RAILWAY_DB_URL
fi

echo ""
echo "Database: ${RAILWAY_DB_URL:0:30}...***"
echo ""

# Step 3: Import to Railway
echo "📤 Step 3: Importing to Railway PostgreSQL..."
python3 import_bots.py railway_upload.json --database "$RAILWAY_DB_URL"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Import failed!"
    echo ""
    echo "Troubleshooting:"
    echo "1. Make sure the PostgreSQL URL is the PUBLIC url (ends with .rlwy.net)"
    echo "2. Check Railway dashboard to verify PostgreSQL service is running"
    echo "3. Try manually: python3 import_bots.py railway_upload.json --database 'YOUR_URL'"
    exit 1
fi

echo ""
echo "🎉 Success! Your bots are now on Railway!"
echo ""
echo "Next steps:"
echo "1. Visit: https://web-production-b1b3e.up.railway.app/login"
echo "2. Login with your credentials"
echo "3. Check the admin panel to see your bots"
echo ""
echo "✨ Your bots are now permanent on Railway!"
