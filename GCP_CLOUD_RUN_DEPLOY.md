# Deploy Backend to GCP Cloud Run

Quick guide to deploy your FastAPI backend to Google Cloud Run.

## Prerequisites

- ✅ Google Cloud account with billing enabled
- ✅ `gcloud` CLI installed
- ✅ Vercel frontend deployed (update API URL later)

---

## Step 1: Install Google Cloud SDK

### macOS:
```bash
brew install --cask google-cloud-sdk
```

### Linux:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Windows:
Download from: https://cloud.google.com/sdk/docs/install

### Verify Installation:
```bash
gcloud --version
```

---

## Step 2: Initialize GCP Project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create kos-management-prod --name="Kos Management"

# Set as active project
gcloud config set project kos-management-prod

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Set default region
gcloud config set run/region asia-southeast1
```

---

## Step 3: Create PostgreSQL Database (Cloud SQL)

```bash
# Create PostgreSQL instance (db-f1-micro = smallest, cheapest)
gcloud sql instances create kos-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-southeast1 \
  --root-password=YOUR_SECURE_ROOT_PASSWORD \
  --storage-size=10GB \
  --storage-type=HDD

# Wait for instance to be ready (takes 3-5 minutes)
gcloud sql instances list

# Create database
gcloud sql databases create kos_production --instance=kos-db

# Create user
gcloud sql users create kos_user \
  --instance=kos-db \
  --password=YOUR_SECURE_USER_PASSWORD
```

**Important**: Save these credentials securely!

---

## Step 4: Store Secrets in Secret Manager

```bash
# Get your Cloud SQL connection name
gcloud sql instances describe kos-db --format='value(connectionName)'
# Output: PROJECT_ID:REGION:kos-db

# Create DATABASE_URL secret
# Format: postgresql://USER:PASSWORD@/DATABASE?host=/cloudsql/CONNECTION_NAME
echo -n "postgresql://kos_user:YOUR_USER_PASSWORD@/kos_production?host=/cloudsql/kos-management-prod:asia-southeast1:kos-db" | \
  gcloud secrets create DATABASE_URL --data-file=-

# Create JWT secret (generate random 32-char string)
openssl rand -base64 32 | gcloud secrets create JWT_SECRET_KEY --data-file=-

