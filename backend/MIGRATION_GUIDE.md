# PostgreSQL Migration Guide for Kos Database

## Overview
Your application is transitioning from SQLite (`kos.db`) to PostgreSQL (Supabase). This guide walks you through the complete migration process.

## Current Status
- **Source Database**: SQLite (`kos.db`)
- **Target Database**: PostgreSQL (Supabase - ap-northeast-1 Region)
- **Database URL**: Already configured in `.env`
- **Migration Script**: `migrate_to_postgres.py` - Ready to run

## Pre-Migration Checklist

### 1. Verify Environment Configuration
Your `.env` file already has PostgreSQL configured:
```
DATABASE_URL=postgresql://postgres.qcyftbttgyreoouazjfx:kMgxNYUzKiR4F8EC@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres
```

✅ **Status**: Configured and ready

### 2. Verify Required Dependencies
Your `requirements.txt` includes all necessary packages:
- `SQLAlchemy==2.0.44` - ORM for database operations
- `psycopg2-binary==2.9.9` - PostgreSQL adapter for Python
- `python-dotenv==1.1.1` - Environment variable management

✅ **Status**: All dependencies present

## Step-by-Step Migration Instructions

### Step 1: Backup Your SQLite Database
Before running any migration, backup your current data:

```bash
# Copy the SQLite database to a backup location
cp kos.db kos.db.backup

# Verify the backup was created
ls -lh kos.db*
```

### Step 2: Verify PostgreSQL Connection
Test the connection to PostgreSQL before migration:

```bash
# Make sure you're in the backend directory
cd /Users/claudio/Documents/Personal/kos-database/backend

# Test the connection (optional - migration script does this automatically)
python3 -c "from sqlalchemy import create_engine, text; import os; from dotenv import load_dotenv; load_dotenv(); engine = create_engine(os.getenv('DATABASE_URL')); conn = engine.connect(); print('✅ PostgreSQL connection successful'); conn.close()"
```

### Step 3: Run the Migration Script
The migration script will:
1. ✅ Create all tables in PostgreSQL
2. ✅ Clear existing data (if any) in PostgreSQL
3. ✅ Migrate data from all tables:
   - Users
   - Rooms
   - Tenants
   - Payments
   - Expenses
   - Room History
4. ✅ Update PostgreSQL sequences for auto-increment IDs

**Run the migration:**

```bash
# Ensure you're in the backend directory
cd /Users/claudio/Documents/Personal/kos-database/backend

# Run the migration script
python3 migrate_to_postgres.py
```

**You'll see output like:**
```
🔄 Starting migration from SQLite to PostgreSQL...
📍 Source: sqlite:///./kos.db
📍 Target: postgresql://***@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres
✅ Successfully connected to PostgreSQL database

📋 Creating tables in PostgreSQL...
✅ Tables created successfully

🗑️  Clearing existing data in PostgreSQL...
✅ Existing data cleared

👤 Migrating users...
✅ Migrated X users

🏠 Migrating rooms...
✅ Migrated X rooms

👥 Migrating tenants...
✅ Migrated X tenants

💰 Migrating payments...
✅ Migrated X payments

💸 Migrating expenses...
✅ Migrated X expenses

📜 Migrating room history...
✅ Migrated X room history records

🔢 Updating PostgreSQL sequences...
✅ Updated users_id_seq to X
✅ Updated rooms_id_seq to X
✅ Updated tenants_id_seq to X
✅ Updated payments_id_seq to X
✅ Updated expenses_id_seq to X
✅ Updated room_history_id_seq to X

============================================================
✅ Migration completed successfully!
============================================================
```

### Step 4: Verify Data Integrity
After migration, verify that all data was transferred correctly:

```bash
# Option A: Use psql (if PostgreSQL client is installed)
psql postgresql://postgres.qcyftbttgyreoouazjfx:kMgxNYUzKiR4F8EC@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres

# In psql shell:
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM rooms;
SELECT COUNT(*) FROM tenants;
SELECT COUNT(*) FROM payments;
SELECT COUNT(*) FROM expenses;
SELECT COUNT(*) FROM room_history;

# Exit psql
\q
```

### Step 5: Test Your Application
Start the FastAPI application and test it with PostgreSQL:

```bash
# Ensure Python virtual environment is activated (if using one)
# Then run the application:
python3 app.py

# Or using uvicorn directly:
uvicorn app:app --reload --port 8001
```

