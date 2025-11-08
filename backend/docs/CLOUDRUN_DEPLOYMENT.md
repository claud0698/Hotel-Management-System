# Google Cloud Run Deployment Guide - Phase 9

**Purpose**: Complete guide for deploying Hotel Management System to Google Cloud Run

**Last Updated**: November 8, 2025

**Status**: Phase 9 - Ready for Review

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Deployment Steps](#deployment-steps)
4. [Configuration](#configuration)
5. [Database Setup](#database-setup)
6. [Environment Variables](#environment-variables)
7. [Monitoring & Logging](#monitoring--logging)
8. [Scaling & Performance](#scaling--performance)
9. [Cost Optimization](#cost-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

Deploy in 5 minutes:

```bash
# 1. Authenticate with GCP
gcloud auth login
gcloud config set project my-project-id

# 2. Build and push to Container Registry
gcloud builds submit --tag gcr.io/my-project-id/hotel-api:latest

# 3. Deploy to Cloud Run
gcloud run deploy hotel-api \
  --image gcr.io/my-project-id/hotel-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://... \
  --set-env-vars SECRET_KEY=...

# 4. Access your API
curl https://hotel-api-xxxxx.run.app/health
```

---

## Prerequisites

### GCP Account & Project

```bash
# Create GCP account at https://console.cloud.google.com
# Create new project

# Set default project
gcloud config set project my-project-id

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com
```

### Install Google Cloud SDK

```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verify installation
gcloud --version
```

### Authenticate

```bash
# Login to your Google account
gcloud auth login

# Set default project
gcloud config set project my-project-id

# Verify
gcloud config list
```

---

## Deployment Steps

### Step 1: Build Docker Image

```bash
cd backend

# Build locally (optional)
docker build -t hotel-api:latest .

# Build on Google Cloud Build (preferred)
gcloud builds submit \
  --tag gcr.io/my-project-id/hotel-api:latest \
  --source . \
  --config cloudbuild.yaml

# View build progress
gcloud builds log <BUILD_ID> --stream
```

### Step 2: Create Cloud SQL Instance (PostgreSQL)

```bash
# Create Cloud SQL instance
gcloud sql instances create hotel-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --backup

# Create database
gcloud sql databases create hotel_prod \
  --instance=hotel-db

# Create database user
gcloud sql users create dbuser \
  --instance=hotel-db \
  --password

# Get connection name
gcloud sql instances describe hotel-db \
  --format='value(connectionName)'
# Output: my-project:us-central1:hotel-db
```

### Step 3: Set up Secret Manager

```bash
# Create secrets for sensitive data
echo -n "postgresql://dbuser:PASSWORD@/hotel_prod?unix_socket_dir=/cloudsql/my-project:us-central1:hotel-db" \
  | gcloud secrets create database-url --data-file=-

echo -n "$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" \
  | gcloud secrets create secret-key --data-file=-

# Grant Cloud Run service account access to secrets
gcloud secrets add-iam-policy-binding database-url \
  --member=serviceAccount:my-project@appspot.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding secret-key \
  --member=serviceAccount:my-project@appspot.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### Step 4: Deploy to Cloud Run

```bash
# Deploy with all configuration
gcloud run deploy hotel-api \
  --image gcr.io/my-project-id/hotel-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 100 \
  --set-env-vars \
    ENVIRONMENT=production,\
    LOG_LEVEL=INFO,\
    CORS_ORIGINS=https://yourdomain.com \
  --set-secrets \
    DATABASE_URL=database-url:latest,\
    SECRET_KEY=secret-key:latest \
  --add-cloudsql-instances my-project:us-central1:hotel-db

# Get service URL
gcloud run services describe hotel-api --region us-central1 --format='value(status.url)'
```

### Step 5: Configure Custom Domain

```bash
# Map custom domain to Cloud Run
gcloud run domain-mappings create \
  --service=hotel-api \
  --domain=api.yourdomain.com \
  --region=us-central1

# Add DNS records to your domain registrar
# TYPE: A
# NAME: api
# VALUE: (from gcloud output)

# Verify domain mapping
gcloud run domain-mappings describe api.yourdomain.com
```

---

## Configuration

### CloudBuild Configuration (cloudbuild.yaml)

```yaml
# cloudbuild.yaml in backend directory
steps:
  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/hotel-api:$SHORT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/hotel-api:latest'
      - '.'
    dir: 'backend'

  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/hotel-api:$SHORT_SHA'
    dir: 'backend'

  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gke-deploy'
    args:
      - 'run'
      - '--filename=.'
      - '--image=gcr.io/$PROJECT_ID/hotel-api:$SHORT_SHA'
      - '--location=us-central1'
      - '--namespace=default'

# Store images in Container Registry
images:
  - 'gcr.io/$PROJECT_ID/hotel-api:$SHORT_SHA'
  - 'gcr.io/$PROJECT_ID/hotel-api:latest'

# Build timeout
timeout: '1800s'

options:
  machineType: 'N1_HIGHCPU_8'
```

### App Configuration (app.yaml)

```yaml
# Alternative: Using app.yaml for deployment
runtime: python
env: flex
entrypoint: gunicorn -w 4 -b :$PORT app:app

env_variables:
  ENVIRONMENT: production
  LOG_LEVEL: INFO

handlers:
  - url: /.*
    script: auto
    secure: always
    redirect_http_response_code: 301

automatic_scaling:
  min_instances: 1
  max_instances: 100
```

---

## Database Setup

### Cloud SQL Connection

**Option 1: Cloud SQL Auth Proxy (Recommended)**

```bash
# Create service account
gcloud iam service-accounts create hotel-api-sa

# Grant roles
gcloud projects add-iam-policy-binding my-project-id \
  --member=serviceAccount:hotel-api-sa@my-project-id.iam.gserviceaccount.com \
  --role=roles/cloudsql.client

# In Cloud Run deployment
gcloud run deploy hotel-api \
  --add-cloudsql-instances my-project:us-central1:hotel-db \
  --service-account=hotel-api-sa@my-project-id.iam.gserviceaccount.com
```

**Option 2: Direct Connection (Less Secure)**

```bash
# Authorize Cloud Run IP
gcloud sql instances patch hotel-db \
  --allowed-networks=0.0.0.0/0  # Not recommended in production

# Use direct connection string
DATABASE_URL=postgresql://dbuser:PASSWORD@cloudsqlproxy:5432/hotel_prod
```

### Database Initialization

```bash
# Connect to database
gcloud sql connect hotel-db --user=postgres

# Or using psql
psql "postgresql://dbuser:PASSWORD@cloudsqlproxy:5432/hotel_prod"

# Run migrations on first deployment
gcloud run deploy hotel-api \
  --image gcr.io/my-project-id/hotel-api:latest \
  --update-env-vars RUN_MIGRATIONS=true

# In your app.py or startup script
if os.getenv('RUN_MIGRATIONS') == 'true':
    import subprocess
    subprocess.run(['alembic', 'upgrade', 'head'])
```

---

## Environment Variables

### Cloud Run Environment Configuration

```bash
# Set as environment variables (non-secret)
gcloud run deploy hotel-api \
  --set-env-vars \
    ENVIRONMENT=production,\
    LOG_LEVEL=INFO,\
    API_VERSION=1.0.0,\
    CORS_ORIGINS=https://yourdomain.com,\
    MAX_REQUEST_SIZE=10485760

# Update environment variables
gcloud run services update hotel-api \
  --set-env-vars LOG_LEVEL=DEBUG \
  --region us-central1

# View environment variables
gcloud run services describe hotel-api \
  --region us-central1 \
  --format='value(spec.template.spec.containers[0].env)'
```

### Secret Manager for Sensitive Data

```bash
# Store secrets
echo -n "postgresql://..." | gcloud secrets create database-url --data-file=-
echo -n "your-secret-key-32-chars" | gcloud secrets create secret-key --data-file=-

# Reference in deployment
gcloud run deploy hotel-api \
  --set-secrets \
    DATABASE_URL=database-url:latest,\
    SECRET_KEY=secret-key:latest

# Update secret
echo -n "new-value" | gcloud secrets versions add database-url --data-file=-
```

### .env.cloudrun Example

```env
# Non-secret environment variables
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
LOG_FORMAT=json
API_PREFIX=/api
API_VERSION=1.0.0

# CORS configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Monitoring
ENABLE_METRICS=true
SENTRY_ENVIRONMENT=production

# Secrets (stored separately)
# DATABASE_URL=<from Secret Manager>
# SECRET_KEY=<from Secret Manager>
```

---

## Monitoring & Logging

### Cloud Logging

```bash
# View logs for your service
gcloud logging read "resource.service.name=hotel-api" \
  --limit 50 \
  --format json

# Stream logs in real-time
gcloud logging read "resource.service.name=hotel-api" \
  --stream

# Filter by severity
gcloud logging read "resource.service.name=hotel-api AND severity>=ERROR" \
  --limit 50

# Access in Cloud Console
# https://console.cloud.google.com/logs/query
```

### Cloud Monitoring

```bash
# Create uptime check
gcloud monitoring uptime-checks create \
  --display-name="Hotel API Health" \
  --resource-type=uptime-url \
  --monitored-resource=https://hotel-api-xxxxx.run.app/health

# View metrics
gcloud monitoring metrics-descriptors list

# Create alert policy (via console)
# https://console.cloud.google.com/monitoring/alertpolicies
```

### Application Insights Setup

```python
# In app.py
from google.cloud import logging as cloud_logging

logging_client = cloud_logging.Client()
logging_client.setup_logging()

import logging
logger = logging.getLogger()
logger.info("Application started")
```

---

## Scaling & Performance

### Autoscaling Configuration

```bash
# Configure autoscaling
gcloud run deploy hotel-api \
  --min-instances 1 \
  --max-instances 100 \
  --memory 1Gi \
  --cpu 1

# Adjust after deployment
gcloud run services update hotel-api \
  --max-instances 50 \
  --region us-central1
```

### Memory and CPU

```bash
# Cloud Run memory/CPU options
# Memory: 128Mi to 8Gi
# CPU: 1 (default), 2, or 4

# Deploy with 2 CPU and 2GB memory
gcloud run deploy hotel-api \
  --memory 2Gi \
  --cpu 2
```

### Load Testing

```bash
# Use Cloud Load Testing
gcloud compute load-testing run \
  --rps 100 \
  --duration 60 \
  https://hotel-api-xxxxx.run.app/health

# Or use Apache Bench
ab -n 1000 -c 100 https://hotel-api-xxxxx.run.app/health

# Or use Locust (from PERFORMANCE_OPTIMIZATION.md)
locust -f locustfile.py -u 100 -r 10 -t 5m
```

---

## Cost Optimization

### Reduce Costs

```bash
# 1. Use Cloud Run's pay-per-use model
# - Billed only when processing requests
# - Free tier: 2M requests/month

# 2. Reduce min instances
gcloud run deploy hotel-api --min-instances 0

# 3. Reduce memory if possible
gcloud run deploy hotel-api --memory 512Mi

# 4. Use Cloud SQL Proxy with shared instances
# Better than dedicated instances for small apps

# 5. Monitor costs
# https://console.cloud.google.com/billing
```

### Cost Estimation

```bash
# Example monthly costs (rough estimate)
# Cloud Run: 1M requests @ $0.40/million = $0.40
# Cloud SQL: db-f1-micro @ $9.23/month = $9.23
# Storage: 10GB @ $0.02/GB = $0.20
# Total: ~$10/month

# Calculate with Google Cloud Pricing Calculator
# https://cloud.google.com/products/calculator
```

---

## Troubleshooting

### Issue: "Deployment failed"

```bash
# Check deployment logs
gcloud run deploy hotel-api \
  --image gcr.io/my-project-id/hotel-api:latest \
  --verbosity=debug

# Check Cloud Build logs
gcloud builds log <BUILD_ID>

# Check service account permissions
gcloud projects get-iam-policy my-project-id
```

### Issue: "Container fails to start"

```bash
# Check container logs
gcloud run services describe hotel-api \
  --region us-central1 \
  --format='value(status.conditions[*].message)'

# View detailed logs
gcloud logging read "resource.service.name=hotel-api" \
  --limit 50 \
  --format json
```

### Issue: "Database connection refused"

```bash
# Check Cloud SQL instance is running
gcloud sql instances list

# Check Cloud SQL Auth Proxy
gcloud sql connect hotel-db --user=postgres

# Verify connection string
gcloud run services describe hotel-api \
  --region us-central1 \
  --format='value(spec.template.spec.containers[0].env[])'
```

### Issue: "Timeouts on startup"

```bash
# Increase startup timeout
gcloud run deploy hotel-api \
  --timeout 3600 \
  --startup-probe-failure-threshold 3

# Or initialize database before deployment
# Run migrations in separate job, then deploy service
```

### Issue: "Out of memory"

```bash
# Check current memory usage
gcloud monitoring time-series list \
  --filter='resource.type=cloud_run_revision'

# Increase memory
gcloud run deploy hotel-api --memory 2Gi

# Optimize code for memory usage
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests pass locally
- [ ] Docker image builds successfully
- [ ] Environment variables configured
- [ ] Cloud SQL instance created
- [ ] Database user created
- [ ] Secrets stored in Secret Manager
- [ ] Custom domain configured (optional)
- [ ] SSL certificate configured (HTTPS)

### Deployment

- [ ] Cloud Build successful
- [ ] Cloud Run service deployed
- [ ] Health check passes
- [ ] Database migrations ran
- [ ] Admin user created
- [ ] Monitoring alerts configured
- [ ] Logging enabled

### Post-Deployment

- [ ] API responds to requests
- [ ] Database queries work
- [ ] Authentication works
- [ ] Logs are being collected
- [ ] Monitoring dashboards set up
- [ ] Backup strategy configured
- [ ] Runbook documented

---

## Quick Commands Reference

```bash
# Deploy service
gcloud run deploy hotel-api --image gcr.io/my-project-id/hotel-api:latest

# View service details
gcloud run services describe hotel-api

# View logs
gcloud logging read "resource.service.name=hotel-api"

# Update service
gcloud run services update hotel-api --set-env-vars KEY=value

# Delete service
gcloud run services delete hotel-api

# List all services
gcloud run services list
```

---

**Last Updated**: November 8, 2025
**Status**: Phase 9 - Ready for Review
**Next**: Production Checklist & Security Hardening
