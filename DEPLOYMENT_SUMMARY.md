# Kos Management System - Deployment Summary

Complete deployment information for the Kos Management System.

## Architecture Overview

```
┌────────────────────────────────────────┐
│         Vercel (Frontend)              │
│     React + TypeScript + Vite          │
│  URL: [Deploy and add URL here]        │
└───────────────┬────────────────────────┘
                │ HTTPS API Calls
                ▼
┌────────────────────────────────────────┐
│      GCP Cloud Run (Backend)           │
│         Flask REST API                 │
│  https://kos-backend-228057609267.     │
│    asia-southeast1.run.app             │
│                                        │
│  Region: asia-southeast1 (Singapore)   │
│  Memory: 256Mi | CPU: 1 vCPU          │
│  Instances: 0-3 (auto-scale)          │
└───────────────┬────────────────────────┘
                │ PostgreSQL Connection
                ▼
┌────────────────────────────────────────┐
│    Supabase PostgreSQL (Database)      │
│      Region: Tokyo (ap-northeast-1)    │
│      Tier: Free (500MB)                │
└────────────────────────────────────────┘
```

## Deployed Services

### Backend API (✅ Live)
- **URL:** https://kos-backend-228057609267.asia-southeast1.run.app
- **API Base:** https://kos-backend-228057609267.asia-southeast1.run.app/api
- **Health Check:** https://kos-backend-228057609267.asia-southeast1.run.app/health
- **Status:** Active and Running
- **Platform:** Google Cloud Run
- **Region:** Asia Southeast 1 (Singapore)
- **Project:** kontrakan-project

### Frontend (⏳ Ready to Deploy)
- **Platform:** Vercel
- **Framework:** React + TypeScript + Vite
- **Status:** Configured and ready for deployment
- **Backend Connection:** Configured

### Database (✅ Live)
- **Provider:** Supabase
- **Type:** PostgreSQL
- **Region:** Tokyo (ap-northeast-1)
- **Tier:** Free (500MB storage)
- **Status:** Active

## Quick Access Links

### Backend
- API Root: https://kos-backend-228057609267.asia-southeast1.run.app/api
- Health: https://kos-backend-228057609267.asia-southeast1.run.app/health
- Docs: https://kos-backend-228057609267.asia-southeast1.run.app/api/docs
- OpenAPI: https://kos-backend-228057609267.asia-southeast1.run.app/api/openapi.json

### Test Credentials
- Username: `admin`
- Password: `admin`

## Cost Summary

### Monthly Costs (Free Tier)
| Service | Tier | Cost |
|---------|------|------|
| GCP Cloud Run | Free (2M requests/month) | $0 |
| GCP Artifact Registry | Free (0.5GB) | $0 |
| Supabase PostgreSQL | Free (500MB) | $0 |
| Vercel | Free (Hobby) | $0 |
| **Total** | | **$0/month** |

### Free Tier Limits
- **Cloud Run:** 2M requests/month, 360k GB-seconds memory, 180k vCPU-seconds
- **Artifact Registry:** 0.5GB storage free
- **Supabase:** 500MB database, 2GB bandwidth
- **Vercel:** Unlimited deployments, 100GB bandwidth

## Configuration

### Backend Environment Variables (GCP Cloud Run)
```env
DATABASE_URL=postgresql://postgres.qcyftbttgyreoouazjfx:***@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=*
APP_ENV=production
LOG_LEVEL=INFO
```

### Frontend Environment Variables (Vercel)
```env
VITE_API_URL=https://kos-backend-228057609267.asia-southeast1.run.app/api
```

## Deployment Commands

### Backend (Already Deployed)
```bash
# Build
docker buildx build --platform linux/amd64 -t kos-backend:latest --load .

# Tag
docker tag kos-backend:latest asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest

# Push
docker push asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest

# Deploy
gcloud run deploy kos-backend \
  --image=asia-southeast1-docker.pkg.dev/kontrakan-project/kos-backend/kos-backend:latest \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory=256Mi \
  --cpu=1 \
  --max-instances=3
```

