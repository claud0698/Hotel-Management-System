# Database Configuration Options
## Kos Management Dashboard

This guide explains the database configuration options and how to switch between them.

---

## Current Configuration

### Development: SQLite
```
DATABASE_URL=sqlite:///kos.db
```
- **Use Case**: Local development, testing
- **Pros**: Zero configuration, fast, built-in
- **Cons**: Single user, not suitable for production
- **Setup**: No setup needed, automatically created

---

## Production Database Options

### Option 1: PostgreSQL (Recommended for Self-Hosted)
```
DATABASE_URL=postgresql://username:password@localhost:5432/kos_db
```

**Installation**:
```bash
# Add PostgreSQL to requirements.txt
pip install psycopg2-binary
```

**Setup**:
```sql
-- Create database
CREATE DATABASE kos_db;

-- Create user
CREATE USER kos_user WITH PASSWORD 'strong_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE kos_db TO kos_user;

-- Connect and initialize
psql -U kos_user -d kos_db -c "SELECT 1"
```

**Environment Variable**:
```
DATABASE_URL=postgresql://kos_user:strong_password@localhost:5432/kos_db
```

---

### Option 2: Supabase (Recommended - Best of Both Worlds)
**Supabase = PostgreSQL + Built-in Features**

Supabase provides:
- ✅ PostgreSQL database (reliable, scalable)
- ✅ Free tier (perfect for starting)
- ✅ Automatic backups
- ✅ Row Level Security (RLS)
- ✅ Real-time capabilities
- ✅ REST API (optional)
- ✅ Connection pooling
- ✅ Easy scaling

**Setup**:
1. Go to https://supabase.com
2. Create new project
3. Wait for database to initialize (2-3 minutes)
4. Click "Connection Pooler" in sidebar
5. Copy connection string

**Connection String Format**:
```
DATABASE_URL=postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
```

**Environment Variable** (.env):
```
DATABASE_URL=postgresql://postgres.PROJECT_REF:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
FLASK_ENV=production
```

**Why Supabase for this project**:
- PostgreSQL backend (production-ready)
- Free tier with 500MB storage
- Easy authentication integration later
- Built-in API (optional)
- Simple to scale up
- No server management

---

### Option 3: Google Cloud SQL (GCP)
```
DATABASE_URL=postgresql://username:password@/kos_db?unix_socket=/cloudsql/PROJECT_ID:REGION:INSTANCE
```

**Setup**:
1. Create GCP project
2. Enable Cloud SQL API
3. Create PostgreSQL instance
4. Create database and user
5. Configure Cloud SQL Proxy
6. Set up Cloud IAM

**Connection from App Engine**:
```
DATABASE_URL=postgresql://kos_user:PASSWORD@/kos_db?unix_socket=/cloudsql/PROJECT_ID:us-central1:kos-db
```

**Why GCP**:
- Managed service (no maintenance)
- Automatic backups and replication
- Integrated with Google Cloud ecosystem
- High availability
- Good for enterprise
- Higher cost ($13+/month minimum)

---

## Recommended Setup Path

### Stage 1: Development (Current)
```
SQLite (sqlite:///kos.db)
- No setup
- Fast development
- Easy testing
```

### Stage 2: Early Production (Recommended)
```
Supabase PostgreSQL
- Free tier ($0/month)
- Production-ready database
- Easy to scale
- Built-in features
```

### Stage 3: Scaling
```
Upgrade to Paid Supabase or GCP based on needs
- More storage
- Better support
- Advanced features
```

---

## How to Switch Database

### 1. Update requirements.txt

Add PostgreSQL driver (choose one):
```bash
# For PostgreSQL (both Supabase and self-hosted)
pip install psycopg2-binary

# Or use psycopg (newer, recommended)
pip install psycopg
```

### 2. Update .env file

```bash
# Change from SQLite
DATABASE_URL=sqlite:///kos.db

# To PostgreSQL / Supabase
DATABASE_URL=postgresql://username:password@host:5432/database_name
```

### 3. Update requirements.txt in repository

