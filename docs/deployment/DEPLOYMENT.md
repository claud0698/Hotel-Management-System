# Deployment Guide

This guide explains how to deploy the Kos Management System to production.

## Architecture

- **Frontend**: React + TypeScript + Vite → Vercel
- **Backend**: FastAPI + Python → Google Cloud Platform (Cloud Run)
- **Database**: SQLite (development) → PostgreSQL on GCP (production)

---

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account (free tier works)
- GitHub repository with this code

### Step-by-Step Deployment

#### 1. Install Vercel CLI (optional, for local testing)
```bash
npm install -g vercel
```

#### 2. Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

#### 3. Environment Variables

Add these environment variables in Vercel Dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `https://your-backend-url.run.app/api` | GCP Backend URL |

**Important**: Update `VITE_API_URL` after deploying the backend!

#### 4. Deploy

- Click **"Deploy"**
- Vercel will build and deploy automatically
- You'll get a URL like: `https://your-project.vercel.app`

#### 5. Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

### Local Testing with Production Build

```bash
cd frontend
npm run build
npm run preview
```

---

## Backend Deployment (Google Cloud Platform)

### Prerequisites
- GCP account with billing enabled
- `gcloud` CLI installed
- Docker installed (for Cloud Run)

### Step-by-Step Deployment

#### 1. Install Google Cloud SDK

**macOS:**
```bash
brew install --cask google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

#### 2. Initialize GCP

```bash
# Login
gcloud auth login

# Create a new project (or use existing)
gcloud projects create kos-management --name="Kos Management"

# Set project
gcloud config set project kos-management

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

#### 3. Create PostgreSQL Database

```bash
# Create Cloud SQL instance
gcloud sql instances create kos-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-southeast1 \
  --root-password=YOUR_SECURE_PASSWORD

# Create database
gcloud sql databases create kos_production --instance=kos-db

# Create user
gcloud sql users create kos_user \
  --instance=kos-db \
  --password=YOUR_USER_PASSWORD
```

#### 4. Store Secrets in Secret Manager

```bash
# Database URL
echo -n "postgresql://kos_user:YOUR_USER_PASSWORD@/kos_production?host=/cloudsql/PROJECT_ID:REGION:kos-db" | \
  gcloud secrets create DATABASE_URL --data-file=-

# JWT Secret
echo -n "$(openssl rand -base64 32)" | \
  gcloud secrets create JWT_SECRET_KEY --data-file=-
```

#### 5. Create Dockerfile (backend)

The backend directory already includes a Dockerfile. If not, create:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations and start app
CMD python -m alembic upgrade head && \
    python -m uvicorn app:app --host 0.0.0.0 --port $PORT
```

#### 6. Deploy to Cloud Run

```bash
cd backend

# Build and deploy
gcloud run deploy kos-backend \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --add-cloudsql-instances PROJECT_ID:REGION:kos-db \
  --set-secrets DATABASE_URL=DATABASE_URL:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest \
  --set-env-vars CORS_ORIGINS=https://your-frontend.vercel.app
```

#### 7. Get Backend URL

```bash
gcloud run services describe kos-backend \
  --platform managed \
  --region asia-southeast1 \
  --format 'value(status.url)'
```

Copy this URL and update the `VITE_API_URL` in Vercel!

---

## Post-Deployment

### 1. Update Frontend Environment Variable

1. Go to Vercel Dashboard
2. Project Settings → Environment Variables
3. Update `VITE_API_URL` with your GCP backend URL
4. Redeploy frontend

### 2. Run Database Migrations

```bash
# Connect to Cloud SQL
gcloud sql connect kos-db --user=kos_user

# In the backend, run migrations
python -m alembic upgrade head

# Seed initial data (optional)
python seed_july_2025.py
```

### 3. Test the Deployment

1. Visit your Vercel frontend URL
2. Try logging in (default: admin/password)
3. Test all features: rooms, tenants, payments, expenses
4. Switch languages (EN/ID) to verify i18n works

### 4. Monitor and Debug

**Vercel Logs:**
- Dashboard → Deployments → Click deployment → View logs

**GCP Cloud Run Logs:**
```bash
gcloud run services logs read kos-backend \
  --platform managed \
  --region asia-southeast1
```

---

## Environment Variables Reference

### Frontend (Vercel)

| Variable | Example | Required |
|----------|---------|----------|
| `VITE_API_URL` | `https://kos-backend-xyz.run.app/api` | Yes |

### Backend (GCP Cloud Run)

| Variable | Example | Required |
|----------|---------|----------|
| `DATABASE_URL` | `postgresql://user:pass@host/db` | Yes |
| `JWT_SECRET_KEY` | `your-secret-key` | Yes |
| `CORS_ORIGINS` | `https://your-app.vercel.app` | Yes |
| `PORT` | `8080` (auto-set by Cloud Run) | No |

---

## Troubleshooting

### Frontend Issues

**Build fails:**
- Check Node version (should be 18+)
- Clear cache: `rm -rf node_modules package-lock.json && npm install`

**API calls fail:**
- Verify `VITE_API_URL` is set correctly
- Check CORS settings on backend
- Check browser console for errors

### Backend Issues

**Database connection fails:**
- Verify Cloud SQL instance is running
- Check database credentials in Secret Manager
- Verify Cloud SQL instance connection string

**CORS errors:**
- Update `CORS_ORIGINS` environment variable
- Include your Vercel domain (e.g., `https://your-app.vercel.app`)

**Cloud Run deploy fails:**
- Check Cloud Run quota limits
- Verify billing is enabled
- Check service account permissions

---

## Security Checklist

- [ ] Change default admin password
- [ ] Use strong JWT secret (32+ characters)
- [ ] Enable HTTPS (automatic on Vercel & Cloud Run)
- [ ] Restrict CORS to your domain only
- [ ] Use Secret Manager for sensitive data
- [ ] Enable Cloud SQL SSL connections
- [ ] Set up Cloud SQL backups
- [ ] Configure Vercel password protection (optional)
- [ ] Set up monitoring and alerts

---

## Cost Estimation

### Vercel (Frontend)
- **Free Tier**: Unlimited personal projects
- **Pro**: $20/month (if needed)

### GCP (Backend + Database)
- **Cloud Run**: ~$5-10/month (free tier: 2M requests/month)
- **Cloud SQL (db-f1-micro)**: ~$10-15/month
- **Total**: ~$15-25/month for small-scale usage

### Free Tier Limits
- Vercel: Unlimited deployments
- GCP Cloud Run: 2M requests/month
- GCP Cloud SQL: 10GB storage included

---

## Backup and Maintenance

### Database Backups

```bash
# Manual backup
gcloud sql backups create --instance=kos-db

# List backups
gcloud sql backups list --instance=kos-db

# Restore backup
gcloud sql backups restore BACKUP_ID --backup-instance=kos-db --backup-instance=kos-db
```

### Update Deployment

**Frontend (Vercel):**
- Push to GitHub → Auto-deploys

**Backend (Cloud Run):**
```bash
cd backend
gcloud run deploy kos-backend --source .
```

---

## Support

For issues or questions:
- Check logs in Vercel Dashboard or GCP Console
- Review this deployment guide
- Check the main README.md for application documentation
