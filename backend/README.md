# Kos Management System - Backend API

Flask-based REST API for managing Kos (boarding house) operations, including room management, tenant tracking, and payment processing.

## Production Deployment

**Service URL:** https://kos-backend-228057609267.asia-southeast1.run.app

**Status:** ✅ Active and Running
**Region:** Asia Southeast 1 (Singapore)
**Platform:** Google Cloud Run
**Database:** Supabase PostgreSQL (Tokyo region)
**Architecture:** Docker container (linux/amd64)
**Free Tier:** $0/month (within limits)

## Quick Links

- **API Root:** https://kos-backend-228057609267.asia-southeast1.run.app/api
- **Health Check:** https://kos-backend-228057609267.asia-southeast1.run.app/health
- **API Docs:** https://kos-backend-228057609267.asia-southeast1.run.app/api/docs
- **OpenAPI Spec:** https://kos-backend-228057609267.asia-southeast1.run.app/api/openapi.json

## Architecture

```
┌─────────────────────────────────────┐
│   Vercel Frontend (React)           │
│   - Next.js / React App             │
└────────────┬────────────────────────┘
             │ HTTPS
             ▼
┌─────────────────────────────────────┐
│  GCP Cloud Run (Backend)            │
│  - Flask REST API                   │
│  - JWT Authentication               │
│  - 256Mi RAM / 1 CPU                │
│  - Auto-scaling (0-3 instances)     │
│  - Region: asia-southeast1          │
└────────────┬────────────────────────┘
             │ PostgreSQL
             ▼
┌─────────────────────────────────────┐
│  Supabase PostgreSQL (Free Tier)   │
│  - 500MB storage                    │
│  - Region: ap-northeast-1 (Tokyo)   │
└─────────────────────────────────────┘
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info (requires auth)

### Rooms
- `GET /api/rooms` - List all rooms
- `POST /api/rooms` - Create new room (requires auth)
- `GET /api/rooms/{id}` - Get room details
- `PUT /api/rooms/{id}` - Update room (requires auth)
- `DELETE /api/rooms/{id}` - Delete room (requires auth)

### Tenants
- `GET /api/tenants` - List all tenants
- `POST /api/tenants` - Create new tenant (requires auth)
- `GET /api/tenants/{id}` - Get tenant details
- `PUT /api/tenants/{id}` - Update tenant (requires auth)
- `DELETE /api/tenants/{id}` - Delete tenant (requires auth)

### Payments
- `GET /api/payments` - List all payments
- `POST /api/payments` - Record new payment (requires auth)
- `GET /api/payments/{id}` - Get payment details
- `PUT /api/payments/{id}` - Update payment (requires auth)
- `DELETE /api/payments/{id}` - Delete payment (requires auth)

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics (requires auth)

### Health
- `GET /health` - Health check endpoint

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Getting a Token

```bash
curl -X POST https://kos-backend-228057609267.asia-southeast1.run.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Response:
```json
{
  "access_token": "your-jwt-token",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "created_at": "2025-11-06T12:54:32.183294"
  }
}
```

### Using the Token

Include the token in the Authorization header:

```bash
curl https://kos-backend-228057609267.asia-southeast1.run.app/api/rooms \
  -H "Authorization: Bearer your-jwt-token"
```

## Frontend Integration

### Configure Frontend Environment Variables

In your Vercel project, add this environment variable:

```bash
REACT_APP_API_URL=https://kos-backend-228057609267.asia-southeast1.run.app
# or
NEXT_PUBLIC_API_URL=https://kos-backend-228057609267.asia-southeast1.run.app
```

### Example API Call from Frontend

```javascript
// Using fetch
const response = await fetch('https://kos-backend-228057609267.asia-southeast1.run.app/api/rooms', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// Using axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://kos-backend-228057609267.asia-southeast1.run.app',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Make request
const rooms = await api.get('/api/rooms');
```

## Table of Contents