```txt
Flask==3.1.2
Flask-CORS==6.0.1
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.7.1
SQLAlchemy==2.0.44
psycopg2-binary==2.9.9
python-dotenv==1.1.1
Werkzeug==3.1.3
```

### 4. Run migrations

SQLAlchemy ORM will handle migrations automatically:
```bash
python app.py  # Creates tables in new database
```

### 5. Seed data (optional)

```bash
python seed.py  # Populate with sample data
```

---

## Database Comparison Table

| Feature | SQLite | PostgreSQL | Supabase | GCP SQL |
|---------|--------|-----------|----------|---------|
| **Setup Time** | 0 min | 10 min | 5 min | 20 min |
| **Cost** | Free | Free (self-hosted) | Free/paid | Paid ($13+) |
| **Production Ready** | ❌ | ✅ | ✅ | ✅ |
| **Scalability** | ❌ | ✅ | ✅ | ✅ |
| **Backups** | Manual | Manual | Automatic | Automatic |
| **Monitoring** | None | None | Dashboard | Dashboard |
| **Multi-user** | ❌ | ✅ | ✅ | ✅ |
| **Maintenance** | Self | Self | Managed | Managed |
| **Best For** | Development | Self-hosted | Startups | Enterprise |

---

## Connection Pooling

For production, use connection pooling to handle multiple concurrent connections:

**Supabase** (Built-in):
- Pooler automatically enabled
- Use `pooler.supabase.com` endpoint
- Connection limit: 5-100 depending on tier

**Self-hosted PostgreSQL**:
```bash
pip install psycopg-pool
```

**GCP Cloud SQL Proxy**:
```bash
# Download and run proxy
cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE &
```

---

## Environment Variables by Database

### SQLite (Development)
```bash
DATABASE_URL=sqlite:///kos.db
FLASK_ENV=development
DEBUG=True
```

### PostgreSQL / Supabase (Production)
```bash
DATABASE_URL=postgresql://user:password@host:5432/db
FLASK_ENV=production
DEBUG=False
```

### GCP Cloud SQL
```bash
DATABASE_URL=postgresql://user:password@/db?unix_socket=/cloudsql/PROJECT:REGION:INSTANCE
FLASK_ENV=production
DEBUG=False
GCP_PROJECT=your-project-id
```

---

## Migration Steps: SQLite → Supabase

If you want to migrate existing data:

### 1. Export SQLite data
```bash
# Create backup
sqlite3 kos.db ".dump" > backup.sql
```

### 2. Create Supabase database
- Sign up at supabase.com
- Create project
- Get connection string

### 3. Update app and run migrations
```bash
# Update .env with Supabase connection
DATABASE_URL=postgresql://...

# Create tables in Supabase
python app.py  # Runs db.create_all()
```

### 4. (Optional) Migrate data
```bash
# Export from SQLite as JSON
python -c "
from app import app, db
from models import *
import json

# Export logic here
"

# Then import to Supabase
```

For most cases, starting fresh is easier than migrating.

---

## Troubleshooting

### "can't connect to PostgreSQL"
- Check connection string format
- Verify username/password
- Check if firewall allows connection
- For Supabase: ensure you're using Connection Pooler endpoint

### "relation does not exist"
- Run `python app.py` to create tables
- Check that database is selected correctly

### "too many connections"
- Enable connection pooling
- Reduce max connections setting
- For Supabase: upgrade plan

---

## Recommendation for This Project

**For Development**: Use SQLite (current setup) ✅

**For Production**: Use Supabase ✅✅
- Easiest to set up (5 minutes)
- Free tier ($0/month)
- Production-ready reliability
- Same code (just change DATABASE_URL)
- Can upgrade anytime without code changes

**Setup Supabase in 5 minutes**:
1. Go to https://supabase.com
2. Click "Start your project"
3. Create new project
4. Wait for initialization
5. Get connection string from "Connection Pooler"
6. Update .env with connection string
7. Run `python app.py`

That's it! Your app now uses PostgreSQL on Supabase.

---

**Document Version**: 1.0
**Last Updated**: October 24, 2025

