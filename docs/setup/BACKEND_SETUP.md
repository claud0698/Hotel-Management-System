# Backend Setup Guide
## Kos Management Dashboard - Flask API

This guide covers setting up the Python Flask backend for development and production.

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment support

Check your Python version:
```bash
python3 --version
```

---

## Development Setup

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask 3.1.2 - Web framework
- Flask-CORS 6.0.1 - Cross-origin requests
- Flask-SQLAlchemy 3.1.1 - Database ORM
- Flask-JWT-Extended 4.7.1 - JWT authentication
- SQLAlchemy 2.0.44 - Database toolkit
- python-dotenv 1.1.1 - Environment variables
- Werkzeug 3.1.3 - Security utilities

### 3. Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py
DEBUG=True

# Security (Change these in production!)
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production-min-32-chars
JWT_EXPIRATION_DAYS=30

# Database Configuration (Development)
DATABASE_URL=sqlite:///kos.db

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
APP_ENV=development
LOG_LEVEL=INFO
```

### 4. Initialize Database

Create tables and seed with sample data:

```bash
# Create tables
python app.py

# Seed with sample data (optional)
python seed.py
```

Sample credentials after seeding:
- **Username**: admin
- **Password**: admin123

### 5. Run Development Server

```bash
python app.py
```

Server will start on `http://localhost:5000`

```
Database: sqlite:///kos.db
Environment: development
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "ok",
  "environment": "development",
  "database": "sqlite"
}
```

### API Info
```bash
curl http://localhost:5000/api
```

Response:
```json
{
  "message": "Kos Management API",
  "version": "1.0.0",
  "status": "active"
}
```

### Authentication

Register new user:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "claudio",
    "email": "claudio@example.com",
    "password": "secure123"
  }'
```

Login:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "claudio",
    "password": "secure123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "claudio",
    "email": "claudio@example.com"
  }
}
```

Use token in future requests:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/rooms
```

### Room Management

Get all rooms:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/rooms
```

Create room:
```bash
curl -X POST http://localhost:5000/api/rooms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "room_number": "401",
    "floor": 4,
    "room_type": "single",
    "monthly_rate": 1500000,
    "amenities": "WiFi, AC"
  }'
```

---

## Production Setup

### 1. Use PostgreSQL or Supabase

SQLite is only for development. For production, use:

**Option A: Supabase (Recommended)**
```bash
# Update .env
DATABASE_URL=postgresql://user:password@host:5432/kos_db

# Install PostgreSQL driver
pip install psycopg2-binary
pip freeze > requirements.txt
```

**Option B: GCP Cloud SQL**
```bash
# Update .env with Cloud SQL Proxy connection
DATABASE_URL=postgresql://user:password@/kos_db?unix_socket=/cloudsql/PROJECT:REGION:INSTANCE
GCP_PROJECT=your-project-id

# Install Cloud SQL Proxy
curl https://dl.google.com/cloudsql/cloud_sql_proxy.mac.386 -o cloud_sql_proxy
chmod +x cloud_sql_proxy

# Run proxy in background
./cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE &
```

### 2. Update Production Environment Variables

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_APP=app.py
DEBUG=False

# Security (Use strong keys!)
SECRET_KEY=generate-with-secrets.token_hex(32)
JWT_SECRET_KEY=generate-with-secrets.token_hex(32)
JWT_EXPIRATION_DAYS=30

# Database (Change from SQLite)
DATABASE_URL=postgresql://user:password@host:5432/kos_db

# CORS (Update with production domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Production
APP_ENV=production
LOG_LEVEL=WARNING
PORT=8080
```

### 3. Collect Static Files (if using Gunicorn)

```bash
# Install WSGI server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

### 4. Database Migration

```bash
# Create tables in production database
python app.py

# Optional: Seed production data
python seed.py
```

### 5. Deploy to Cloud Platform

#### Deploy to Heroku:
```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login and create app
heroku login
heroku create kos-management-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Initialize database
heroku run python seed.py
```

