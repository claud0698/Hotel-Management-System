# Database Initialization Scripts

Initialize and create all database tables for Hotel Management System v1.0.

## 📋 Overview

This folder contains scripts that handle database table creation and initialization.

### Scripts in This Folder

| Script | Purpose | Time | Status |
|--------|---------|------|--------|
| `setup_complete.py` | ⭐ **Complete setup** (all-in-one) | ~30s | RECOMMENDED |
| `create_tables.py` | Create all 12 tables | ~5s | Single step |
| `from_sql.py` | SQL-based initialization | ~10s | Alternative |

---

## 🚀 Quick Start

### Option 1: Complete Setup (Recommended)

Run this for full database initialization:

```bash
python setup_complete.py
```

**What it does (all at once):**
1. ✓ Checks environment configuration
2. ✓ Imports all SQLAlchemy models
3. ✓ Tests database connection
4. ✓ Creates all 12 tables
5. ✓ Seeds initial data (room types, channels, settings)
6. ✓ Runs 5 comprehensive tests
7. ✓ Provides detailed summary

**Output:**
```
✓ Tables created: 12/12
✓ Indexes created: 42
✓ Records seeded: 17
✓ Tests passed: 5/5
```

**Time:** ~30 seconds

---

### Option 2: Step-by-Step

Create only the tables (without seeding):

```bash
python create_tables.py
```

**What it does:**
- ✓ Creates database engine
- ✓ Tests connection
- ✓ Creates all 12 tables with relationships
- ✓ Verifies 42 indexes
- ✓ Reports creation status

**Output:**
```
✓ Tables created/verified: 12
✓ Indexes created: 42
```

**Time:** ~5 seconds

Then seed data separately using scripts in `../seed/`

---

## 📝 Script Details

### setup_complete.py

**Full automation - all database setup in one script**

```bash
python setup_complete.py
```

**Features:**
- ✓ Single command for complete setup
- ✓ Environment validation
- ✓ Connection testing
- ✓ Table creation
- ✓ Data seeding
- ✓ Comprehensive testing
- ✓ Detailed reporting

**Best for:**
- First-time setup
- Clean database initialization
- Automated deployment
- CI/CD pipelines

**Class-based architecture:**
- `DatabaseSetup` class orchestrates all operations
- Modular methods for each step
- Comprehensive error handling
- Progress tracking and statistics

---

### create_tables.py

**Create database tables using SQLAlchemy ORM**

```bash
python create_tables.py
```

**Features:**
- ✓ SQLAlchemy ORM models
- ✓ Proper relationships and foreign keys
- ✓ Automatic index creation (42 total)
- ✓ Audit trails (created_at, updated_at)
- ✓ Connection pooling
- ✓ Transaction management

**Tables created (12 total):**
- users, room_types, rooms, room_images, room_type_images
- guests, reservations, payments, payment_attachments
- settings, discounts, booking_channels

**Best for:**
- Creating database structure only
- Manual step-by-step setup
- Troubleshooting table creation

---

### from_sql.py

**SQL-based database initialization**

```bash
python from_sql.py
```

**Features:**
- ✓ Direct SQL execution (no ORM)
- ✓ Reads migration file
- ✓ Statement-by-statement execution
- ✓ Detailed migration tracking
- ✓ Error reporting per statement

**Uses:**
- `backend/migrations/001_v1_0_initial_schema.sql`

**Best for:**
- Direct SQL control
- Debugging table creation issues
- Advanced users who prefer SQL
- Detailed execution tracking

---

## 📊 What Gets Created

### 12 Database Tables

```
users
  - User authentication & management
  - Password hashing with bcrypt

room_types
  - Room categories
  - Default rates (IDR 500k - 2M)

rooms
  - Individual rooms
  - Custom rate overrides

room_images
  - Room photo galleries
  - Display ordering

room_type_images
  - Room type showcase images

guests
  - Guest profiles
  - VIP tracking

reservations
  - Booking system
  - Confirmation numbers

payments
  - Payment tracking
  - 6 payment methods

payment_attachments
  - Payment proofs
  - Verification workflow

settings
  - Admin configuration

discounts
  - Promotional pricing (v1.1+ ready)

booking_channels
  - Booking source tracking
```

### Database Features

- ✓ 42 optimized indexes for fast queries
- ✓ Foreign key relationships with cascading
- ✓ CheckConstraints for data validation
- ✓ Audit trails (created_at, updated_at)
- ✓ Connection pooling (20 base + 10 overflow)
- ✓ Transaction management

---

## ⚙️ Prerequisites

### Python 3.12

```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate py3.12
```

### Dependencies

```bash
pip install -r backend/requirements.txt
```

### Environment File (.env)

```env
DATABASE_URL=postgresql://...
DB_HOST=aws-1-ap-southeast-1.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=...
```

---

## 📝 Usage Workflow

### First-Time Setup

```bash
# 1. Navigate to init folder
cd backend/scripts/init

# 2. Run complete setup
python setup_complete.py

# 3. Check output for success message
✓ Database setup completed successfully!
```

### Verification

Check tables created:
```bash
python -c "from backend.models import Base; print(list(Base.metadata.tables.keys()))"
```

Expected output:
```
['users', 'room_types', 'rooms', 'room_images', 'room_type_images',
 'guests', 'reservations', 'payments', 'payment_attachments',
 'settings', 'discounts', 'booking_channels']
```

---

## 🆘 Troubleshooting

### "Connection refused"
- Verify Supabase is running
- Check DATABASE_URL in .env
- Ensure IP is whitelisted in Supabase

### "Module not found"
```bash
pip install -r backend/requirements.txt
```

### "Table already exists"
Normal with `IF NOT EXISTS` - safe to re-run

### "Permission denied"
- Check .env file permissions
- Verify database user permissions
- Ensure DB_USER has CREATE TABLE privilege

---

## 🔍 How They Work

### setup_complete.py Flow

```
1. Check Environment
   ↓
2. Import Models
   ↓
3. Test Connection
   ↓
4. Create Tables
   ↓
5. Seed Initial Data
   ↓
6. Run Tests
   ↓
7. Print Summary
```

### create_tables.py Flow

```
1. Check Environment
   ↓
2. Import Models
   ↓
3. Create Engine
   ↓
4. Test Connection
   ↓
5. Create Tables
   ↓
6. Verify Indexes
   ↓
7. Print Summary
```

---

## 📚 Next Steps

After initialization:

1. **Seed initial data:**
   ```bash
   cd ../seed
   python initial_data.py
   ```

2. **Verify setup:**
   ```bash
   cd ../verify
   python check_setup.py
   ```

3. **Create admin user:**
   ```bash
   python ../../../init_admin.py
   ```

4. **Start backend:**
   ```bash
   cd ../../
   uvicorn app:app --reload
   ```

---

## 🎯 Features

✅ **Idempotent** - Safe to run multiple times
✅ **Error Handling** - Comprehensive error messages
✅ **Progress Reporting** - Step-by-step output
✅ **Transaction Safe** - Proper rollback on errors
✅ **Connection Pooling** - Optimized database access

---

**Questions?** Check the main scripts README: `../README.md`
