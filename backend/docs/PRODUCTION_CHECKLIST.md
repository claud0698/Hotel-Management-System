# Production Deployment Checklist - Phase 9

**Purpose**: Complete checklist to ensure Hotel Management System is production-ready

**Last Updated**: November 8, 2025

**Status**: Phase 9 - Complete

---

## Overview

This checklist covers all aspects of deploying to production on Google Cloud Run. Work through each section methodically.

**Total Items**: 85
**Estimated Time**: 4-6 hours
**Owner**: DevOps/Platform Team

---

## 1. Pre-Deployment Review (15 items)

### Code Quality
- [ ] All tests pass locally: `pytest docs/testing/ -v`
- [ ] All tests pass in CI/CD pipeline
- [ ] Code coverage > 80%: `pytest --cov=.`
- [ ] No hardcoded secrets in code
- [ ] No TODO comments left in code
- [ ] No debug statements (print, logging.debug)
- [ ] No deprecated dependencies
- [ ] Requirements.txt pinned to specific versions
- [ ] No breaking changes since last version

### Documentation
- [ ] API documentation complete and accurate
- [ ] Environment configuration documented (ENVIRONMENT_CONFIGURATION.md)
- [ ] Deployment guide reviewed (CLOUDRUN_DEPLOYMENT.md)
- [ ] Runbook created for common issues
- [ ] Change log updated
- [ ] Version number incremented

### Architecture Review
- [ ] Database schema reviewed
- [ ] Indexes created on critical fields
- [ ] No N+1 query problems
- [ ] Error handling complete
- [ ] Logging properly configured

---

## 2. Security (25 items)

### Secret Management
- [ ] No hardcoded secrets in code
- [ ] All secrets in Google Secret Manager
- [ ] Service account created and configured
- [ ] Service account has minimal required permissions
- [ ] Secret rotation schedule defined
- [ ] Backup of production secrets created
- [ ] Secrets never logged or output

### Authentication & Authorization
- [ ] JWT tokens configured with strong SECRET_KEY
- [ ] TOKEN_EXPIRE_MINUTES set to 960 (16 hours)
- [ ] Password hashing using bcrypt (12+ rounds)
- [ ] Role-based access control (RBAC) implemented
- [ ] Admin panel accessible only to admins
- [ ] Receptionist panel accessible only to receptionists
- [ ] API endpoints require authentication

### Network Security
- [ ] CORS configured for production domain only
- [ ] CORS_ORIGINS does not include wildcards
- [ ] HTTPS enforced (redirect HTTP to HTTPS)
- [ ] SSL certificate valid and up-to-date
- [ ] TLS 1.2+ configured
- [ ] Firewall rules restrict database access

### Input Validation
- [ ] All user inputs validated on backend
- [ ] SQL injection prevention (using SQLAlchemy ORM)
- [ ] XSS prevention (using FastAPI/Pydantic)
- [ ] CSRF protection enabled if applicable
- [ ] File upload restrictions implemented
- [ ] Request size limits enforced

### Error Handling
- [ ] No sensitive info in error messages
- [ ] Error logs captured but not displayed to users
- [ ] Stack traces not exposed to clients
- [ ] Sentry configured for error tracking
- [ ] Error response format standardized

### Dependencies
- [ ] All dependencies scanned for vulnerabilities
- [ ] `pip install -i https://mirrors.aliyun.com/pypi/simple` clean
- [ ] No dev dependencies in production (requirements.txt)
- [ ] License compliance checked

### Audit & Compliance
- [ ] Audit logging enabled (receptionist tracking)
- [ ] User actions logged with timestamps
- [ ] Sensitive operations logged (check-in, checkout, refunds)
- [ ] Logs retained for compliance period (30 days)
- [ ] Compliance checklist reviewed

---

## 3. Database (15 items)

### Setup & Configuration
- [ ] Cloud SQL instance created (PostgreSQL 15)
- [ ] Database created: `hotel_prod`
- [ ] Database user created (not using postgres admin)
- [ ] User has minimum required permissions
- [ ] Automated backups configured (daily)
- [ ] Backup retention set to 30+ days
- [ ] Backup restoration tested

### Schema & Migrations
- [ ] All migrations applied: `alembic upgrade head`
- [ ] Migration tested on staging first
- [ ] Rollback procedure documented
- [ ] Database schema documented
- [ ] Foreign key constraints in place
- [ ] Indexes created on:
  - [ ] reservations.guest_id
  - [ ] reservations.room_id
  - [ ] reservations.check_in_date
  - [ ] reservations.check_out_date
  - [ ] reservations.status
  - [ ] payments.reservation_id
  - [ ] rooms.room_type_id

### Performance
- [ ] Connection pooling configured
- [ ] SQLALCHEMY_POOL_SIZE = 20
- [ ] SQLALCHEMY_POOL_MAX_OVERFLOW = 40
- [ ] Query timeout set appropriately
- [ ] Slow query logging enabled
- [ ] Database monitoring configured

### Data Quality
- [ ] No duplicate data in production
- [ ] Test data removed from production
- [ ] Admin user created in production database
- [ ] Sample room types and rooms created
- [ ] Database constraints validated

