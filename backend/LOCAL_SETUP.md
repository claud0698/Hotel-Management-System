# Local Development Setup Guide

## Overview
This guide explains how to run the Hotel Management System with a local PostgreSQL database instead of Supabase.

## Prerequisites
- Docker installed and running
- Python 3.12+ with required packages
- Git

---

## Quick Start (One Command)

```bash
# Start PostgreSQL container
docker run --name hotel-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=hotel_db \
  -p 5432:5432 \
  -d postgres:15-alpine
```

Then run the backend:
```bash
# Copy local env
cp .env.local .env

# Run migrations
python3 << 'EOF'
import psycopg2
from pathlib import Path

conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/hotel_db")
cursor = conn.cursor()

# Run migration files
for migration_file in sorted(Path('migrations').glob('*.sql')):
    with open(migration_file) as f:
        sql = f.read()
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        if stmt and not stmt.startswith('--'):
            cursor.execute(stmt)

conn.commit()
cursor.close()
conn.close()
print("✓ Migrations completed!")
EOF

# Start the backend
python app.py
```

Backend will be running at: `http://localhost:8001`

---

## Detailed Setup Steps

### Step 1: Start PostgreSQL Docker Container

```bash
# Stop any existing container
docker stop hotel-postgres 2>/dev/null || true
docker rm hotel-postgres 2>/dev/null || true

# Start new container
docker run --name hotel-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=hotel_db \
  -p 5432:5432 \
  -d postgres:15-alpine

# Verify it's running
docker ps | grep hotel-postgres
```

**Expected output:**
```
efb98e7ad495   postgres:15-alpine   ...   Up 8 seconds   0.0.0.0:5432->5432/tcp
```

### Step 2: Update Environment

```bash
# Use local environment configuration
cp .env.local .env
```

**Key differences from Supabase:**
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hotel_db`
- `ENV=development`
- `DEBUG=True`

### Step 3: Run Database Migrations

```bash
python3 run_migrations.py
```

This will:
- Load initial schema from `migrations/001_v1_0_initial_schema.sql`
- Add missing columns from `migrations/002_add_missing_columns.sql`

### Step 4: Start the Backend

```bash
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Application startup complete.
Database: postgresql://postgres:postgres@localhost:5432/hotel_db
Environment: development
```

---

## Docker Commands Reference

### Check Container Status
```bash
docker ps
docker logs hotel-postgres
```

### Connect to PostgreSQL
```bash
docker exec -it hotel-postgres psql -U postgres -d hotel_db
```

### Stop Container
```bash
docker stop hotel-postgres
```

### Remove Container (clears data)
```bash
docker rm hotel-postgres
```

### View Container Storage
```bash
# PostgreSQL data is stored in Docker's volume system
docker volume ls | grep postgres
```

---

## Switching Between Local & Supabase

### Use Local Database
```bash
cp .env.local .env
python app.py
```

### Use Supabase (Production)
```bash
# Restore original .env with Supabase credentials
# Then restart the app
python app.py
```

---

## Troubleshooting

### Issue: "Address already in use" (Port 5432)
```bash
# Kill process using port 5432
lsof -ti:5432 | xargs kill -9

# Or use different port
docker run -p 5433:5432 ...  # Maps 5433 on host to 5432 in container
# Update .env: DB_PORT=5433
```

### Issue: Database Connection Refused
```bash
# Check if container is running
docker ps | grep hotel-postgres

# If not running, start it
docker start hotel-postgres

# Wait 5 seconds for startup
sleep 5
```

### Issue: Migrations Failed
```bash
# Check PostgreSQL logs
docker logs hotel-postgres

# Verify database exists
docker exec -it hotel-postgres psql -U postgres -l
```

### Issue: SQLAlchemy Errors
```bash
# Ensure all missing columns are added
# Delete existing docker volume and restart
docker stop hotel-postgres
docker rm hotel-postgres
# Then re-run the container and migrations
```

---

## Performance Notes

- **Local Docker**: ~100ms query latency (excellent for development)
- **Supabase**: ~150-200ms latency (includes network round-trip)
- **SQLite**: ~5ms latency (but less feature-complete)

For development, local PostgreSQL Docker is ideal because:
✓ Identical to production (same database engine)
✓ Fast
✓ Easy to reset/recreate
✓ No internet dependency
✓ Full SQL compatibility

---

## Important Files

- `.env.local` - Local development configuration
- `migrations/001_v1_0_initial_schema.sql` - Initial schema
- `migrations/002_add_missing_columns.sql` - Missing column additions
- `run_migrations.py` - Migration runner script

---

## Next Steps

1. Start PostgreSQL: `docker run ...`
2. Set environment: `cp .env.local .env`
3. Run migrations: `python3 run_migrations.py`
4. Start backend: `python app.py`
5. Test API: `curl http://localhost:8001/api/health`

Happy coding! 🚀
