# Database Verification & Diagnostic Scripts

Verify database setup, test connections, and diagnose issues for Hotel Management System.

## 📋 Overview

This folder contains scripts for verifying the database is properly configured and initialized.

### Scripts in This Folder

| Script | Purpose | Time | When to Use |
|--------|---------|------|------------|
| `check_setup.py` | ⭐ **Full verification** (recommended) | ~10s | After setup |

---

## 🚀 Quick Start

### Run Full Verification

```bash
python check_setup.py
```

**What it checks:**
- ✓ Environment variables present
- ✓ Migration file exists
- ✓ Models import successfully
- ✓ Database connection working
- ✓ All 12 tables created
- ✓ Initial data seeded
- ✓ 42 indexes created

**Output Example:**
```
✓ Database connection verified
✓ 12 tables found
✓ 42 indexes verified
✓ 4 room types found
✓ 5 booking channels found
✓ 8 settings found
```

**Time:** ~10 seconds

---

## 📝 Script Details

### check_setup.py

**Complete database verification and diagnostics**

```bash
python check_setup.py
```

**Features:**
- ✓ Environment validation
- ✓ Migration file verification
- ✓ Model import testing
- ✓ Database connectivity check
- ✓ Table existence verification
- ✓ Record count checking
- ✓ Index verification
- ✓ Detailed diagnostics

---

## ✅ Verification Checklist

### Step 1: Environment Variables
Checks for:
- `DATABASE_URL` ✓
- `DB_HOST` ✓
- `DB_PORT` ✓
- `DB_NAME` ✓
- `DB_USER` ✓
- `DB_PASSWORD` ✓

**Example output:**
```
✓ Database URL configured: postgresql://postgres...@aws-...
✓ All required environment variables present
```

---

### Step 2: Migration File

Checks:
- Migration file exists at: `backend/migrations/001_v1_0_initial_schema.sql`
- File size > 0 bytes
- Contains table definitions

**Example output:**
```
✓ Migration file found
✓ File size: 18,421 bytes
✓ Tables to create: 12
```

---

### Step 3: Models Import

Checks:
- All 12 models can be imported
- No syntax errors
- Relationships properly defined

**Models verified:**
- User
- RoomType
- Room
- RoomImage
- RoomTypeImage
- Guest
- Reservation
- Payment
- PaymentAttachment
- Setting
- Discount
- BookingChannel

**Example output:**
```
✓ All 12 models imported successfully
  - User
  - RoomType
  - Room
  ... (etc)
```

---

### Step 4: Database Connection

Checks:
- Can connect to database
- Connection pool works
- Query execution works

**Example output:**
```
✓ Database connection successful
✓ Connection pool ready
✓ Query execution verified
```

---

### Step 5: Table Verification

Checks:
- All 12 tables exist
- Proper structure
- All columns present

**Example output:**
```
✓ All 12 tables exist
  ✓ users
  ✓ room_types
  ✓ rooms
  ... (etc)
```

---

### Step 6: Data Verification

Checks:
- Initial data seeded
- Record counts

**Example output:**
```
✓ 4 room types found
  - Standard (STD): IDR 500,000
  - Deluxe (DLX): IDR 750,000
  - Suite (SUI): IDR 1,200,000
  - Penthouse (PNT): IDR 2,000,000

✓ 5 booking channels found
  - Direct Booking
  - Tiket.com
  ... (etc)

✓ 8 settings found
  - hotel_name
  ... (etc)
```

---

### Step 7: Index Verification

Checks:
- All indexes created
- Proper index count (42 expected)

**Example output:**
```
✓ 42 indexes found (expected: 42+)
```

---

## 🔍 Detailed Output

### When Everything Works

```
======================================================================
✓ DATABASE VERIFICATION COMPLETE
======================================================================

Environment Check:    ✓ PASSED
Migration File:       ✓ PASSED
Models Import:        ✓ PASSED
Database Connection:  ✓ PASSED
Tables:               ✓ PASSED (12/12)
Data:                 ✓ PASSED (17 records)
Indexes:              ✓ PASSED (42)

All checks passed! Database is properly configured.
```

---

### When Issues Found

```
======================================================================
⚠ DATABASE VERIFICATION COMPLETED WITH WARNINGS
======================================================================

Environment Check:    ✓ PASSED
Migration File:       ✗ FAILED (missing DATABASE_URL)
  → Solution: Check .env file for DATABASE_URL variable

Models Import:        ✓ PASSED
Database Connection:  ✗ FAILED (Connection refused)
  → Solution: Verify Supabase is running and IP is whitelisted
```

---

