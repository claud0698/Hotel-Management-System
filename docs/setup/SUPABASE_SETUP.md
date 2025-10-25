# Supabase + Cloud Run Deployment Guide

**Total Cost: $0/month** (100% FREE for small apps) 🎉

This guide shows you how to deploy your Kos Management Dashboard using:
- **Supabase** (FREE PostgreSQL database - 500MB storage)
- **Cloud Run** (FREE - 2M requests/month)

---

## 🎯 What You Get for FREE

### Supabase Free Tier:
- ✅ 500 MB database storage
- ✅ Unlimited API requests
- ✅ 50,000 monthly active users
- ✅ 1 GB file storage
- ✅ 2 GB bandwidth
- ✅ PostgreSQL database with extensions
- ✅ Auto-generated REST APIs
- ✅ Realtime subscriptions
- ✅ Social OAuth providers

### Cloud Run Free Tier:
- ✅ 2 million requests/month
- ✅ 360,000 GB-seconds of memory
- ✅ 180,000 vCPU-seconds

**Perfect for small to medium kos management apps!**

---

## Step 1: Create Supabase Project

1. **Go to Supabase**: https://supabase.com
2. **Sign up** with GitHub or email
3. **Create New Project**:
   - Project name: `kos-dashboard`
   - Database password: Generate a strong password (SAVE THIS!)
   - Region: **Southeast Asia (Singapore)** (closest to Indonesia)
   - Pricing plan: **Free**

4. **Wait 2-3 minutes** for project to be created

---

## Step 2: Get Database Connection String

1. In your Supabase project dashboard, go to:
   **Settings** (⚙️) → **Database** → **Connection String**

2. Select **URI** and copy the connection string. It looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
   ```

3. Replace `[YOUR-PASSWORD]` with your actual database password

4. **For SQLAlchemy (our app), modify the connection string**:
   ```
   postgresql+psycopg2://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
   ```
   Note: Added `+psycopg2` after `postgresql`

---

## Step 3: Test Local Connection

Before deploying, test that your app can connect to Supabase:

```bash
cd backend

# Create .env file
cat > .env << 'EOF'
FLASK_ENV=development
DEBUG=True
PORT=8001

# Replace with your Supabase connection string
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@db.xxxxxxxxxxxxx.supabase.co:5432/postgres

CORS_ORIGINS=*

# Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your-generated-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# Install dependencies (if not already)
pip install -r requirements.txt

# Run the app
python3 app.py
```

Visit http://localhost:8001/health - you should see:
```json
{
  "status": "ok",
  "environment": "development",
  "database": "postgresql",
  "timestamp": "2025-10-26T..."
}
```

---

## Step 4: Initialize Database (Create Tables & Admin User)

Your app automatically creates tables on startup, but you need to create an admin user.

### Option A: Using Supabase SQL Editor (Recommended)

1. Go to **SQL Editor** in Supabase dashboard
2. Click **New Query**
3. Run this SQL:

```sql
-- Check if tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';

-- Create admin user (adjust values as needed)
-- Password will be hashed: 'admin123' -> bcrypt hash
INSERT INTO users (username, email, password_hash, created_at)
VALUES (
  'admin',
  'admin@kos-dashboard.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI2aUBzLQ4Hy',  -- password: admin123
  NOW()
)
ON CONFLICT (username) DO NOTHING;