#### Deploy to GCP (Cloud Run):
```bash
# Create Dockerfile (provided)
docker build -t gcr.io/PROJECT/kos-api:latest .

# Push to Google Container Registry
docker push gcr.io/PROJECT/kos-api:latest

# Deploy to Cloud Run
gcloud run deploy kos-api \
  --image gcr.io/PROJECT/kos-api:latest \
  --platform managed \
  --region us-central1
```

#### Deploy to AWS (Elastic Beanstalk):
```bash
# Initialize EB
eb init -p python-3.11 kos-api

# Create environment
eb create kos-api-env

# Deploy
eb deploy
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
PORT=8000 python app.py
```

### Database Lock Error

```bash
# Delete SQLite database and recreate
rm kos.db
python app.py
python seed.py
```

### JWT Token Errors

```bash
# Verify token format
Authorization: Bearer eyJ0eXAiOiJKV1Q...

# Check SECRET_KEY and JWT_SECRET_KEY are set
echo $JWT_SECRET_KEY
```

### CORS Errors

Make sure frontend origin is in CORS_ORIGINS:
```bash
# Check CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Database Connection Error

```bash
# For SQLite: Check if kos.db exists
ls -la kos.db

# For PostgreSQL: Test connection
psql postgresql://user:password@host:5432/kos_db

# For Supabase: Verify connection string
echo $DATABASE_URL
```

---

## Development Tips

### Enable Debug Mode

```bash
# In .env
DEBUG=True
FLASK_ENV=development

# In app.py, debug mode is enabled automatically
```

### Hot Reload

Flask automatically reloads when code changes (debug mode).

To disable:
```bash
FLASK_ENV=production
```

### Database Shell

```bash
# SQLite
sqlite3 kos.db

# PostgreSQL
psql postgresql://user:password@host:5432/kos_db
```

### View Application Logs

```bash
# Tail logs
tail -f app.log

# With timestamps and levels
FLASK_ENV=development python app.py
```

### Reset Database

```bash
# Clear all data and recreate structure
python seed.py --clear

# Just delete and recreate
rm kos.db
python app.py
```

---

## Project Structure

```
backend/
├── app.py              # Main Flask application
├── models.py           # SQLAlchemy models (database schema)
├── routes.py           # API endpoints and blueprints
├── seed.py             # Sample data generator
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (git-ignored)
├── venv/               # Virtual environment
├── kos.db              # SQLite database (development)
└── server.log          # Application logs (git-ignored)
```

---

## Next Steps

1. ✅ Backend is set up and running
2. ⏭️ Next: Set up frontend (React + TypeScript)
3. ⏭️ Then: Connect frontend to backend API
4. ⏭️ Finally: Deploy to production

---

## Performance Optimization (Production)

### Enable Connection Pooling

```python
# In app.py
from sqlalchemy.pool import QueuePool

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': QueuePool,
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### Add Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/dashboard/metrics')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_metrics():
    ...
```

### Use Compression

```bash
pip install flask-compress

from flask_compress import Compress
Compress(app)
```

---

## Security Best Practices

1. **Never commit .env file** ✅ (Already in .gitignore)
2. **Use strong secret keys** (32+ characters)
3. **Enable HTTPS in production** (Use certificate)
4. **Validate all inputs** (Already done in routes)
5. **Use CORS carefully** (Only allow trusted domains)
6. **Rate limiting** (Add if needed)
7. **Regular backups** (For PostgreSQL/Supabase)

---

## Database Support Matrix

| Database | Dev | Dev Setup | Prod | Notes |
|----------|-----|-----------|------|-------|
| SQLite | ✅ | No config | ❌ | Single file, no setup |
| PostgreSQL | ✅ | Local install | ✅ | Self-hosted, reliable |
| Supabase | ✅ | Free account | ✅ | Recommended, managed |
| GCP Cloud SQL | ⚠️ | Proxy needed | ✅ | Enterprise, premium |

---

**Backend Setup Guide v1.0**
**Last Updated**: October 24, 2025

