# GCP Cloud Run Deployment Guide - Step by Step

**Status**: Complete step-by-step instructions for manual deployment
**Target**: GCP Cloud Run (Serverless)
**Architecture**: amd64 (x86-64) - compatible with Cloud Run

---

## Prerequisites

Before starting, ensure you have:
- ✅ GCP Account with billing enabled
- ✅ Docker installed locally
- ✅ `gcloud` CLI installed
- ✅ `docker` CLI configured
- ✅ GCP Project created

### Install GCP CLI (if not already installed)

```bash
# Download and install gcloud CLI
# Visit: https://cloud.google.com/sdk/docs/install

# After installation, verify:
gcloud --version
gcloud auth login
```

---

## Step 1: Set Up GCP Project

### 1.1 Set your GCP Project ID
```bash
# List your projects
gcloud projects list

# Set your project (replace PROJECT_ID with your actual project ID)
gcloud config set project PROJECT_ID

# Verify
gcloud config get-value project
```

### 1.2 Enable Required APIs
```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com
```

### 1.3 Set Default Region
```bash
# Set region to Asia Southeast 1 (Singapore)
gcloud config set run/region asia-southeast1

# Or set it per command (see Step 3)
```

---

## Step 2: Create Artifact Registry Repository

### 2.1 Create a Docker repository in Artifact Registry
```bash
# Create repository in Asia Southeast 1 (Singapore)
gcloud artifacts repositories create kos-backend \
  --repository-format=docker \
  --location=asia-southeast1 \
  --description="Kos Management System Backend"

# Verify creation
gcloud artifacts repositories list
```

### 2.2 Configure Docker Authentication
```bash
# Configure Docker to authenticate with Artifact Registry
gcloud auth configure-docker asia-southeast1-docker.pkg.dev

# Verify (should show login success)
# You should see: Login Succeeded
```

---

## Step 3: Build Docker Image Locally

### 3.1 Navigate to Backend Directory
```bash
# Change to backend directory
cd /Users/claudio/Documents/Personal/kos-database/backend
```

### 3.2 Build Image for amd64 (Important for Cloud Run)
```bash
# Build with amd64 architecture specified
docker buildx build \
  --platform linux/amd64 \
  -t kos-backend:latest \
  -t kos-backend:1.0.0 \
  --load \
  .

# Or if buildx not available, try:
docker build -t kos-backend:latest .

# Verify image was created
docker images | grep kos-backend
```

**Expected Output:**
```
REPOSITORY      TAG       IMAGE ID       CREATED        SIZE
kos-backend     latest    abc123def456   X minutes ago   XXX MB
kos-backend     1.0.0     abc123def456   X minutes ago   XXX MB
```

### 3.3 Test Image Locally (Optional but Recommended)
```bash
# Run the image locally to verify it works
docker run -p 8080:8080 \
  -e DATABASE_URL="your_postgres_url" \
  kos-backend:latest

# In another terminal, test the health endpoint:
curl http://localhost:8080/health

# Press Ctrl+C to stop the container
```

---

## Step 4: Tag Image for Artifact Registry

### 4.1 Tag the image with your Artifact Registry path
```bash
# Set variables
PROJECT_ID=$(gcloud config get-value project)
REGION=asia-southeast1
REPOSITORY=kos-backend
IMAGE_NAME=kos-backend
TAG=1.0.0

# Tag the image
docker tag kos-backend:latest \
  ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${TAG}

docker tag kos-backend:latest \
  ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest

# Verify tags
docker images | grep pkg.dev
```

**Expected Output:**
```
asia-southeast1-docker.pkg.dev/your-project/kos-backend/kos-backend   1.0.0     abc123def456
asia-southeast1-docker.pkg.dev/your-project/kos-backend/kos-backend   latest    abc123def456
```

---

## Step 5: Push Image to Artifact Registry

### 5.1 Push the images
```bash
# Push both tags
docker push \
  asia-southeast1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${TAG}

docker push \
  asia-southeast1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest

# This may take a few minutes...
```

**Expected Output:**
```
The push refers to repository [asia-southeast1-docker.pkg.dev/...]
... pushing layers...
1.0.0: digest: sha256:abc123... size: 12345
latest: digest: sha256:abc123... size: 12345
```

### 5.2 Verify Push
```bash
# List images in Artifact Registry
gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}

# Should show your images
```

---

## Step 6: Prepare Environment Variables for Cloud Run