### Frontend (Next Steps)
```bash
# Option 1: Using Vercel CLI
cd frontend
npm install -g vercel
vercel login
vercel --prod

# Option 2: Using Vercel Dashboard
# 1. Push code to GitHub
# 2. Import repository to Vercel
# 3. Set root directory: frontend
# 4. Set build command: npm run build
# 5. Set output directory: dist
# 6. Add env var: VITE_API_URL=https://kos-backend-228057609267.asia-southeast1.run.app/api
# 7. Deploy
```

## Testing the Deployment

### Test Backend Health
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

### Test Authentication
```bash
curl -X POST https://kos-backend-228057609267.asia-southeast1.run.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### Test Protected Endpoint
```bash
TOKEN="your-token-from-login"
curl https://kos-backend-228057609267.asia-southeast1.run.app/api/rooms \
  -H "Authorization: Bearer $TOKEN"
```

## Monitoring

### View Backend Logs
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

### Monitor Costs
- GCP Console: https://console.cloud.google.com/billing
- Set up budget alerts at $1 threshold

## Performance

### Backend Performance
- **Cold Start:** 2-3 seconds (first request after idle)
- **Warm Response:** 100-300ms
- **Database Latency:** 50-150ms (Singapore to Tokyo)
- **Concurrent Requests:** Up to 80 per instance

### Frontend Performance (Expected)
- **Build Time:** ~30 seconds
- **Page Load:** < 2 seconds
- **Time to Interactive:** < 3 seconds
- **CDN:** Global edge network (Vercel)

## Security

### Implemented
- ✅ HTTPS only (enforced by Cloud Run and Vercel)
- ✅ JWT authentication
- ✅ Password hashing
- ✅ Environment variable secrets
- ✅ CORS configured
- ✅ SQL injection prevention (SQLAlchemy ORM)

### Recommended
- [ ] Update SECRET_KEY and JWT_SECRET_KEY with strong random values
- [ ] Restrict CORS_ORIGINS to Vercel domain after deployment
- [ ] Enable rate limiting
- [ ] Set up monitoring alerts
- [ ] Configure backup strategy
- [ ] Implement logging and error tracking

## Next Steps

### 1. Deploy Frontend to Vercel
```bash
cd frontend
vercel --prod
```

### 2. Update Backend CORS
After Vercel deployment, update backend CORS:
```bash
gcloud run services update kos-backend \
  --region asia-southeast1 \
  --update-env-vars="CORS_ORIGINS=https://your-vercel-app.vercel.app"
```

### 3. Update Frontend README
Add your Vercel URL to:
- `frontend/README.md` (line 7)
- This document

### 4. Test End-to-End
- Login from frontend
- Create/update/delete rooms
- Add tenants
- Record payments
- Check all features

### 5. Production Hardening
- Generate new SECRET_KEY and JWT_SECRET_KEY
- Update secrets in GCP Cloud Run
- Restrict CORS to specific domain
- Set up error monitoring (Sentry, etc.)
- Configure database backups

## Support & Documentation

- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
- [GCP Deployment Guide](./backend/GCP_DEPLOYMENT_GUIDE.md)
- [Migration Guide](./backend/MIGRATION_GUIDE.md)

## Troubleshooting

### Backend Issues
See [backend/README.md](./backend/README.md#troubleshooting)

### Frontend Issues
See [frontend/README.md](./frontend/README.md#troubleshooting)

### CORS Issues
```bash
# Allow all origins (development only)
gcloud run services update kos-backend \
  --region asia-southeast1 \
  --update-env-vars="CORS_ORIGINS=*"

# Restrict to specific domain (production)
gcloud run services update kos-backend \
  --region asia-southeast1 \
  --update-env-vars="CORS_ORIGINS=https://your-app.vercel.app"
```

## Rollback

### Rollback Backend
```bash
# List revisions
gcloud run revisions list --service=kos-backend --region=asia-southeast1

# Rollback to previous revision
gcloud run services update-traffic kos-backend \
  --region=asia-southeast1 \
  --to-revisions=REVISION_NAME=100
```

### Rollback Frontend (Vercel)
- Go to Vercel Dashboard
- Select deployment
- Click "Promote to Production"

## Contact

For issues and questions, please open an issue in the repository.

---

**Last Updated:** 2025-11-06
**Backend Status:** ✅ Deployed and Running
**Frontend Status:** ⏳ Ready for Deployment
**Total Cost:** $0/month (Free Tier)
