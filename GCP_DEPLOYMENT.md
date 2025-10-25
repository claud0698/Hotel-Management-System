# GCP Deployment Guide - Kos Management Dashboard

This guide covers deploying your FastAPI backend to Google Cloud Platform using the **cheapest** options.

## 📊 Cost Comparison

| Service | Monthly Cost | Best For |
|---------|--------------|----------|
| **Cloud Run** (Recommended) | **$0-5** | Low to medium traffic, scales to zero |
| App Engine Standard | $25-50 | Simple deployment, always-on |
| Compute Engine (f1-micro) | $25+ | Full control, always-on |
| Cloud SQL (db-f1-micro) | $7-10 | Production database |
| SQLite on Cloud Storage | ~$0.02 | Development/testing only |

## 🎯 Recommended: Cloud Run + Cloud SQL

**Total estimated cost: $7-15/month** (or FREE with external DB)

---

## Option 1: Cloud Run (CHEAPEST - Recommended)

### Why Cloud Run?
- ✅ Pay only when handling requests
- ✅ Scales to zero (no idle costs)
- ✅ FREE tier: 2M requests/month
- ✅ Perfect for small to medium apps
- ✅ Your app will likely stay 100% FREE

### Prerequisites

1. **Install Google Cloud SDK**
   ```bash
   # macOS
   brew install google-cloud-sdk

   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Set up GCP Project**
   ```bash
   # Login to GCP
   gcloud auth login

   # Create new project (or use existing)
   gcloud projects create kos-dashboard-prod --name="Kos Dashboard"

   # Set project
   gcloud config set project kos-dashboard-prod

   # Enable required APIs
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable sqladmin.googleapis.com
   ```

### Step 1: Set Up Database

#### Option A: Cloud SQL PostgreSQL (Recommended for Production)

```bash
# Create Cloud SQL instance (db-f1-micro = cheapest)
gcloud sql instances create kos-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-southeast2 \
  --storage-size=10GB \
  --storage-type=HDD \
  --storage-auto-increase \
  --backup-start-time=03:00

# Set root password
gcloud sql users set-password postgres \
  --instance=kos-db \
  --password=YOUR_SECURE_PASSWORD

# Create database
gcloud sql databases create kos_db --instance=kos-db

# Create app user
gcloud sql users create kos_user \
  --instance=kos-db \
  --password=YOUR_APP_PASSWORD

# Get connection name (you'll need this)
gcloud sql instances describe kos-db --format='value(connectionName)'
# Output: PROJECT_ID:REGION:INSTANCE_NAME
```

**Cost: ~$7-10/month**

#### Option B: Free External Database (FREE)

Use one of these free PostgreSQL services:
- **Supabase**: 500MB free, excellent for small apps
- **Neon**: 3GB free, serverless PostgreSQL
- **PlanetScale**: 5GB free (MySQL)

Sign up and get connection string, then skip Cloud SQL setup.

### Step 2: Deploy to Cloud Run

```bash
# Navigate to backend directory
cd backend

# Build and deploy (Cloud Run will build from Dockerfile)
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

# The command will:
# 1. Build container image using your Dockerfile
# 2. Push to Google Container Registry
# 3. Deploy to Cloud Run
# 4. Give you a URL like: https://kos-api-xxx-uc.a.run.app
```

### Step 3: Configure Environment Variables

```bash
# For Cloud SQL
gcloud run services update kos-api \
  --region=asia-southeast2 \
  --set-env-vars="FLASK_ENV=production,DEBUG=False" \
  --set-env-vars="DATABASE_URL=postgresql+psycopg2://kos_user:YOUR_APP_PASSWORD@/kos_db?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME" \
  --add-cloudsql-instances=PROJECT_ID:REGION:INSTANCE_NAME

# For external database (Supabase, Neon, etc.)
gcloud run services update kos-api \
  --region=asia-southeast2 \
  --set-env-vars="FLASK_ENV=production,DEBUG=False" \
  --set-env-vars="DATABASE_URL=postgresql+psycopg2://username:password@host:5432/database"

# Set CORS origins (your frontend URL)
gcloud run services update kos-api \
  --region=asia-southeast2 \
  --set-env-vars="CORS_ORIGINS=https://your-frontend.vercel.app"
```

### Step 4: Set Up Secrets (Recommended)

```bash
# Enable Secret Manager
gcloud services enable secretmanager.googleapis.com

# Create secret for DATABASE_URL
echo -n "postgresql+psycopg2://user:pass@host/db" | \
  gcloud secrets create database-url --data-file=-

# Create secret for JWT key
python3 -c "import secrets; print(secrets.token_urlsafe(32))" | \
  gcloud secrets create jwt-secret-key --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding database-url \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding jwt-secret-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update Cloud Run to use secrets
gcloud run services update kos-api \
  --region=asia-southeast2 \
  --update-secrets=DATABASE_URL=database-url:latest,JWT_SECRET_KEY=jwt-secret-key:latest
```

### Step 5: Test Deployment

```bash
# Get your Cloud Run URL
gcloud run services describe kos-api \
  --region=asia-southeast2 \
  --format='value(status.url)'

# Test health endpoint
curl https://kos-api-xxx-uc.a.run.app/health