### 6.1 Create a `.env.cloudrun` file with production variables

**Create file**: `/Users/claudio/Documents/Personal/kos-database/backend/.env.cloudrun`

```env
# Flask Configuration
FLASK_ENV=production
DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/database

# Security (Update these!)
SECRET_KEY=your-production-secret-key-min-32-chars-change-this
JWT_SECRET_KEY=your-production-jwt-secret-key-min-32-chars-change-this
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Environment
APP_ENV=production
LOG_LEVEL=INFO
```

### 6.2 Important Variables Needed
You'll need to update:
- `DATABASE_URL` - Your PostgreSQL connection string
- `SECRET_KEY` - Generate a random 32+ character string
- `JWT_SECRET_KEY` - Generate a random 32+ character string
- `CORS_ORIGINS` - Your actual domain(s)

---

## Step 7: Deploy to Cloud Run

### 7.1 Deploy from Image in Artifact Registry
```bash
# Set variables
IMAGE_URL="asia-southeast1-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest"
SERVICE_NAME="kos-backend"
REGION="asia-southeast1"

# Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_URL} \
  --platform managed \
  --region=${REGION} \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --max-instances=10 \
  --set-env-vars="DATABASE_URL=your_postgres_url,FLASK_ENV=production,DEBUG=False,SECRET_KEY=your_secret,JWT_SECRET_KEY=your_jwt_secret,CORS_ORIGINS=your_domain"
```

**Important Notes:**
- `--allow-unauthenticated` makes your API public
- `--memory=512Mi` sets memory (adjust as needed)
- `--cpu=1` sets CPU allocation
- `--max-instances=10` sets auto-scaling limit
- Replace `your_postgres_url`, `your_secret`, etc. with actual values

### 7.2 Alternative: Use Secrets Manager for Sensitive Data
```bash
# Store DATABASE_URL in Secret Manager
echo -n "postgresql://user:password@host:5432/db" | \
  gcloud secrets create kos-db-url --data-file=-

# Store SECRET_KEY
echo -n "your-secret-key-32-chars-minimum" | \
  gcloud secrets create kos-secret-key --data-file=-

# Store JWT_SECRET_KEY
echo -n "your-jwt-secret-key-32-chars-minimum" | \
  gcloud secrets create kos-jwt-secret-key --data-file=-

# Deploy with secrets (REGION variable should already be set to asia-southeast1)
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_URL} \
  --platform managed \
  --region=${REGION} \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --set-env-vars="FLASK_ENV=production,DEBUG=False,CORS_ORIGINS=your_domain" \
  --set-secrets="DATABASE_URL=kos-db-url:latest,SECRET_KEY=kos-secret-key:latest,JWT_SECRET_KEY=kos-jwt-secret-key:latest"
```

---

## Step 8: Verify Deployment

### 8.1 Check Deployment Status
```bash
# Get the service URL
gcloud run services describe kos-backend --region asia-southeast1

# Should show:
# - Service URL: https://kos-backend-abc123-as.a.run.app
# - Status: OK
```

### 8.2 Get Service URL
```bash
# Get just the URL
gcloud run services describe kos-backend \
  --region asia-southeast1 \
  --format='value(status.url)'
```

### 8.3 Test the Deployment
```bash
# Replace with your actual URL from above
SERVICE_URL="https://kos-backend-abc123-as.a.run.app"

# Test health endpoint
curl ${SERVICE_URL}/health

# Test API root
curl ${SERVICE_URL}/api

# Expected responses:
# /health should return: {"status":"ok",...}
# /api should return: {"message":"Kos Management API",...}
```

### 8.4 Test Login Endpoint
```bash
# Replace SERVICE_URL with your actual URL
curl -X POST ${SERVICE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Expected response: {"access_token":"...","token_type":"bearer",...}
```

---

## Step 9: View Logs

### 9.1 Stream Logs from Cloud Run
```bash
# View real-time logs
gcloud run logs read kos-backend --region asia-southeast1 --limit 50

# Or continuous stream
gcloud run logs read kos-backend --region asia-southeast1 --tail
```

### 9.2 Check for Errors
```bash
# Get recent errors
gcloud run logs read kos-backend --region asia-southeast1 --limit 100 | grep -i error
```

---

## Step 10: Configure Custom Domain (Optional)