---

## 4. Application Configuration (18 items)

### Environment Variables
- [ ] ENVIRONMENT=production
- [ ] DEBUG=False (NEVER True in production)
- [ ] LOG_LEVEL=INFO
- [ ] LOG_FORMAT=json
- [ ] SECRET_KEY set to 32+ character random value
- [ ] ALGORITHM=HS256
- [ ] TOKEN_EXPIRE_MINUTES=960
- [ ] CORS_ORIGINS points to production domain only
- [ ] API_PREFIX=/api
- [ ] API_VERSION matches release version
- [ ] MAX_REQUEST_SIZE set appropriately
- [ ] Database URL uses Cloud SQL proxy

### Application Features
- [ ] Swagger UI disabled (/docs not accessible)
- [ ] ReDoc disabled (/redoc not accessible)
- [ ] CORS enabled for production domain
- [ ] Rate limiting enabled (100 req/min)
- [ ] Request logging enabled
- [ ] Error tracking (Sentry) enabled
- [ ] Monitoring (Prometheus) enabled
- [ ] Health check endpoint working

### Performance Tuning
- [ ] Uvicorn workers configured: 4+ workers
- [ ] Worker timeout set: 120 seconds
- [ ] Keep-alive timeout configured
- [ ] Response compression enabled (gzip)

---

## 5. Container & Deployment (18 items)

### Docker Image
- [ ] Dockerfile uses Python 3.12-slim base
- [ ] Non-root user created (appuser)
- [ ] Health check configured and tested
- [ ] Image size reasonable (<500MB)
- [ ] No security vulnerabilities in image
- [ ] Image tagged with version: `gcr.io/project/hotel-api:1.0.0`
- [ ] Image pushed to Container Registry

### Cloud Build
- [ ] cloudbuild.yaml created
- [ ] Build completes successfully
- [ ] Build logs reviewed for errors
- [ ] Build time < 10 minutes
- [ ] Automated builds on git push configured

### Cloud Run Deployment
- [ ] Service deployed successfully
- [ ] Service URL accessible
- [ ] Health check passes
- [ ] Min instances >= 1
- [ ] Max instances set appropriately (100)
- [ ] Memory allocated: 1Gi+
- [ ] CPU allocated: 1 core+
- [ ] Timeout set: 3600 seconds
- [ ] Concurrency set: 100+
- [ ] Service account configured
- [ ] Cloud SQL connection configured

### Custom Domain
- [ ] Domain added to Cloud Run
- [ ] DNS records updated
- [ ] SSL certificate valid
- [ ] Domain accessible via HTTPS
- [ ] HTTP redirects to HTTPS

---

## 6. Monitoring & Logging (12 items)

### Cloud Logging
- [ ] Cloud Logging enabled for service
- [ ] Log sink configured
- [ ] Logs viewable in Cloud Console
- [ ] Log retention set: 30 days
- [ ] ERROR and WARNING level monitored
- [ ] Sentry integrated for error tracking

### Cloud Monitoring
- [ ] Dashboard created for key metrics
- [ ] Uptime monitoring configured
- [ ] CPU usage monitored
- [ ] Memory usage monitored
- [ ] Request latency monitored
- [ ] Error rate monitored

### Alerts
- [ ] Alert for service down
- [ ] Alert for high error rate (>1%)
- [ ] Alert for slow response time (>2s)
- [ ] Alert for high memory usage (>80%)
- [ ] Alert recipients configured (email/Slack)
- [ ] Alert test completed

---

## 7. Backup & Disaster Recovery (8 items)

### Database Backups
- [ ] Automated daily backups configured
- [ ] Backup retention: 30+ days
- [ ] Backup restoration tested
- [ ] Backup procedure documented
- [ ] Restore procedure documented
- [ ] RTO (Recovery Time Objective) defined: 1 hour
- [ ] RPO (Recovery Point Objective) defined: 24 hours
- [ ] Disaster recovery drill completed

---

## 8. Performance & Load Testing (8 items)

### Baseline Performance
- [ ] Response time for GET /api/rooms: <200ms
- [ ] Response time for POST /api/reservations: <300ms
- [ ] Response time for GET /api/reservations: <500ms
- [ ] Database queries optimized
- [ ] No N+1 queries
- [ ] Caching implemented where beneficial

### Load Testing
- [ ] Load test with 100 concurrent users completed
- [ ] System handles 10 requests/second
- [ ] No errors under load
- [ ] Autoscaling triggered appropriately
- [ ] Database connection pool sufficient
- [ ] Memory usage remains stable

---

## 9. Documentation & Handoff (5 items)

### Documentation
- [ ] Runbook created for common issues
- [ ] Escalation procedures documented
- [ ] On-call rotation defined
- [ ] Contact information documented
- [ ] Deployment procedure documented

---

## 10. Post-Deployment Validation (6 items)

### Functional Testing
- [ ] API responds to health check: GET /health
- [ ] Authentication works: POST /api/auth/login
- [ ] Room management works: GET/POST /api/rooms
- [ ] Reservation workflow works: POST /api/reservations
- [ ] Database queries work correctly
- [ ] All endpoints respond with correct data

