# Flyer Industries Dashboard - Supabase Deployment

## 🚀 Quick Deploy to Supabase

### Option A: Supabase Storage (Static Hosting)

1. **Go to Supabase Dashboard:**
   - URL: https://supabase.com/dashboard/project/kidbbtdnhtncxtaqqgcp

2. **Create Storage Bucket:**
   - Navigate to "Storage" in sidebar
   - Click "New Bucket"
   - Name: `dashboard`
   - Enable "Public bucket"
   - Click "Save"

3. **Upload Files:**
   - Click on `dashboard` bucket
   - Click "Upload files"
   - Select: `index.html`
   - Upload

4. **Access Dashboard:**
   - Your URL will be:
   ```
   https://kidbbtdnhtncxtaqqgcp.supabase.co/storage/v1/object/public/dashboard/index.html
   ```

### Option B: Supabase Edge Functions (Better Performance)

1. **Install Supabase CLI:**
   ```bash
   npm install -g supabase
   ```

2. **Login:**
   ```bash
   supabase login
   ```

3. **Link Project:**
   ```bash
   supabase link --project-ref kidbbtdnhtncxtaqqgcp
   ```

4. **Deploy:**
   ```bash
   supabase functions deploy dashboard
   ```

### Option C: Custom Domain (Recommended for Production)

1. **Add Custom Domain:**
   - Go to Settings → Storage → Custom Domain
   - Add: `dashboard.flyerindustries.com`
   - Configure DNS as instructed

2. **Or use Vercel/Netlify with Supabase backend:**
   - Deploy frontend to Vercel
   - Connect to Supabase for data
   - Best of both worlds!

## 🔧 Recommended Setup

### Best Architecture:
```
Vercel/Netlify (Frontend) ←→ Supabase (Database + Auth)
```

This gives you:
- ✅ Fast global CDN
- ✅ Perfect JavaScript execution
- ✅ Direct Supabase connection
- ✅ Free custom domains

### Steps for Vercel:
1. Push code to GitHub
2. Import to Vercel
3. Add environment variables:
   ```
   SUPABASE_URL=https://kidbbtdnhtncxtaqqgcp.supabase.co
   SUPABASE_KEY=sb_publishable_9tYmqkG3w3UWYToiuzzoSw_KNib98xb
   ```
4. Deploy!

## 📊 Current Status

- Database: ✅ Connected to Supabase
- Tables: ✅ Created (businesses, monthly_summaries, etc.)
- Frontend: ✅ Ready for deployment
- Next: Choose deployment option above

## 🎯 My Recommendation

**Use Vercel for frontend + Supabase for data**

This is the most reliable setup and it's FREE!

Want me to set this up? I can:
1. Create vercel.json config
2. Set up environment variables
3. Give you one-click deploy button