### 10.1 Map Custom Domain to Cloud Run
```bash
# Add custom domain mapping
gcloud run domain-mappings create \
  --service=kos-backend \
  --domain=api.yourdomain.com \
  --region=asia-southeast1

# Get DNS configuration
gcloud run domain-mappings describe api.yourdomain.com
```

### 10.2 Update DNS Records
Follow the DNS configuration shown in the output above to point your domain to Cloud Run.

---

## Step 11: Set Up Auto-Deployment (Optional)

### 11.1 Create Cloud Build Configuration
**Create file**: `cloudbuild.yaml` in backend directory

```yaml
steps:
  # Build the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/kos-backend/kos-backend:latest', '.']

  # Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/kos-backend/kos-backend:latest']

  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gke-deploy'
    args:
      - 'run'
      - '--filename=.'
      - '--image=asia-southeast1-docker.pkg.dev/$PROJECT_ID/kos-backend/kos-backend:latest'
      - '--location=asia-southeast1'
      - '--namespace=default'

images:
  - 'asia-southeast1-docker.pkg.dev/$PROJECT_ID/kos-backend/kos-backend:latest'
```

---

## Troubleshooting

### Issue: Image pull fails
**Solution**: Verify image is in Artifact Registry and service account has access

```bash
# Check image exists
gcloud artifacts docker images list asia-southeast1-docker.pkg.dev/${PROJECT_ID}/kos-backend
```

### Issue: Database connection fails
**Solution**: Verify:
1. DATABASE_URL is correct
2. PostgreSQL allows Cloud Run IP (if not public)
3. Network connectivity between Cloud Run and database

```bash
# Test from Cloud Run shell (if possible)
gcloud run services describe kos-backend --region asia-southeast1
```

### Issue: 403 Forbidden on Health Check
**Solution**: May be authentication issue. Check:
1. The health endpoint doesn't require auth (it shouldn't)
2. Verify logs: `gcloud run logs read kos-backend --region asia-southeast1 --limit 50`

### Issue: Out of Memory
**Solution**: Increase memory allocation

```bash
gcloud run deploy kos-backend \
  --memory=1Gi \
  --region asia-southeast1
```

---

## Performance Tuning

### Adjust CPU and Memory
```bash
# For production with expected load
gcloud run deploy kos-backend \
  --cpu=2 \
  --memory=2Gi \
  --max-instances=50 \
  --region asia-southeast1
```

### Set Min Instances (to avoid cold starts)
```bash
gcloud run deploy kos-backend \
  --min-instances=1 \
  --region asia-southeast1
```

---

## Cost Optimization

### Cloud Run Pricing
- Free tier: 2M requests/month
- After: $0.40 per million requests
- CPU/Memory: Billed per 100ms of execution

### Tips
1. Use `--max-instances` to prevent runaway costs
2. Use `--memory=512Mi` for simple APIs
3. Monitor with: `gcloud run describe kos-backend --region asia-southeast1`

---

## Full Deployment Commands Summary

```bash
# 1. Set project
gcloud config set project YOUR_PROJECT_ID

# 2. Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# 3. Create repository
gcloud artifacts repositories create kos-backend \
  --repository-format=docker \
  --location=asia-southeast1

# 4. Configure Docker auth
gcloud auth configure-docker asia-southeast1-docker.pkg.dev

# 5. Build image
docker buildx build --platform linux/amd64 -t kos-backend:latest --load .

# 6. Tag image
docker tag kos-backend:latest asia-southeast1-docker.pkg.dev/YOUR_PROJECT_ID/kos-backend/kos-backend:latest

# 7. Push image
docker push asia-southeast1-docker.pkg.dev/YOUR_PROJECT_ID/kos-backend/kos-backend:latest

# 8. Deploy
gcloud run deploy kos-backend \
  --image=asia-southeast1-docker.pkg.dev/YOUR_PROJECT_ID/kos-backend/kos-backend:latest \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --set-env-vars="DATABASE_URL=your_url,FLASK_ENV=production,DEBUG=False,SECRET_KEY=your_key,JWT_SECRET_KEY=your_jwt_key,CORS_ORIGINS=your_domain"

# 9. Get URL
gcloud run services describe kos-backend --region asia-southeast1 --format='value(status.url)'
```

---

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference/run)

---

**Notes:**
- Replace `YOUR_PROJECT_ID` with your actual GCP project ID
- Replace `your_domain.com` with your actual domain
- Generate strong random secrets for production
- Always use HTTPS URLs in CORS_ORIGINS
- Monitor costs in GCP Console