# Grant Cloud Run access to secrets
PROJECT_NUMBER=$(gcloud projects describe kos-management-prod --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding DATABASE_URL \
  --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding JWT_SECRET_KEY \
  --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

---

## Step 5: Update Backend Code for Production

### Option A: Environment-based Database (Recommended)

Your `app.py` should already use `DATABASE_URL` from environment:

```python
# backend/app.py
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///kos.db')
```

This is already set up! ✅

### Option B: Create Production Config (Optional)

Create `backend/.env.production`:

```bash
DATABASE_URL=postgresql://kos_user:password@/kos_production?host=/cloudsql/PROJECT_ID:REGION:kos-db
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

---

## Step 6: Deploy to Cloud Run

```bash
cd backend

# Deploy (Cloud Run will build from Dockerfile automatically)
gcloud run deploy kos-backend \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0 \
  --timeout 60 \
  --add-cloudsql-instances kos-management-prod:asia-southeast1:kos-db \
  --set-secrets DATABASE_URL=DATABASE_URL:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest \
  --set-env-vars CORS_ORIGINS=https://your-vercel-app.vercel.app
```

**⏱️ This takes 3-5 minutes** (building Docker image + deploying)

---

## Step 7: Get Backend URL

```bash
# Get the service URL
gcloud run services describe kos-backend \
  --platform managed \
  --region asia-southeast1 \
  --format 'value(status.url)'
```

**Output example**: `https://kos-backend-xyz123-uc.a.run.app`

**Save this URL!** You'll need it for Vercel.

---

## Step 8: Test the Deployment

```bash
# Test health endpoint
curl https://YOUR_BACKEND_URL.run.app/health

# Should return:
# {"status":"ok","environment":"production","database":"postgresql","timestamp":"..."}

# Test API docs
# Visit: https://YOUR_BACKEND_URL.run.app/api/docs
```

---

## Step 9: Run Database Migrations & Seed Data

### Option A: Cloud Shell (Easiest)

```bash
# Connect to Cloud SQL
gcloud sql connect kos-db --user=kos_user --quiet

# In PostgreSQL shell:
\c kos_production
\q

# Back in your terminal, run migrations
# (You'll need to upload your migration scripts or run from Cloud Shell)
```

### Option B: Local Connection via Proxy

```bash
# Install Cloud SQL Proxy
gcloud components install cloud-sql-proxy

# Start proxy (in separate terminal)
cloud-sql-proxy kos-management-prod:asia-southeast1:kos-db

# In another terminal, run migrations with DATABASE_URL pointing to proxy
DATABASE_URL=postgresql://kos_user:password@127.0.0.1:5432/kos_production \
  python -c "from models import Base; from sqlalchemy import create_engine; engine = create_engine('postgresql://kos_user:password@127.0.0.1:5432/kos_production'); Base.metadata.create_all(engine)"

# Seed data
DATABASE_URL=postgresql://kos_user:password@127.0.0.1:5432/kos_production \
  python seed_july_2025.py
```

---

## Step 10: Update Vercel Environment Variable

```bash
# Copy your Cloud Run URL
# Example: https://kos-backend-abc123-uc.a.run.app

# Go to Vercel Dashboard:
# 1. Open https://vercel.com/dashboard
# 2. Select your project
# 3. Settings → Environment Variables
# 4. Edit VITE_API_URL
# 5. Set to: https://YOUR_BACKEND_URL.run.app/api
# 6. Click Save
# 7. Go to Deployments → Redeploy
```

**Important**: Add `/api` at the end!

---

## Step 11: Update CORS in Backend

```bash
# Redeploy backend with correct CORS
gcloud run deploy kos-backend \
  --platform managed \
  --region asia-southeast1 \
  --update-env-vars CORS_ORIGINS=https://your-actual-vercel-url.vercel.app
```

---

## Verify Everything Works

1. **Test Health**: `curl https://YOUR_BACKEND_URL.run.app/health`
2. **Visit Frontend**: Open your Vercel URL
3. **Login**: Use `admin` / `password`
4. **Test Features**:
   - Dashboard loads with metrics
   - Rooms page shows rooms
   - Language switching works (EN/ID)
   - Create/edit/delete operations work

---

## Monitoring & Logs

### View Logs:
```bash
# Real-time logs
gcloud run services logs tail kos-backend \
  --platform managed \
  --region asia-southeast1

# Recent logs
gcloud run services logs read kos-backend \
  --platform managed \
  --region asia-southeast1 \
  --limit 50
```

### View Metrics:
```bash
# Open Cloud Console
open https://console.cloud.google.com/run/detail/asia-southeast1/kos-backend/metrics
```

---

## Cost Breakdown

### Monthly Estimate (Low Traffic):

| Service | Configuration | Cost |
|---------|--------------|------|
| Cloud Run | 512MB RAM, minimal traffic | $3-5 |
| Cloud SQL (db-f1-micro) | 10GB HDD storage | $10-12 |
| Networking | Egress (minimal) | $1-2 |
| **Total** | | **$14-19/month** |

### Free Tier Includes:
- Cloud Run: 2M requests/month
- Cloud SQL: First 10GB storage included
- Networking: 1GB egress/month

---

## Scaling Configuration

### For Higher Traffic:

```bash
# Increase resources
gcloud run deploy kos-backend \
  --platform managed \
  --region asia-southeast1 \
  --memory 1Gi \
  --cpu 2 \
  --max-instances 100 \
  --min-instances 1 \
  --concurrency 80
```

### For Production Database:

```bash
# Upgrade to larger instance
gcloud sql instances patch kos-db \
  --tier=db-n1-standard-1 \
  --storage-size=20GB \
  --storage-type=SSD \
  --backup-start-time=02:00
```

---

## Troubleshooting

### Build Fails:
```bash
# Check build logs
gcloud builds list --limit 5

# View specific build
gcloud builds log BUILD_ID
```

### Container Won't Start:
```bash
# Check logs
gcloud run services logs read kos-backend --limit 100

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Port binding (should use PORT env var)
```

### Database Connection Fails:
```bash
# Verify Cloud SQL instance is running
gcloud sql instances describe kos-db

# Test connection
gcloud sql connect kos-db --user=kos_user

# Check secrets
gcloud secrets versions access latest --secret=DATABASE_URL
```

### CORS Errors:
```bash
# Update CORS_ORIGINS
gcloud run services update kos-backend \
  --update-env-vars CORS_ORIGINS=https://your-correct-url.vercel.app
```

---

## Cleanup (If Needed)

```bash
# Delete Cloud Run service
gcloud run services delete kos-backend --region asia-southeast1

# Delete Cloud SQL instance
gcloud sql instances delete kos-db

# Delete secrets
gcloud secrets delete DATABASE_URL
gcloud secrets delete JWT_SECRET_KEY

# Delete project (removes everything)
gcloud projects delete kos-management-prod
```

---

## Next Steps After Deployment

1. ✅ Change default admin password
2. ✅ Set up Cloud SQL automated backups
3. ✅ Configure custom domain (optional)
4. ✅ Set up monitoring alerts
5. ✅ Enable Cloud SQL SSL connections
6. ✅ Review security settings

---

## Quick Commands Reference

```bash
# Redeploy after code changes
cd backend
gcloud run deploy kos-backend --source .

# View logs
gcloud run services logs tail kos-backend

# Update environment variables
gcloud run services update kos-backend \
  --update-env-vars KEY=VALUE

# Scale up/down
gcloud run services update kos-backend \
  --max-instances 50 \
  --min-instances 1

# Get service URL
gcloud run services describe kos-backend \
  --format 'value(status.url)'
```

---

## Support & Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Pricing Calculator](https://cloud.google.com/products/calculator)

**Ready to deploy!** 🚀