- [Local Development](#local-development)
- [Building the Application](#building-the-application)
- [Deployment to GCP Cloud Run](#deployment-to-gcp-cloud-run)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Database Management](#database-management)
- [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites
- Python 3.11+
- Docker (for containerized development)
- PostgreSQL or Supabase account
- pip and virtualenv

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/claud0698/kos-database.git
cd kos-database/backend
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required variables in `.env`:
```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars

# App Config
FLASK_ENV=development
DEBUG=True
PORT=8001
CORS_ORIGINS=*
```

5. **Run the application:**
```bash
python app.py
```

The API will be available at http://localhost:8001

### Testing Locally

```bash
# Test health endpoint
curl http://localhost:8001/health

# Test login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## Building the Application

### Build Docker Image Locally

1. **Build for local testing (ARM/M1 Macs):**
```bash
docker build -t kos-backend:latest .
```

2. **Build for production (amd64 for Cloud Run):**
```bash
docker buildx build \
  --platform linux/amd64 \
  -t kos-backend:latest \
  --load \
  .
```

3. **Test the Docker image:**
```bash
# Run container locally
docker run -p 8080:8080 \
  -e DATABASE_URL="your_postgres_url" \
  -e SECRET_KEY="your_secret_key" \
  -e JWT_SECRET_KEY="your_jwt_secret_key" \
  kos-backend:latest

# Test in another terminal
curl http://localhost:8080/health
```

### Docker Image Details

- **Base Image:** python:3.11-slim
- **Port:** 8080 (Cloud Run requirement)
- **User:** appuser (non-root for security)
- **Size:** ~700MB
- **Architecture:** linux/amd64 (Cloud Run compatible)

---

## Deployment to GCP Cloud Run

### Prerequisites
- GCP Account with billing enabled
- `gcloud` CLI installed and configured
- Docker installed locally
- Project ID: `kontrakan-project`

### Step-by-Step Deployment

#### 1. Configure GCP

```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project kontrakan-project

# Set region
gcloud config set run/region asia-southeast1

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### 2. Create Artifact Registry Repository

```bash
# Create Docker repository
gcloud artifacts repositories create kos-backend \
  --repository-format=docker \
  --location=asia-southeast1 \
  --description="Kos Management System Backend"

# Configure Docker authentication
gcloud auth configure-docker asia-southeast1-docker.pkg.dev
```

#### 3. Build and Push Image

```bash
# Navigate to backend directory
cd backend

# Build image for amd64
docker buildx build \
  --platform linux/amd64 \
  -t kos-backend:latest \
  --load \
  .

# Tag for Artifact Registry
docker tag kos-backend:latest \
  asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest

# Push to Artifact Registry
docker push \
  asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest
```

#### 4. Deploy to Cloud Run

```bash
# Deploy with free tier settings
gcloud run deploy kos-backend \
  --image=asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory=256Mi \
  --cpu=1 \
  --timeout=60 \
  --max-instances=3 \
  --min-instances=0 \
  --cpu-throttling \
  --concurrency=80 \
  --set-env-vars="DATABASE_URL=your_supabase_url,FLASK_ENV=production,DEBUG=False,SECRET_KEY=your_secret,JWT_SECRET_KEY=your_jwt_secret,CORS_ORIGINS=*"
```

#### 5. Verify Deployment

```bash
# Get service URL
gcloud run services describe kos-backend \
  --region asia-southeast1 \
  --format='value(status.url)'

# Test the deployment
curl https://kos-backend-228057609267.asia-southeast1.run.app/health
```

### Update Deployment

To update the deployed application:

```bash
# 1. Make your code changes

# 2. Rebuild and push
docker buildx build --platform linux/amd64 -t kos-backend:latest --load .
docker tag kos-backend:latest asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest
docker push asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest

# 3. Redeploy (Cloud Run will automatically use the new image)
gcloud run deploy kos-backend \
  --image=asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest \
  --region asia-southeast1
```

### Deployment Configuration

**Free Tier Optimized Settings:**
- Memory: 256Mi (minimum)
- CPU: 1 vCPU with throttling
- Min Instances: 0 (scales to zero)
- Max Instances: 3 (cost control)
- Timeout: 60 seconds
- Concurrency: 80 requests/instance

**Monthly Costs:** $0 (within free tier limits)

### View Logs

```bash
# Real-time logs
gcloud run services logs read kos-backend --region asia-southeast1 --tail

# Recent logs
gcloud run services logs read kos-backend --region asia-southeast1 --limit 100

# Filter errors
gcloud run services logs read kos-backend --region asia-southeast1 --limit 100 | grep -i error
```

### Rollback Deployment

```bash
# List revisions
gcloud run revisions list --service=kos-backend --region=asia-southeast1

# Rollback to specific revision
gcloud run services update-traffic kos-backend \
  --region=asia-southeast1 \
  --to-revisions=REVISION_NAME=100
```

---

### Environment Variables

```env
# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py
DEBUG=True
PORT=8001

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/database

# CORS Configuration
CORS_ORIGINS=*  # Restrict in production

# Environment
APP_ENV=development
LOG_LEVEL=INFO
```

## Deployment

### Deploy to Google Cloud Run

Follow the [GCP Deployment Guide](./GCP_DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

Quick deployment:

```bash
# 1. Build image
docker buildx build --platform linux/amd64 -t kos-backend:latest --load .

# 2. Tag for GCP
docker tag kos-backend:latest asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest

# 3. Push to Artifact Registry
docker push asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest

# 4. Deploy to Cloud Run
gcloud run deploy kos-backend \
  --image=asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory=256Mi \
  --set-env-vars="DATABASE_URL=your_url,FLASK_ENV=production,..."
```

## Database Schema

### Tables

#### users
- `id` - Primary key
- `username` - Unique username
- `password_hash` - Hashed password
- `created_at` - Timestamp
- `updated_at` - Timestamp

#### rooms
- `id` - Primary key
- `room_number` - Unique room identifier
- `floor` - Floor number
- `room_type` - Type (single, shared, etc.)
- `monthly_rate` - Monthly rent price
- `status` - Status (available, occupied, maintenance)
- `amenities` - Room amenities
- `created_at` - Timestamp
- `updated_at` - Timestamp

#### tenants
- `id` - Primary key
- `name` - Tenant name
- `phone` - Contact phone
- `email` - Email address
- `id_number` - National ID number
- `move_in_date` - Move-in date
- `move_out_date` - Move-out date (nullable)
- `current_room_id` - Foreign key to rooms
- `status` - Status (active, inactive)
- `notes` - Additional notes
- `created_at` - Timestamp
- `updated_at` - Timestamp

#### payments
- `id` - Primary key
- `tenant_id` - Foreign key to tenants
- `room_id` - Foreign key to rooms
- `amount` - Payment amount
- `payment_date` - Date of payment
- `payment_method` - Payment method (cash, transfer, etc.)
- `status` - Status (paid, pending, overdue)
- `notes` - Additional notes
- `created_at` - Timestamp
- `updated_at` - Timestamp

## Performance & Costs

### Free Tier Configuration
- **Memory:** 256Mi (minimum for Cloud Run)
- **CPU:** 1 vCPU with CPU throttling
- **Min Instances:** 0 (scales to zero when idle)
- **Max Instances:** 3 (prevents runaway costs)
- **Timeout:** 60 seconds
- **Concurrency:** 80 requests per instance

### Monthly Costs (within free tier)
- **Cloud Run:** $0 (within 2M requests/month)
- **Artifact Registry:** $0 (within 0.5GB storage)
- **Supabase:** $0 (free tier)
- **Total:** $0/month for low-moderate traffic

### Expected Performance
- **Cold start:** 2-3 seconds (first request after idle)
- **Warm response:** 100-300ms
- **Database latency:** 50-150ms (Singapore to Tokyo)

## Monitoring

### View Logs
```bash
# Real-time logs
gcloud run logs tail kos-backend --region asia-southeast1

# Recent logs
gcloud run logs read kos-backend --region asia-southeast1 --limit 100
```

### Check Service Status
```bash
gcloud run services describe kos-backend --region asia-southeast1
```

### Health Check
```bash
curl https://kos-backend-228057609267.asia-southeast1.run.app/health
```

Expected response:
```json
{
  "status": "ok",
  "environment": "production",
  "database": "postgresql",
  "timestamp": "2025-11-06T13:16:34.451147"
}
```

## Security

### Best Practices Implemented
- ✅ JWT token authentication
- ✅ Password hashing with werkzeug
- ✅ HTTPS only (enforced by Cloud Run)
- ✅ CORS configured
- ✅ Environment variables for secrets
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Input validation

### Production Security Checklist
- [ ] Update SECRET_KEY and JWT_SECRET_KEY
- [ ] Restrict CORS_ORIGINS to your frontend domain
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular security updates
- [ ] Database backups

## Troubleshooting

### Issue: 502 Bad Gateway
**Solution:** Check logs for startup errors
```bash
gcloud run logs read kos-backend --region asia-southeast1 --limit 50
```

### Issue: Database Connection Failed
**Solution:** Verify DATABASE_URL is correct and Supabase allows connections

### Issue: Authentication Failed
**Solution:** Check JWT_SECRET_KEY matches between deployments

### Issue: CORS Errors
**Solution:** Update CORS_ORIGINS to include your frontend domain

## Support & Documentation

- [GCP Deployment Guide](./GCP_DEPLOYMENT_GUIDE.md)
- [Migration Guide](./MIGRATION_GUIDE.md)
- [Test Report](./TEST_REPORT.md)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)

## License

MIT License

## Contact

For issues and questions, please open an issue in the repository.

---

**Last Updated:** 2025-11-06
**Version:** 1.0.0
**Deployment:** Production on GCP Cloud Run