**Expected output:**
```
Database: postgresql://postgres.qcyftbttgyreoouazjfx:kMgxNYUzKiR4F8EC@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres
Environment: development
```

### Step 6: Test API Endpoints
Once the application is running, test key endpoints:

```bash
# Health check
curl http://localhost:8001/health

# API root
curl http://localhost:8001/api

# Login (if test user exists)
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'

# Get rooms
curl http://localhost:8001/api/rooms
```

## Post-Migration Steps

### 1. Update Application Code (if needed)
The application is already configured to work with both SQLite and PostgreSQL. The `DATABASE_URL` environment variable determines which database is used.

**No code changes are needed** - your `app.py` already handles both:
```python
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./kos.db')
# ... connection logic automatically adapts based on the URL
```

### 2. Disable SQLite (Optional)
If you want to prevent accidental use of SQLite, you can:
- Comment out the SQLite configuration in `.env` (already done ✅)
- Delete the `kos.db` file (after verifying all data is in PostgreSQL)

### 3. Configure Production Settings
When deploying to production:

```env
# Update these settings in your production .env file:
FLASK_ENV=production
DEBUG=False
CORS_ORIGINS=https://your-production-domain.com
```

### 4. Set Up Monitoring
For production PostgreSQL:
- Monitor database performance using Supabase dashboard
- Set up automated backups (Supabase provides this)
- Monitor connection pool usage
- Set up alerts for unusual activity

## Troubleshooting

### Connection Issues
**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
1. Verify the `DATABASE_URL` in `.env` is correct
2. Check your internet connection
3. Verify Supabase is running and accessible
4. Check firewall/network restrictions

### Data Migration Issues
**Error**: `Foreign key constraint failed`

**Solution**:
1. Ensure all referenced tables are created first (the script handles this)
2. Check for orphaned records in SQLite before migration
3. Run the migration script again

### Authentication Issues
**Error**: `password authentication failed for user "postgres"`

**Solution**:
1. Verify the password in `DATABASE_URL` is correct
2. Check if the Supabase project credentials have changed
3. Regenerate the database connection string from Supabase dashboard

## Data Migration Details

### Tables Migrated
1. **users** - Admin users for authentication
2. **rooms** - Rental room information
3. **tenants** - Tenant details and contact information
4. **payments** - Payment records and status
5. **expenses** - Expense tracking and categorization
6. **room_history** - Historical record of tenant-room occupancy

### Data Integrity Checks
The migration script:
- ✅ Preserves all IDs from SQLite
- ✅ Maintains referential integrity with foreign keys
- ✅ Converts datetime values correctly
- ✅ Resets PostgreSQL sequences to prevent ID conflicts
- ✅ Preserves all text and numeric data accurately

## Performance Comparison

### SQLite vs PostgreSQL
| Feature | SQLite | PostgreSQL |
|---------|--------|-----------|
| Concurrent Users | ⚠️ Limited | ✅ Excellent |
| Data Size | ⚠️ Limited | ✅ Unlimited |
| Backups | ⚠️ Manual | ✅ Automated (Supabase) |
| Scalability | ⚠️ Poor | ✅ Excellent |
| Security | ⚠️ File-based | ✅ Enterprise-grade |

## Rollback (If Needed)

If you need to revert to SQLite:

1. **Stop the application**
2. **Restore the SQLite backup**:
   ```bash
   # Copy backup back to original location
   cp kos.db.backup kos.db
   ```
3. **Update `.env` to use SQLite**:
   ```env
   DATABASE_URL=sqlite:///./kos.db
   ```
4. **Restart the application**

## Success Indicators

After completing the migration, you should see:

✅ Migration script completes without errors
✅ All data counts match between SQLite and PostgreSQL
✅ Application starts successfully with PostgreSQL
✅ API endpoints respond correctly
✅ Health check endpoint works (`/health`)
✅ No foreign key constraint errors
✅ No authentication errors when testing login

## Additional Resources

- [Supabase PostgreSQL Documentation](https://supabase.com/docs/guides/database)
- [SQLAlchemy PostgreSQL Documentation](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [FastAPI Database Documentation](https://fastapi.tiangolo.com/advanced/sql-databases/)

## Support

If you encounter any issues:
1. Check the error message in the migration script output
2. Review the troubleshooting section above
3. Verify your `.env` configuration
4. Check Supabase project status and credentials

---

**Last Updated**: November 6, 2024
**Migration Script**: `migrate_to_postgres.py`
**FastAPI Version**: 0.104.1
**PostgreSQL Version**: Supabase (Latest)
