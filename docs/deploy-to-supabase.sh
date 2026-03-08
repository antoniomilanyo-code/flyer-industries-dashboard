#!/bin/bash
# Deploy Flyer Industries Dashboard to Supabase Storage

echo "🚀 Deploying Flyer Industries Dashboard to Supabase..."

# Supabase project details
PROJECT_ID="kidbbtdnhtncxtaqqgcp"
BUCKET_NAME="dashboard"
SUPABASE_URL="https://kidbbtdnhtncxtaqqgcp.supabase.co"

# Check if supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Installing..."
    npm install -g supabase
fi

# Login to Supabase (if needed)
echo "📋 Make sure you're logged in: supabase login"

# Link to project
echo "🔗 Linking to project..."
supabase link --project-ref $PROJECT_ID

# Create storage bucket if not exists
echo "📦 Creating storage bucket..."
supabase storage create $BUCKET_NAME --public || echo "Bucket may already exist"

# Upload files
echo "📤 Uploading dashboard files..."
supabase storage upload $BUCKET_NAME ./index.html index.html
supabase storage upload $BUCKET_NAME ./test-navigation.js test-navigation.js

# Get public URL
echo "✅ Deployment complete!"
echo ""
echo "🌐 Dashboard URL:"
echo "$SUPABASE_URL/storage/v1/object/public/$BUCKET_NAME/index.html"
echo ""
echo "📱 To use a custom domain, configure in Supabase Dashboard:"
echo "Settings → Storage → Custom Domain"
