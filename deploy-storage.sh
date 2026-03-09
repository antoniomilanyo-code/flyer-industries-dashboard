#!/bin/bash
# Deploy to Supabase Storage

SUPABASE_URL="https://kidbbtdnhtncxtaqqgcp.supabase.co"
SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtpZGJidGRuaHRuY3h0YXFxZ2NwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjkyOTE4MywiZXhwIjoyMDg4NTA1MTgzfQ.HK2a_lvd6m0gSbE2pRkfVEzD0TAkYzpbujaxHs3SHK4"

echo "🚀 Deploying to Supabase Storage..."

# Create bucket
echo "📦 Creating bucket..."
curl -X POST "$SUPABASE_URL/storage/v1/bucket" \
  -H "Authorization: Bearer $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "dashboard",
    "name": "dashboard",
    "public": true
  }'

echo ""
echo "📤 Uploading index.html..."

# Upload file
curl -X POST "$SUPABASE_URL/storage/v1/object/dashboard/index.html" \
  -H "Authorization: Bearer $SERVICE_KEY" \
  -H "Content-Type: text/html" \
  --data-binary @/root/.openclaw/workspace/docs/index.html

echo ""
echo "✅ Done!"
echo ""
echo "🌐 Your dashboard:"
echo "$SUPABASE_URL/storage/v1/object/public/dashboard/index.html"