-- Verify user created
SELECT id, username, email, created_at FROM users;
```

4. To generate your own password hash, run locally:
```python
python3 -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('YOUR_PASSWORD'))"
```

### Option B: Using Python Script

Create `backend/create_admin.py`:

```python
#!/usr/bin/env python3
"""Create admin user in Supabase database"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Base

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("Error: DATABASE_URL not set in .env")
    exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Create tables if they don't exist
Base.metadata.create_all(engine)

# Check if admin exists
existing_admin = session.query(User).filter_by(username='admin').first()
if existing_admin:
    print("Admin user already exists!")
    print(f"Username: {existing_admin.username}")
    print(f"Email: {existing_admin.email}")
else:
    # Create admin user
    admin = User(
        username='admin',
        email='admin@kos-dashboard.com'
    )
    admin.set_password('admin123')  # Change this password!

    session.add(admin)
    session.commit()

    print("Admin user created successfully!")
    print(f"Username: admin")
    print(f"Email: admin@kos-dashboard.com")
    print(f"Password: admin123")
    print("\n⚠️  IMPORTANT: Change this password after first login!")

session.close()
```

Run it:
```bash
cd backend
python3 create_admin.py
```

---

## Step 5: Deploy to Cloud Run

Now deploy your app to GCP Cloud Run:

```bash
# Make sure you're in the backend directory
cd backend

# Login to GCP
gcloud auth login

# Set your project (or create new one)
gcloud config set project YOUR_PROJECT_ID

# Enable Cloud Run API
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy to Cloud Run
gcloud run deploy kos-api \
  --source . \
  --region=asia-southeast2 \
  --platform=managed \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=3 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300
```

This will:
1. Build your Docker container
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Give you a URL like: `https://kos-api-xxxxx-de.a.run.app`

---

## Step 6: Configure Environment Variables in Cloud Run

```bash
# Set DATABASE_URL (use your Supabase connection string)
gcloud run services update kos-api \
  --region=asia-southeast2 \
  --set-env-vars="DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@db.xxxxxxxxxxxxx.supabase.co:5432/postgres"

# Set other environment variables
gcloud run services update kos-api \
  --region=asia-southeast2 \
  --set-env-vars="FLASK_ENV=production,DEBUG=False,CORS_ORIGINS=https://your-frontend.vercel.app"

# Generate and set JWT secret
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
gcloud run services update kos-api \
  --region=asia-southeast2 \
  --set-env-vars="JWT_SECRET_KEY=${JWT_SECRET}"
```

### Better: Use Secret Manager (Recommended for Production)

```bash
# Enable Secret Manager
gcloud services enable secretmanager.googleapis.com

# Create secret for DATABASE_URL
echo -n "postgresql+psycopg2://postgres:YOUR_PASSWORD@db.xxxxxxxxxxxxx.supabase.co:5432/postgres" | \
  gcloud secrets create database-url --data-file=-

# Create secret for JWT key
python3 -c "import secrets; print(secrets.token_urlsafe(32))" | \
  gcloud secrets create jwt-secret-key --data-file=-

# Get project number
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding database-url \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding jwt-secret-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update Cloud Run to use secrets
gcloud run services update kos-api \
  --region=asia-southeast2 \
  --update-secrets=DATABASE_URL=database-url:latest \
  --update-secrets=JWT_SECRET_KEY=jwt-secret-key:latest \
  --set-env-vars="FLASK_ENV=production,DEBUG=False"
```

---

## Step 7: Test Your Deployment

```bash
# Get your Cloud Run URL
SERVICE_URL=$(gcloud run services describe kos-api \
  --region=asia-southeast2 \
  --format='value(status.url)')

echo "Your API is live at: $SERVICE_URL"

# Test health endpoint
curl $SERVICE_URL/health

# Test API root
curl $SERVICE_URL/api

# Test login (should work if admin user was created)
curl -X POST $SERVICE_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

You should see a JWT token in the response!

---

## Step 8: Update Frontend

Update your frontend to use the Cloud Run URL:

In your frontend `.env` or `.env.production`:
```bash
VITE_API_URL=https://kos-api-xxxxx-de.a.run.app/api
```

Or directly in your frontend code:
```typescript
// frontend/src/config.ts
export const API_URL = import.meta.env.VITE_API_URL ||
  'https://kos-api-xxxxx-de.a.run.app/api';
```

---

## Step 9: Seed Sample Data (Optional)

If you want to add sample rooms and tenants:

1. Update your existing seed scripts to work with Supabase
2. Run locally:
```bash
cd backend
python3 seed_july_2025.py  # or your preferred seed script
```

Or create a Cloud Run Job to seed remotely.

---

## 🔒 Security Checklist

- [ ] Changed default admin password
- [ ] Set CORS_ORIGINS to your frontend URL only (not `*`)
- [ ] DATABASE_URL stored in Secret Manager (not env vars)
- [ ] JWT_SECRET_KEY is random and stored securely
- [ ] Enable Row Level Security (RLS) in Supabase if needed
- [ ] Set up Supabase Auth if you want social login

---

## 📊 Monitoring

### Supabase Dashboard:
- **Database** → **Tables** - View all data
- **Database** → **Logs** - Query logs
- **Settings** → **API** - API keys and settings

### Cloud Run Dashboard:
```bash
# View logs
gcloud run services logs read kos-api \
  --region=asia-southeast2 \
  --limit=50

# View metrics
gcloud run services describe kos-api --region=asia-southeast2
```

Or visit: https://console.cloud.google.com/run

---

## 💡 Tips & Best Practices

1. **Connection Pooling**: Supabase handles this automatically
2. **Backups**: Supabase does daily backups (free tier: 7 days retention)
3. **Indexes**: Add indexes for frequently queried columns:
   ```sql
   CREATE INDEX idx_tenants_status ON tenants(status);
   CREATE INDEX idx_payments_tenant_id ON payments(tenant_id);
   CREATE INDEX idx_payments_status ON payments(status);
   ```
4. **Monitor Usage**: Check Supabase dashboard → **Settings** → **Usage**
5. **Scale Up**: If you exceed free tier, upgrade to Supabase Pro ($25/month)

---

## 🚨 Troubleshooting

### Connection Refused
```bash
# Test connection from Cloud Run
gcloud run services update kos-api \
  --region=asia-southeast2 \
  --set-env-vars="DEBUG=True"

# Check logs
gcloud run services logs read kos-api --region=asia-southeast2 --limit=100
```

### SSL Error
If you see SSL errors, add `?sslmode=require` to connection string:
```
postgresql+psycopg2://postgres:pass@db.xxx.supabase.co:5432/postgres?sslmode=require
```

### Password Authentication Failed
- Double-check password in Supabase dashboard
- Make sure there are no special characters that need URL encoding
- Try resetting database password in Supabase Settings

### Tables Not Created
Run this in Supabase SQL Editor:
```sql
-- Check if tables exist
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- If tables don't exist, your app should create them on first run
-- Or you can create them manually from models.py
```

---

## 🎯 Cost Breakdown

| Service | Free Tier | Your Usage | Cost |
|---------|-----------|------------|------|
| Supabase | 500MB DB, Unlimited requests | ~50-100MB | **$0** |
| Cloud Run | 2M requests/month | ~10K requests/month | **$0** |
| **Total** | | | **$0/month** 🎉 |

---

## 🔄 CI/CD with GitHub Actions (Optional)

Create `.github/workflows/deploy-cloudrun.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - id: auth
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v1
        with:
          service: kos-api
          region: asia-southeast2
          source: ./backend
          env_vars: |
            FLASK_ENV=production
            DEBUG=False
          secrets: |
            DATABASE_URL=database-url:latest
            JWT_SECRET_KEY=jwt-secret-key:latest
```

---

## 📚 Useful Commands

```bash
# View Cloud Run services
gcloud run services list

# Update Cloud Run
gcloud run services update kos-api --region=asia-southeast2 --memory=1Gi

# View logs in real-time
gcloud run services logs tail kos-api --region=asia-southeast2

# Delete service (to start over)
gcloud run services delete kos-api --region=asia-southeast2

# Get service URL
gcloud run services describe kos-api \
  --region=asia-southeast2 \
  --format='value(status.url)'
```

---

## 🎉 You're Done!

Your Kos Management Dashboard is now running on:
- ✅ **Backend**: Cloud Run (FREE)
- ✅ **Database**: Supabase PostgreSQL (FREE)
- ✅ **Total Cost**: $0/month

Next steps:
1. Update frontend to use Cloud Run URL
2. Deploy frontend to Vercel (also FREE)
3. Set up custom domain (optional)
4. Enable HTTPS (automatic with Cloud Run)

---

## 🆙 Upgrade Path

When you outgrow the free tier:

**Supabase Pro** ($25/month):
- 8GB database
- 100GB bandwidth
- 50GB file storage
- No pausing after 1 week inactivity

**Cloud Run**: Scales automatically, only pay for actual usage

Total cost even after upgrade: ~$25-35/month

---

## 📞 Support

- Supabase Docs: https://supabase.com/docs
- Cloud Run Docs: https://cloud.google.com/run/docs
- Supabase Discord: https://discord.supabase.com

---

**Happy deploying! 🚀**
