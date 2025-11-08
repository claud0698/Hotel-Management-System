# Backend Setup Scripts

Organized database initialization, seeding, and verification scripts for the Hotel Management System v1.0.

## 📁 Folder Structure

```
scripts/
├── README.md (this file)
├── init/              # Database initialization scripts
│   ├── setup_complete.py      ⭐ MAIN: Complete setup (all-in-one)
│   ├── create_tables.py        - Create all 12 tables
│   └── from_sql.py             - SQL-based initialization
├── seed/              # Database seeding scripts
│   ├── initial_data.py         - Seed room types, channels, settings
│   ├── seed.py                 - Original seeding script
│   ├── seed_admin_user.py      - Admin user creation
│   ├── seed_real_data.py       - Realistic test data
│   ├── seed_rooms_simple.py    - Simple room data
│   └── seed_july_2025.py       - Historical July 2025 data
└── verify/            # Verification & diagnostic scripts
    └── check_setup.py          - Verify database setup

```

---

## 🚀 Quick Start

### Option 1: Complete Setup (Recommended)
All database initialization in one command:

```bash
python backend/scripts/init/setup_complete.py
```

This will:
- ✓ Check environment configuration
- ✓ Create all 12 tables
- ✓ Seed initial data (room types, channels, settings)
- ✓ Run verification tests
- ✓ Provide detailed summary

### Option 2: Step-by-Step

```bash
# 1. Create all database tables
python backend/scripts/init/create_tables.py

# 2. Seed initial data
python backend/scripts/seed/initial_data.py

# 3. Verify everything is set up correctly
python backend/scripts/verify/check_setup.py
```

---

## 📋 Script Details

### `init/` - Database Initialization

#### `setup_complete.py` ⭐ RECOMMENDED
**Complete database setup in one script**

```bash
python backend/scripts/init/setup_complete.py
```

**What it does:**
1. Checks environment configuration
2. Imports all SQLAlchemy models
3. Tests database connection
4. Creates all 12 tables
5. Seeds initial data (4 room types, 5 channels, 8 settings)
6. Runs 5 comprehensive tests
7. Provides detailed summary

**Output:**
```
✓ Tables created: 12/12
✓ Indexes created: 42
✓ Records seeded: 17
✓ Tests passed: 5/5
```

---

#### `create_tables.py`
**Create all 12 PostgreSQL tables using SQLAlchemy ORM**

```bash
python backend/scripts/init/create_tables.py
```

**Tables created:**
- users, room_types, rooms, room_images, room_type_images
- guests, reservations, payments, payment_attachments
- settings, discounts, booking_channels

**Features:**
- ✓ Proper relationships and foreign keys
- ✓ 42 optimized indexes
- ✓ Full audit trail (created_at, updated_at)

---

#### `from_sql.py`
**Alternative SQL-based database initialization**

```bash
python backend/scripts/init/from_sql.py
```

**Use when:**
- Prefer direct SQL execution
- Need detailed SQL tracking
- Direct database control required

---

### `seed/` - Database Seeding

#### `initial_data.py`
**Seed essential data for Hotel Management System**

```bash
python backend/scripts/seed/initial_data.py
```

**What it seeds:**
- ✓ 4 room types (Standard, Deluxe, Suite, Penthouse)
- ✓ 5 booking channels (Direct, Tiket, Traveloka, Booking, Other)
- ✓ 8 default settings (hotel info, times, localization)

**Features:**
- Duplicate checks (safe to re-run)
- Full audit trail
- Transaction management

---

#### Other Seeding Scripts

**`seed.py`** - Original seeding script
```bash
python backend/scripts/seed/seed.py
```

**`seed_admin_user.py`** - Create admin user
```bash
python backend/scripts/seed/seed_admin_user.py
```

**`seed_real_data.py`** - Realistic test data
```bash
python backend/scripts/seed/seed_real_data.py
```

**`seed_rooms_simple.py`** - Simple room data
```bash
python backend/scripts/seed/seed_rooms_simple.py
```

**`seed_july_2025.py`** - Historical July 2025 data
```bash
python backend/scripts/seed/seed_july_2025.py
```

---

### `verify/` - Verification & Diagnostics

#### `check_setup.py`
**Verify database setup and provide diagnostics**

```bash
python backend/scripts/verify/check_setup.py
```

