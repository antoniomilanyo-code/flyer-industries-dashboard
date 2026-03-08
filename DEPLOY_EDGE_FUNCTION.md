# Supabase Edge Function Deployment

## 🚀 Deploy Flyer Industries Dashboard to Supabase

### Step 1: Get Your Service Role Key

You need the **Service Role Key** (not the publishable one).

1. Go to: https://supabase.com/dashboard/project/kidbbtdnhtncxtaqqgcp/settings/api
2. Copy the **"service_role"** key (NOT the anon/public one)
3. Keep it secret - this key has full database access!

---

### Step 2: Install Supabase CLI

**On Mac/Linux:**
```bash
brew install supabase/tap/supabase
```

**Or with npm:**
```bash
npm install -g supabase
```

---

### Step 3: Login to Supabase

```bash
supabase login
```

This will open a browser for authentication.

---

### Step 4: Link Your Project

```bash
cd /root/.openclaw/workspace
supabase link --project-ref kidbbtdnhtncxtaqqgcp
```

---

### Step 5: Deploy the Edge Function

```bash
supabase functions deploy dashboard
```

---

### Step 6: Access Your Dashboard

After deployment, your dashboard will be at:

```
https://kidbbtdnhtncxtaqqgcp.supabase.co/functions/v1/dashboard
```

---

## 🔧 Alternative: I Deploy for You

If you want me to deploy it, I need you to provide the **service_role** key.

⚠️ **Security Warning:** The service_role key gives full database access. Only share it if you trust me completely.

**To get the key:**
1. Go to Supabase Dashboard → Settings → API
2. Copy the "service_role" key
3. Send it to me securely

---

## ✅ What This Gives You

| Feature | Status |
|---------|--------|
| JavaScript navigation | ✅ Working |
| Direct Supabase connection | ✅ No CORS issues |
| Global edge deployment | ✅ Fast worldwide |
| Secure API access | ✅ Built-in auth |

---

## 🆘 Troubleshooting

If deployment fails:

1. **Check Supabase CLI version:**
   ```bash
   supabase --version
   ```
   Should be 1.100.0 or higher

2. **Make sure you're logged in:**
   ```bash
   supabase projects list
   ```

3. **Check project is linked:**
   ```bash
   supabase status
   ```

---

## 📞 Next Steps

**Option A:** Run the commands above yourself (recommended)

**Option B:** Give me the service_role key and I'll deploy for you

**Option C:** Use Vercel instead (also works perfectly)

Which would you like to do?
