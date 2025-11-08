# Environment Configuration Guide - Phase 9

**Purpose**: Complete guide for setting up environment variables and configuration for development, testing, and production

**Last Updated**: November 8, 2025

**Status**: Phase 9 - Ready for Deployment

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Development Environment](#development-environment)
3. [Testing Environment](#testing-environment)
4. [Production Environment](#production-environment)
5. [Database Configuration](#database-configuration)
6. [Security Configuration](#security-configuration)
7. [API Configuration](#api-configuration)
8. [Logging Configuration](#logging-configuration)
9. [Deployment Environments](#deployment-environments)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Local Development (5 minutes)

```bash
cd backend

# Create .env.local for development
cat > .env.local << 'EOF'
# Basic Settings
APP_NAME=Hotel Management System
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hotel_dev
SQLALCHEMY_ECHO=True

# JWT Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=960

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# API Configuration
API_PREFIX=/api
API_VERSION=1.0.0

# Logging
LOG_FORMAT=json
LOG_OUTPUT=console
EOF

# Load environment
export $(cat .env.local | xargs)

# Run application
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

### 2. Testing (2 minutes)

```bash
cd backend

# Tests use in-memory SQLite by default
# Run all tests
pytest docs/testing/ -v

# Run specific test file
pytest docs/testing/test_integration_rooms_reservations.py -v

# Generate coverage report
pytest --cov=. --cov-report=html
```

### 3. Production (see Production Environment section)

---

## Development Environment

### .env.local Configuration

```env
# ============================================================================
# DEVELOPMENT ENVIRONMENT VARIABLES
# ============================================================================

# Application Settings
APP_NAME=Hotel Management System
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/hotel_dev
SQLALCHEMY_ECHO=True                          # Log all SQL queries
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_POOL_RECYCLE=3600

# JWT & Security
SECRET_KEY=dev-secret-key-12345              # Change this!
ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=960                      # 16 hours for shift-based

# CORS - Allow local development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000

# API Configuration
API_PREFIX=/api
API_VERSION=1.0.0
MAX_REQUEST_SIZE=10485760                     # 10MB

# Logging
LOG_FORMAT=text                               # human-readable in development
LOG_OUTPUT=console
LOG_FILE=logs/app.log
LOG_ROTATION=10485760                         # Rotate at 10MB

# Features
ENABLE_CORS=true
ENABLE_SWAGGER=true                           # Enable /docs

# Rate Limiting
RATE_LIMIT_ENABLED=false                      # Disable for development
```

### Running Development Server

```bash
# Start with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8001

# Access API
# - Swagger UI: http://localhost:8001/docs
# - ReDoc: http://localhost:8001/redoc
# - API: http://localhost:8001/api/...
```

### Development Database Setup

```bash
# Using PostgreSQL locally
docker run -d \
  --name postgres-dev \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=hotel_dev \
  -p 5432:5432 \
  postgres:15

# Create admin user
psql -h localhost -U postgres -d hotel_dev << 'EOF'
INSERT INTO users (username, password_hash, role, created_at)
VALUES (
  'admin',
  'admin123',  -- In real scenario, this is hashed
  'admin',
  NOW()
);
EOF
```

---

## Testing Environment

### .env.test Configuration

```env
# ============================================================================
# TESTING ENVIRONMENT VARIABLES
# ============================================================================

# Use in-memory SQLite (default in conftest.py)
ENVIRONMENT=testing
DEBUG=True
LOG_LEVEL=INFO

# Testing API
TEST_API_URL=http://localhost:8001

# JWT Settings (same as development)
SECRET_KEY=test-secret-key
ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=960

# Disable external services in tests
RATE_LIMIT_ENABLED=false
ENABLE_CORS=false
```

### Running Tests

```bash
# Run all tests
pytest docs/testing/ -v

# Run specific test class
pytest docs/testing/test_integration_rooms_reservations.py::TestStandardBookingWorkflow -v

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term-missing

# Run in parallel (faster)
pytest -n auto docs/testing/

# Run with detailed output
pytest -vv --tb=long docs/testing/

# Run only integration tests
pytest docs/testing/test_integration_rooms_reservations.py -v

# Run with specific markers
pytest -m "integration" -v
```

### Test Database

```python
# conftest.py uses in-memory SQLite
# Database is created fresh for each test session
# No configuration needed!

@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine
```

---

## Production Environment

### .env.production Configuration

```env
# ============================================================================
# PRODUCTION ENVIRONMENT VARIABLES
# ============================================================================

# Application Settings
APP_NAME=Hotel Management System
ENVIRONMENT=production
DEBUG=False                                   # NEVER True in production
LOG_LEVEL=INFO

# Database Configuration (Cloud SQL/RDS)
DATABASE_URL=postgresql://user:password@cloud-db.example.com:5432/hotel_prod
SQLALCHEMY_ECHO=False                         # Don't log queries in production
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_POOL_MAX_OVERFLOW=40
SQLALCHEMY_POOL_RECYCLE=3600
SQLALCHEMY_POOL_PRE_PING=true                 # Test connections before use

# JWT & Security
SECRET_KEY=your-production-secret-key-min-32-chars-change-monthly
ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=960

# CORS - Only allow frontend domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# API Configuration
API_PREFIX=/api
API_VERSION=1.0.0
MAX_REQUEST_SIZE=10485760

# Logging
LOG_FORMAT=json                               # Machine-readable for logs aggregation
LOG_OUTPUT=file
LOG_FILE=/var/log/hotel-api/app.log
LOG_ROTATION=52428800                         # Rotate at 50MB
LOG_RETENTION=30                              # Keep logs for 30 days

# Features
ENABLE_CORS=true
ENABLE_SWAGGER=false                          # Disable /docs in production

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60                          # 100 requests per minute

# Error Reporting
SENTRY_DSN=https://key@sentry.io/project
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Monitoring
ENABLE_METRICS=true
PROMETHEUS_PORT=8002                          # Separate metrics port
```

### Security Checklist

```bash
# 1. Generate secure SECRET_KEY (32+ chars)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Update database credentials
# Don't store in .env file in production
# Use environment variables from deployment platform

# 3. Verify CORS settings
# Only allow your frontend domain

# 4. Enable HTTPS
# All production APIs must use HTTPS

# 5. Rotate secrets monthly
# Keep old secret in LEGACY_SECRET_KEY during rotation window

# 6. Monitor API logs
# Setup log aggregation (ELK, Datadog, etc)
```

### Production Database Setup

```bash
# Using Cloud SQL (GCP) or RDS (AWS)

# Option 1: GCP Cloud SQL
gcloud sql instances create hotel-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create hotel_prod \
  --instance=hotel-db

# Create user
gcloud sql users create dbuser \
  --instance=hotel-db \
  --password=random-secure-password

# Option 2: AWS RDS
aws rds create-db-instance \
  --db-instance-identifier hotel-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password 'random-secure-password'
```

---

## Database Configuration

### PostgreSQL Configuration

```env
# Development
DATABASE_URL=postgresql://user:pass@localhost:5432/hotel_dev

# Production (Cloud SQL GCP)
DATABASE_URL=postgresql://user:pass@/hotel_prod?unix_socket_dir=/cloudsql/project:region:instance

# Production (RDS AWS)
DATABASE_URL=postgresql://user:pass@hotel-db.xxxxx.us-east-1.rds.amazonaws.com:5432/hotel_prod

# Pooling Configuration
SQLALCHEMY_POOL_SIZE=20                       # Connections to keep in pool
SQLALCHEMY_POOL_MAX_OVERFLOW=40              # Additional connections allowed
SQLALCHEMY_POOL_RECYCLE=3600                 # Recycle after 1 hour
SQLALCHEMY_POOL_PRE_PING=true                # Test before use (detects stale connections)
```

### Connection String Format

```
postgresql://username:password@host:port/database

Components:
- username: Database user (not admin in production)
- password: Secure password (min 20 chars)
- host: Localhost or cloud database host
- port: 5432 (default PostgreSQL)
- database: database name
```

### Database Initialization

```python
# In app.py or startup script
from sqlalchemy import create_engine
from models import Base
from database import init_db

# Create tables on startup
def startup():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    init_db()  # Create default users, room types, etc

# Run migrations instead (recommended for production)
# alembic upgrade head
```

---

## Security Configuration

### JWT Configuration

```env
# Secret Key - Change IMMEDIATELY in production
SECRET_KEY=dev-key-change-this                # Development
SECRET_KEY=<32+ character random string>      # Production

# Algorithm
ALGORITHM=HS256                               # HS256 is sufficient for this project

# Token Expiration
TOKEN_EXPIRE_MINUTES=960                      # 16 hours (shift-based)

# Optional: Refresh token configuration
REFRESH_TOKEN_EXPIRE_DAYS=30
```

### Generating Secure Secret Key

```bash
# Using Python
python << 'EOF'
import secrets
key = secrets.token_urlsafe(32)
print(f"SECRET_KEY={key}")
EOF

# Using OpenSSL
openssl rand -base64 32

# Using Ruby
ruby -e "puts SecureRandom.random_bytes(32).unpack('H*').first"
```

### Password Hashing

```python
# In security.py
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increase for production (slower but more secure)
)

# Hash password
hashed = pwd_context.hash("password123")

# Verify password
is_valid = pwd_context.verify("password123", hashed)
```

### CORS Configuration

```env
# Development (allow multiple local ports)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000

# Production (only your domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Allowed methods and headers are set in app.py
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Authorization
```

### HTTPS/TLS Configuration

```env
# Production ONLY
HTTPS_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/your-cert.pem
SSL_KEY_PATH=/etc/ssl/private/your-key.pem

# Or use reverse proxy (nginx) to handle HTTPS
```

---

## API Configuration

### Rate Limiting

```env
# Development
RATE_LIMIT_ENABLED=false

# Production
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100                       # Requests per period
RATE_LIMIT_PERIOD=60                          # Seconds (60 = per minute)
RATE_LIMIT_STORAGE=redis                      # redis or memory
```

### Request Size Limits

```env
MAX_REQUEST_SIZE=10485760                     # 10MB
MAX_UPLOAD_SIZE=5242880                       # 5MB for images
```

### API Versioning

```env
API_PREFIX=/api
API_VERSION=1.0.0

# In code
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["reservations"])

@router.get("/reservations")
async def list_reservations():
    pass
```

### Pagination

```env
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

---

## Logging Configuration

### Log Levels

```env
# Development
LOG_LEVEL=DEBUG                               # All messages

# Production
LOG_LEVEL=INFO                                # Info and above (no debug)
```

### Log Format

```env
# Development (human-readable)
LOG_FORMAT=text
LOG_OUTPUT=console

# Production (machine-readable JSON)
LOG_FORMAT=json
LOG_OUTPUT=file
LOG_FILE=/var/log/hotel-api/app.log
```

### Log Rotation

```env
LOG_ROTATION=52428800                         # Rotate at 50MB
LOG_RETENTION=30                              # Keep for 30 days

# Using logrotate
# /etc/logrotate.d/hotel-api
/var/log/hotel-api/app.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    postrotate
        systemctl reload hotel-api > /dev/null 2>&1 || true
    endscript
}
```

### Logging to External Services

```env
# Sentry (error tracking)
SENTRY_DSN=https://key@sentry.io/project
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1                 # Sample 10% of traces

# DataDog (APM)
DD_AGENT_HOST=localhost
DD_AGENT_PORT=8126
DD_ENV=production

# ELK Stack
ELASTICSEARCH_HOST=localhost:9200
LOGSTASH_HOST=localhost:5000
```

---

## Deployment Environments

### Local Development

```bash
# Using .env.local
cp .env.example .env.local
# Edit .env.local with local values

export $(cat .env.local | xargs)
uvicorn app:app --reload
```

### Staging

```env
# Similar to production but with staging database
ENVIRONMENT=staging
DEBUG=False
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://user:pass@staging-db.example.com/hotel_staging
CORS_ORIGINS=https://staging.yourdomain.com
```

### Production on Cloud Run (GCP)

```bash
# Set secrets via Cloud Secret Manager
gcloud secrets create database-url --data-file=- <<< "postgresql://..."
gcloud secrets create secret-key --data-file=- <<< "..."

# Reference in Cloud Run
gcloud run deploy hotel-api \
  --image gcr.io/project/hotel-api:latest \
  --set-env-vars ENVIRONMENT=production \
  --set-env-vars LOG_LEVEL=INFO \
  --secret DATABASE_URL=database-url:latest \
  --secret SECRET_KEY=secret-key:latest
```

### Production on Heroku

```bash
# Set config vars
heroku config:set ENVIRONMENT=production
heroku config:set DATABASE_URL=postgresql://...
heroku config:set SECRET_KEY=...
heroku config:set LOG_LEVEL=INFO

# Deploy
git push heroku main
```

---

## Troubleshooting

### Issue: "Database connection refused"

```bash
# Check database is running
psql -h localhost -U postgres -d hotel_dev -c "SELECT 1"

# Check DATABASE_URL format
echo $DATABASE_URL

# Verify host and port
nc -zv localhost 5432

# Check credentials
psql -h localhost -U user -d hotel_dev -W
```

### Issue: "Invalid SECRET_KEY"

```bash
# Regenerate
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env and restart
export SECRET_KEY=new-key
```

### Issue: "CORS error in browser"

```bash
# Check CORS_ORIGINS
echo $CORS_ORIGINS

# Should match your frontend URL exactly (including protocol)
# http://localhost:3000 (development)
# https://yourdomain.com (production)
```

### Issue: "API returns 401 Unauthorized"

```bash
# Check token is being sent correctly
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8001/api/rooms

# Verify SECRET_KEY hasn't changed
# Token was signed with old key but verified with new key
```

### Issue: "Database pool exhausted"

```bash
# Increase pool size in .env
SQLALCHEMY_POOL_SIZE=30
SQLALCHEMY_POOL_MAX_OVERFLOW=60

# Check for leaked connections
# Review logs for unclosed connections

# Restart application
```

---

## Configuration Checklist

### Before Development
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create .env.local file
- [ ] Start PostgreSQL container
- [ ] Run database migrations
- [ ] Create admin user

### Before Testing
- [ ] All tests use in-memory database (no configuration needed)
- [ ] Run: `pytest docs/testing/ -v`
- [ ] Check coverage: `pytest --cov=.`

### Before Production
- [ ] Generate secure SECRET_KEY
- [ ] Configure cloud database (Cloud SQL/RDS)
- [ ] Setup logging aggregation
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS for production domain
- [ ] Setup error tracking (Sentry)
- [ ] Setup monitoring (Prometheus/DataDog)
- [ ] Run security audit
- [ ] Load test (see PERFORMANCE_OPTIMIZATION.md)

### Before Deployment
- [ ] All tests pass
- [ ] Security checklist complete
- [ ] Database migrations tested
- [ ] Environment variables verified
- [ ] Backups configured
- [ ] Monitoring alerts configured
- [ ] Runbook documented

---

**Last Updated**: November 8, 2025
**Status**: Phase 9 - Complete
**Next**: Docker Setup, Deployment Guide