## 🆘 Troubleshooting

### "DATABASE_URL not found"

**Problem:** Missing environment variable

**Solution:**
1. Check .env file exists: `cat backend/.env`
2. Verify DATABASE_URL is set
3. Restart terminal if just added

---

### "Connection refused"

**Problem:** Cannot connect to Supabase

**Solution:**
1. Verify Supabase is running
2. Check DATABASE_URL is correct
3. Ensure your IP is whitelisted:
   - Supabase Dashboard → Settings → Network
4. Test connection manually:
   ```bash
   psql "$(cat backend/.env | grep DATABASE_URL | cut -d= -f2)"
   ```

---

### "Table does not exist"

**Problem:** Tables haven't been created yet

**Solution:**
1. Run initialization:
   ```bash
   cd ../init
   python setup_complete.py
   ```

---

### "Module not found"

**Problem:** Missing dependencies

**Solution:**
```bash
pip install -r backend/requirements.txt
```

---

## ⚙️ Prerequisites

### Python 3.12

```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate py3.12
```

### Environment File (.env)

Must exist at: `backend/.env`

```env
DATABASE_URL=postgresql://...
DB_HOST=...
DB_USER=...
DB_PASSWORD=...
```

### Database Must Be Created First

Run initialization:
```bash
cd ../init
python setup_complete.py
```

---

## 📝 Usage Workflow

### After Initial Setup

```bash
# 1. Run complete setup
cd ../init
python setup_complete.py

# 2. Verify everything worked
cd ../verify
python check_setup.py

# 3. Check output
✓ All checks passed! Database is properly configured.
```

### Before Starting Backend

```bash
# Always verify before starting backend server
python check_setup.py

# If all checks pass:
cd ../../
uvicorn app:app --reload
```

### During Development

```bash
# Run periodically to ensure database health
python check_setup.py

# Helps identify:
- Connection issues
- Missing data
- Schema problems
- Index problems
```

---

## 📊 Expected Values

### Database Tables: 12 Total

```
users                    - Authentication
room_types               - Room categories
rooms                    - Individual rooms
room_images              - Room photos
room_type_images         - Room showcases
guests                   - Guest profiles
reservations             - Bookings
payments                 - Payment tracking
payment_attachments      - Payment proofs
settings                 - Admin config
discounts                - Promotions
booking_channels         - Booking sources
```

### Database Indexes: 42 Total

Distributed across tables for:
- ID lookups
- Foreign key relationships
- Date range queries
- Status filtering
- Active record filtering

### Initial Data: 17 Total Records

```
Room Types:        4
Booking Channels:  5
Settings:          8
━━━━━━━━━━━━━━━━━━━━
Total:            17
```

---

## 🔄 Regular Verification

### Daily Check

```bash
# Run during development
python check_setup.py
```

### Before Deployment

```bash
# Verify before pushing to production
python check_setup.py

# Expected output
✓ All checks passed! Database is properly configured.
```

### After Data Changes

```bash
# Verify data integrity
python check_setup.py

# Look for unusual record counts
# Check for missing expected data
```

---

## 📋 Verification Report

Script generates report showing:

**Configuration:**
- Environment variables
- Connection string (masked)
- Database version

**Structure:**
- 12 tables present
- Proper indexes (42)
- Foreign key relationships

**Data:**
- Room types (4)
- Booking channels (5)
- Settings (8)
- Total records

**Health:**
- Connection status
- Query performance
- Error summary

---

## 🎯 Integration Tips

### In CI/CD Pipeline

```yaml
# .github/workflows/test.yml
- name: Verify Database Setup
  run: python backend/scripts/verify/check_setup.py
```

### Before Running Tests

```bash
# Ensure database is ready before running tests
python check_setup.py && pytest
```

### In Docker

```dockerfile
# Run verification before starting app
CMD python scripts/verify/check_setup.py && \
    uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## 📚 Next Steps

After successful verification:

1. **Create admin user:**
   ```bash
   python ../../init_admin.py
   ```

2. **Start backend:**
   ```bash
   cd ../../
   uvicorn app:app --reload
   ```

3. **Access API:**
   - http://localhost:8000/api/docs

4. **Begin development:**
   - Implement Phase 1 endpoints
   - Start building features

---

## 🎯 Features

✅ **Comprehensive** - Checks all aspects of setup
✅ **Detailed** - Provides specific error messages
✅ **Fast** - Completes in ~10 seconds
✅ **Helpful** - Includes troubleshooting tips
✅ **Repeatable** - Safe to run anytime

---

**Questions?** Check the main scripts README: `../README.md`
