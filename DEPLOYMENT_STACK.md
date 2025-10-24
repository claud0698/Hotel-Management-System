# Deployment Stack Setup
## Vercel + Supabase + Flask Backend

**Recommended Production Stack for Kos Management Dashboard**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frontend Layer:                                           │
│  ┌──────────────────────────────────────────────┐         │
│  │ Vercel (React + Vite)                       │         │
│  │ • Hosted globally on CDN                    │         │
│  │ • Auto-deploys from GitHub                  │         │
│  │ • Free tier or Pro ($20/month)              │         │
│  │ • URL: https://app.yourdomain.com           │         │
│  └──────────────────────────────────────────────┘         │
│           ↓ API calls (REST)                              │
│  Backend Layer:                                            │
│  ┌──────────────────────────────────────────────┐         │
│  │ Flask API Server (Your VPS/Cloud)           │         │
│  │ • DigitalOcean App Platform ($5-20)         │         │
│  │ • Or any server you prefer                  │         │
│  │ • URL: https://api.yourdomain.com           │         │
│  └──────────────────────────────────────────────┘         │
│           ↓ Database queries (SQL)                        │
│  Data Layer:                                               │
│  ┌──────────────────────────────────────────────┐         │
│  │ Supabase (PostgreSQL + Features)            │         │
│  │ • Free tier: 500MB storage, unlimited API  │         │
│  │ • Managed backups & monitoring              │         │
│  │ • Connection pooling included               │         │
│  │ • URL: postgresql://...supabase.com         │         │
│  └──────────────────────────────────────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Cost Breakdown:
├─ Frontend (Vercel)     = $0 (free tier)
├─ Backend (Your choice) = $5-20/month
├─ Database (Supabase)   = $0 (free tier)
├─ Domain               = $1-2/month
└─ TOTAL               = $6-23/month starting
```

---

## Step 1: Setup Supabase (5 minutes)

### 1.1 Create Supabase Account

1. Go to **https://supabase.com**
2. Click "Start your project"
3. Sign up with GitHub (easiest)
4. Create organization (free tier)
5. Create project:
   - **Name**: `kos-management`
   - **Password**: Strong password (save it!)
   - **Region**: Choose closest to you
   - Wait 2-3 minutes for initialization

### 1.2 Get Connection String

1. In Supabase dashboard, go to **Settings → Database**
2. Find **"Connection Pooler"** section
3. Copy the connection string:
   ```
   postgresql://postgres.xxxxx:password@aws-0-region.pooler.supabase.com:6543/postgres
   ```

### 1.3 Update Backend .env

Replace DATABASE_URL in your `backend/.env`:

```bash
# OLD (SQLite)
DATABASE_URL=sqlite:///kos.db

# NEW (Supabase)
DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-region.pooler.supabase.com:6543/postgres

FLASK_ENV=production
DEBUG=False
```

### 1.4 Create Tables in Supabase

```bash
cd backend
source venv/bin/activate

# This creates all tables in Supabase
python app.py

# Then seed with data (optional)
python seed.py
```

Done! Your database is now in Supabase ✅

---

## Step 2: Setup Vercel (5 minutes)

### 2.1 Push Frontend to GitHub

Make sure your code is on GitHub:

```bash
cd /path/to/kos-database/frontend

# Add GitHub remote if not already there
git remote add origin https://github.com/yourusername/kos-database

# Push frontend folder (or push from root)
git push origin main
```

### 2.2 Connect Vercel to GitHub

1. Go to **https://vercel.com**
2. Sign up with GitHub
3. Click **"New Project"**
4. Select your `kos-database` repository
5. Configure build settings:
   - **Framework Preset**: React
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
   - **Root Directory**: `frontend`
6. Click **"Deploy"**

Wait ~2 minutes... your app is live! 🎉

### 2.3 Add Environment Variables

1. In Vercel dashboard, go to **Settings → Environment Variables**
2. Add variable:
   ```
   Name:  VITE_API_URL
   Value: https://api.yourdomain.com
   ```
   (or use your backend URL)

3. Click **"Add Environment Variable"**
4. **Redeploy** to apply changes:
   - Click "Deployments" tab
   - Click latest deployment
   - Click "Redeploy"

### 2.4 Access Your App

Your frontend is now live at:
```
https://kos-management.vercel.app
(or custom domain)
```

---

## Step 3: Setup Backend (Your Choice)

### Option A: DigitalOcean App Platform (Recommended)

**Cost**: $5-20/month | **Setup**: 15 minutes

```bash
# 1. Create DigitalOcean account
# https://www.digitalocean.com

# 2. Create App from GitHub
# - Click "Create" → "Apps"
# - Connect GitHub account
# - Select kos-database repo
# - Configure:
#   - Source directory: backend/
#   - Build command: pip install -r requirements.txt
#   - Run command: gunicorn -w 4 -b 0.0.0.0:8080 app:app

# 3. Set environment variables
# - Add DATABASE_URL (from Supabase)
# - Add SECRET_KEY (generate new one)
# - Add JWT_SECRET_KEY (generate new one)

# 4. Click "Create Resources"
# - Wait 5-10 minutes for deployment
# - Get your backend URL
```

Update Vercel environment variable with your DigitalOcean URL.

### Option B: Heroku

**Cost**: $5-7/month | **Setup**: 10 minutes

```bash
# 1. Install Heroku CLI
brew install heroku

# 2. Login
heroku login

# 3. Create app
heroku create kos-api

# 4. Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev -a kos-api