# Test API root
curl https://kos-api-xxx-uc.a.run.app/api
```

### Step 6: Initialize Database

```bash
# Connect to Cloud SQL and create admin user
gcloud sql connect kos-db --user=postgres

# Or use Cloud Run job to seed database
# Create seed_job.yaml and deploy
```

---

## Option 2: App Engine (Simpler but More Expensive)

**Cost: ~$25-50/month** (always-on instance)

### Deploy to App Engine

```bash
# Navigate to backend
cd backend

# Enable App Engine
gcloud app create --region=asia-southeast2

# Deploy using app.yaml
gcloud app deploy app.yaml

# View your app
gcloud app browse
```

### Set Environment Variables

```bash
# Edit app.yaml to add env_variables
# Or use Cloud Console: App Engine > Settings > Environment Variables
```

---

## 🔒 Security Best Practices

1. **Use Secret Manager** for sensitive data (DATABASE_URL, JWT keys)
2. **Restrict CORS** to your frontend domain only
3. **Enable Cloud Armor** for DDoS protection (if needed)
4. **Set up Cloud SQL backups**:
   ```bash
   gcloud sql instances patch kos-db \
     --backup-start-time=03:00 \
     --enable-bin-log
   ```
5. **Use IAM roles** instead of root credentials
6. **Enable Cloud SQL SSL**:
   ```bash
   gcloud sql ssl-certs create client-cert client-key.pem \
     --instance=kos-db
   ```

---

## 📊 Monitoring & Logs

```bash
# View Cloud Run logs
gcloud run services logs read kos-api \
  --region=asia-southeast2 \
  --limit=50

# View Cloud SQL logs
gcloud sql operations list --instance=kos-db

# Set up monitoring alerts in Cloud Console
# Navigate to: Monitoring > Alerting > Create Policy
```

---

## 💰 Cost Optimization Tips

1. **Use Cloud Run with min-instances=0** to scale to zero
2. **Choose asia-southeast2 (Jakarta)** for Indonesia users - lowest latency
3. **Use db-f1-micro** for Cloud SQL (cheapest tier)
4. **Use HDD instead of SSD** for storage (3x cheaper)
5. **Enable storage auto-increase** to avoid over-provisioning
6. **Set up budget alerts**:
   ```bash
   # In Cloud Console: Billing > Budgets & Alerts
   # Set alert at $10, $20, $30
   ```
7. **Use external free database** (Supabase/Neon) during development

---

## 🚀 CI/CD with GitHub Actions (Optional)

Create `.github/workflows/deploy-gcp.yml`:

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
```

---

## 🔧 Troubleshooting

### Cloud Run Issues

```bash
# Check service status
gcloud run services describe kos-api --region=asia-southeast2

# View logs
gcloud run services logs read kos-api --region=asia-southeast2 --limit=100

# Check container build
gcloud builds list --limit=5
```

### Cloud SQL Connection Issues

```bash
# Test connection from Cloud Shell
gcloud sql connect kos-db --user=kos_user

# Check if Cloud SQL API is enabled
gcloud services list --enabled | grep sql

# Verify connection name
gcloud sql instances describe kos-db --format='value(connectionName)'
```

### Port Issues

Cloud Run expects port **8080**. Your Dockerfile already uses `${PORT:-8080}`.

---

## 📚 Useful Commands

```bash
# Get Cloud Run URL
gcloud run services list

# Update Cloud Run configuration
gcloud run services update kos-api --region=asia-southeast2 --memory=1Gi

# Delete Cloud Run service
gcloud run services delete kos-api --region=asia-southeast2

# Stop Cloud SQL (save costs during development)
gcloud sql instances patch kos-db --activation-policy=NEVER

# Start Cloud SQL
gcloud sql instances patch kos-db --activation-policy=ALWAYS

# View billing
gcloud billing accounts list
gcloud billing projects describe PROJECT_ID
```

---

## 🎯 Recommended Setup for Production

**For maximum savings:**
- **Cloud Run** (FREE tier - 2M requests/month)
- **External DB** (Supabase/Neon FREE tier)
- **Total Cost: $0/month** for small apps

**For better performance:**
- **Cloud Run** (FREE tier)
- **Cloud SQL db-f1-micro** ($7-10/month)
- **Total Cost: $7-10/month**

---

## Next Steps

1. ✅ Deploy backend to Cloud Run
2. ✅ Set up database (Cloud SQL or external)
3. ✅ Configure environment variables
4. ✅ Update frontend to use Cloud Run URL
5. ✅ Test all API endpoints
6. ✅ Set up monitoring and alerts
7. ✅ Configure custom domain (optional)

---

## Custom Domain Setup (Optional)

```bash
# Map custom domain to Cloud Run
gcloud run domain-mappings create \
  --service=kos-api \
  --domain=api.yourdomain.com \
  --region=asia-southeast2

# Follow DNS setup instructions provided
```

---

## Support

- GCP Documentation: https://cloud.google.com/run/docs
- Cloud SQL Docs: https://cloud.google.com/sql/docs
- Pricing Calculator: https://cloud.google.com/products/calculator

**Estimated Total Cost: $0-15/month** 🎉