**Checks:**
- ✓ Environment variables present
- ✓ Migration file exists
- ✓ Models import successfully
- ✓ Database connection working
- ✓ All tables created
- ✓ Initial data seeded

**Provides:**
- Connection diagnostics
- Table verification
- Record counts
- Troubleshooting tips

---

## 📊 What Gets Created

### 12 Database Tables

| Table | Purpose | Initial Records |
|-------|---------|-----------------|
| users | Authentication | 0 |
| room_types | Room categories | 4 ✅ |
| rooms | Individual rooms | 0 |
| room_images | Room photos | 0 |
| room_type_images | Room showcases | 0 |
| guests | Guest profiles | 0 |
| reservations | Bookings | 0 |
| payments | Payment tracking | 0 |
| payment_attachments | Payment proofs | 0 |
| settings | Admin configuration | 8 ✅ |
| discounts | Promotional pricing | 0 |
| booking_channels | Booking sources | 5 ✅ |

### Initial Data Seeded

**Room Types (4):**
- Standard: IDR 500,000/night
- Deluxe: IDR 750,000/night
- Suite: IDR 1,200,000/night
- Penthouse: IDR 2,000,000/night

**Booking Channels (5):**
- Direct Booking (0% commission)
- Tiket.com (15% commission)
- Traveloka (18% commission)
- Booking.com (20% commission)
- Other (0% commission)

**Settings (8):**
- hotel_name, hotel_address, hotel_phone
- check_in_time, check_out_time
- timezone, currency, default_language

**Total: 17 initial records**

---

## ⚙️ Setup Prerequisites

### Python 3.12
```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate py3.12
```

### Dependencies
```bash
pip install -r backend/requirements.txt
```

### Environment Variables (.env)
```env
DATABASE_URL=postgresql://postgres.qfyhhdhrvnjjgmkswrvw:...@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
DB_HOST=aws-1-ap-southeast-1.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=...
```

---

## 📝 Usage Workflow

### First Time Setup

```bash
# 1. Navigate to project root
cd /path/to/Hotel-Management-System

# 2. Activate Python 3.12
source $(conda info --base)/etc/profile.d/conda.sh
conda activate py3.12

# 3. Complete database setup (all-in-one)
python backend/scripts/init/setup_complete.py

# 4. Create admin user
python backend/init_admin.py

# 5. Start backend server
cd backend && uvicorn app:app --reload

# 6. Access API documentation
# http://localhost:8000/api/docs
```

### Verification Commands

**Check all tables created:**
```bash
python -c "from backend.models import Base; print(list(Base.metadata.tables.keys()))"
```

**Count initial data:**
```bash
python -c "from backend.database import SessionLocal; from backend.models import RoomType; print(f'Room types: {SessionLocal().query(RoomType).count()}')"
```

**Run verification script:**
```bash
python backend/scripts/verify/check_setup.py
```

---

## ✅ Features

### All Scripts Are Idempotent
- Safe to run multiple times
- Duplicate checks prevent data duplication
- Transaction management for data integrity

### Comprehensive Error Handling
- Detailed error messages
- Connection diagnostics
- Troubleshooting guidance

### Progress Reporting
- Step-by-step output
- Status indicators (✓, ✗, •)
- Record counts and summaries

---

## 🆘 Troubleshooting

### "Module not found: dotenv"
```bash
pip install -r backend/requirements.txt
```

### "Connection refused"
- Verify Supabase is running
- Check DATABASE_URL in .env
- Run: `python backend/scripts/verify/check_setup.py`

### "Table already exists"
Normal with `IF NOT EXISTS` - safe to re-run

### "Missing environment variables"
```bash
cat backend/.env
```
Ensure all required variables are present.

---

## 📚 Related Documentation

- [Database Design](../../docs/architecture/DATABASE_DESIGN.md) - Complete schema documentation
- [Backend Tasks](../../docs/planning/BACKEND_TASKS.md) - Development phases and roadmap
- [Setup Complete](../../SETUP_COMPLETE.md) - Overall setup status and next steps

---

## 🎯 Next Steps After Setup

1. **Create Admin User:**
   ```bash
   python backend/init_admin.py
   ```

2. **Start Backend Server:**
   ```bash
   cd backend && uvicorn app:app --reload
   ```

3. **Access API Docs:**
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc
   - Health: http://localhost:8000/health

4. **Begin Phase 1 Development:**
   - Authentication endpoints
   - User management
   - Room management

---

**Ready to build! 🚀**