# 5. Set config variables
heroku config:set DATABASE_URL=postgresql://... -a kos-api
heroku config:set SECRET_KEY=your-secret-key -a kos-api

# 6. Deploy
git push heroku main

# 7. Initialize database
heroku run python seed.py -a kos-api
```

### Option C: Self-hosted VPS

**Cost**: $3-10/month | **Setup**: 20 minutes

Use any VPS provider (Linode, Vultr, AWS EC2, etc.)

---

## Step 4: Setup Custom Domain (Optional)

### 4.1 Buy Domain

- Namecheap: ~$8/year
- Google Domains: ~$10/year
- GoDaddy: ~$10/year

### 4.2 Connect to Vercel

1. In Vercel dashboard → Settings → Domains
2. Add your domain
3. Update DNS at your registrar:
   ```
   Type: A
   Name: @
   Value: 76.76.19.132

   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```
4. Wait ~15-30 minutes for DNS propagation

Your app is now at: `https://yourdomain.com`

### 4.3 Backend Domain (Optional)

For API, use subdomain:
```
CNAME: api
Value: your-backend-provider.com
```

Or just use the backend provider's URL directly.

---

## Step 5: Configure CORS

Update your Flask backend `backend/.env`:

```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://kos-management.vercel.app,http://localhost:5173
```

Restart backend for changes to take effect.

---

## Environment Variables Checklist

### Supabase
- ✅ Create project
- ✅ Get connection pooler URL
- ✅ Save DATABASE_URL

### Vercel
- ✅ Push code to GitHub
- ✅ Connect GitHub to Vercel
- ✅ Add `VITE_API_URL` env var
- ✅ Deploy

### Backend
- ✅ Update `DATABASE_URL` to Supabase
- ✅ Update `CORS_ORIGINS` to include Vercel URL
- ✅ Generate new `SECRET_KEY` and `JWT_SECRET_KEY`
- ✅ Deploy to DigitalOcean/Heroku/VPS

### Domain (Optional)
- ✅ Buy domain
- ✅ Connect to Vercel
- ✅ Update API endpoint in Vercel env vars

---

## Quick Commands Reference

### Supabase Database
```bash
# Connect to database locally for testing
psql postgresql://postgres:PASSWORD@HOST:6543/postgres

# Or in Python
from sqlalchemy import create_engine
engine = create_engine('postgresql://...')
```

### Vercel Deployment
```bash
# Trigger redeploy from git
git push origin main
# Vercel auto-deploys!

# Or deploy from CLI
npm install -g vercel
vercel deploy --prod
```

### Backend Logs
```bash
# DigitalOcean
# Dashboard → Apps → Select app → Runtime logs

# Heroku
heroku logs --tail -a kos-api

# VPS
ssh user@server
tail -f /var/log/your-app.log
```

---

## Monitoring & Analytics

### Vercel
- Built-in Web Analytics
- Real-time logs
- Performance metrics
- Error tracking

### Supabase
- Dashboard with stats
- Query performance monitoring
- Connection status
- Backup status

### Backend
- Application logs
- Error tracking (optional: Sentry)
- Performance monitoring (optional: New Relic)

---

## Security Checklist

- ✅ Environment variables not in git (use .gitignore)
- ✅ SSL/TLS enabled (automatic with Vercel)
- ✅ Supabase connection uses connection pooler
- ✅ Strong passwords for databases
- ✅ CORS configured correctly
- ✅ JWT tokens with good expiration
- ✅ API keys not exposed in frontend code
- ✅ Regular backups enabled (Supabase auto)

---

## Cost Summary

| Service | Free Tier | Paid Tier | Notes |
|---------|-----------|-----------|-------|
| Vercel | ✅ Unlimited | $20/mo | Use free tier! |
| Supabase | ✅ 500MB | $25+/mo | Free tier perfect for v1 |
| DigitalOcean | ❌ No | $5/mo | Cheapest backend option |
| Heroku | ❌ No | $7/mo | Easy deployment |
| Domain | ❌ No | $1-2/mo | Optional but recommended |
| **TOTAL** | | **$6-27/month** | Scales only as needed |

---

## Troubleshooting

### Frontend can't connect to API
- Check `VITE_API_URL` in Vercel env vars
- Check backend is running and accessible
- Check CORS_ORIGINS in backend .env
- Browser console shows specific error

### Database connection fails
- Verify CONNECTION POOLER URL (not regular URL)
- Check password in connection string
- Check firewall allows connections
- Test: `psql postgresql://...`

### Vercel deployment failed
- Check build logs in Vercel dashboard
- Ensure `frontend/` folder has package.json
- Check Node.js version compatible
- Rebuild: push to git again

### Supabase storage exceeded
- Check current usage in Supabase dashboard
- Upgrade to paid plan ($25/mo = 100GB)
- Or delete old data

---

## Next Steps

1. ✅ Create Supabase account (5 min)
2. ✅ Update backend DATABASE_URL (2 min)
3. ✅ Create tables in Supabase (1 min)
4. ✅ Push frontend to GitHub (2 min)
5. ✅ Connect to Vercel (3 min)
6. ✅ Deploy backend (10-15 min)
7. ✅ Add environment variables (5 min)
8. ✅ Test API connection (5 min)
9. ✅ Setup custom domain (optional, 15 min)
10. ✅ Monitor and celebrate! 🎉

**Total setup time: ~45 minutes**

---

## Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/

---

**Deployment Stack Guide v1.0**
**Stack: Vercel + Supabase + Flask**
**Last Updated**: October 24, 2025