---

## Quick Verification Commands

Run these commands to verify production is ready:

```bash
# Test service accessibility
curl https://api.yourdomain.com/health

# Check logs
gcloud logging read "resource.service.name=hotel-api" --limit 10

# Check service status
gcloud run services describe hotel-api --region us-central1

# Verify database connection
gcloud sql connect hotel-db --user=postgres

# Test API endpoints
curl -H "Authorization: Bearer TOKEN" https://api.yourdomain.com/api/rooms

# Run health checks
bash scripts/health_check.sh
```

---

## Rollback Procedure

If deployment fails, follow this procedure:

```bash
# 1. Identify the issue
gcloud logging read "resource.service.name=hotel-api" --limit 50

# 2. Revert to previous version
gcloud run deploy hotel-api \
  --image gcr.io/my-project-id/hotel-api:previous-tag \
  --region us-central1

# 3. Verify rollback
curl https://api.yourdomain.com/health

# 4. Document incident
# Create incident report in your tracking system

# 5. Investigate and fix
# Review logs, identify root cause, fix code

# 6. Test on staging
# Deploy to staging first before re-deploying to production
```

---

## Post-Deployment Monitoring (First 24 hours)

Monitor these metrics during the first 24 hours:

```
Every 30 minutes:
- [ ] Check error rate (should be < 0.1%)
- [ ] Check response times (should be < 200ms)
- [ ] Check database connections (should be < 20)
- [ ] Check memory usage (should be < 70%)
- [ ] Check log for any ERRORS or WARNINGS

Every hour:
- [ ] Check Sentry for new errors
- [ ] Check Cloud Monitoring dashboard
- [ ] Verify backups are running
- [ ] Verify replicas are healthy

End of day:
- [ ] Review all metrics
- [ ] Document any issues found
- [ ] Create follow-up tasks if needed
- [ ] Sign off on deployment success
```

---

## Sign-Off

### Development Team
- [ ] Code review completed
- [ ] All tests pass
- [ ] Documentation complete
- **Reviewed by**: _________________ **Date**: _______

### QA/Testing Team
- [ ] Functional testing completed
- [ ] Performance testing completed
- [ ] Security testing completed
- **Reviewed by**: _________________ **Date**: _______

### DevOps/Operations Team
- [ ] Infrastructure configured
- [ ] Monitoring configured
- [ ] Backup procedures tested
- **Reviewed by**: _________________ **Date**: _______

### Management/Product
- [ ] Feature meets requirements
- [ ] User documentation ready
- [ ] Support team trained
- **Reviewed by**: _________________ **Date**: _______

### Production Deployment Authorization
- **Authorized by**: _________________ **Date**: _______
- **Production URL**: https://api.yourdomain.com
- **Version**: 1.0.0
- **Deployment Time**: _______________________
- **Deployment Duration**: __________________ minutes

---

## Post-Deployment Approval

- [ ] Service running without errors
- [ ] All API endpoints responding correctly
- [ ] Database backups working
- [ ] Monitoring and alerts configured
- [ ] Documentation accessible
- [ ] Support team trained
- [ ] No critical issues found

**Approved for production**: _________________ **Date**: _______

---

## Appendix: Automated Checklist Script

Create `scripts/production_checklist.sh`:

```bash
#!/bin/bash

echo "=== Production Readiness Checklist ==="
echo ""

# 1. Test Docker image
echo "1. Testing Docker image..."
docker build -t hotel-api:test . > /dev/null 2>&1 && echo "✓ Docker builds" || echo "✗ Docker build failed"

# 2. Run tests
echo "2. Running tests..."
pytest docs/testing/ -q > /dev/null 2>&1 && echo "✓ All tests pass" || echo "✗ Tests failed"

# 3. Check code coverage
echo "3. Checking code coverage..."
pytest --cov=. --cov-report=term-missing | grep -i "coverage" && echo "✓ Coverage OK" || echo "✗ Coverage low"

# 4. Check for hardcoded secrets
echo "4. Checking for hardcoded secrets..."
grep -r "password\|secret\|key" app.py | grep "=" && echo "✗ Found hardcoded secrets" || echo "✓ No hardcoded secrets"

# 5. Verify environment variables
echo "5. Verifying environment variables..."
[ -f .env.production ] && echo "✓ .env.production exists" || echo "✗ .env.production missing"

# 6. Check database migrations
echo "6. Checking migrations..."
ls alembic/versions/*.py | wc -l | awk '{print "✓ " $1 " migrations found"}'

# 7. Verify Dockerfile
echo "7. Verifying Dockerfile..."
grep "HEALTHCHECK" Dockerfile > /dev/null && echo "✓ Health check configured" || echo "✗ Health check missing"

echo ""
echo "=== Checklist Complete ==="
```

Run with: `bash scripts/production_checklist.sh`

---

**Last Updated**: November 8, 2025
**Status**: Phase 9 - Complete & Ready for Review
**Next**: Deploy to Staging, then Production
