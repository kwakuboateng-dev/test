#!/bin/bash
# Script to remove API_HOST and API_PORT from backend .env file

ENV_FILE="/Users/papa/Desktop/app/backend/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found at $ENV_FILE"
    exit 1
fi

echo "🔧 Removing API_HOST and API_PORT from .env..."

# Create backup
cp "$ENV_FILE" "$ENV_FILE.backup"
echo "✅ Backup created: $ENV_FILE.backup"

# Remove the lines
sed -i '' '/^API_HOST=/d' "$ENV_FILE"
sed -i '' '/^API_PORT=/d' "$ENV_FILE"

echo "✅ Removed API_HOST and API_PORT from .env"
echo ""
echo "You can now start the backend with:"
echo "  cd /Users/papa/Desktop/app/backend"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000"
