# Database Seeding Scripts

Populate the database with initial data, test data, and fixtures for Hotel Management System v1.0.

## 📋 Overview

This folder contains scripts for seeding various types of data into the database.

### Scripts in This Folder

| Script | Purpose | Records | Time |
|--------|---------|---------|------|
| `initial_data.py` | ⭐ **Essential data** (recommended) | 17 | ~5s |
| `seed.py` | Original seeding script | Variable | ~10s |
| `seed_admin_user.py` | Admin user creation | 1 | ~2s |
| `seed_real_data.py` | Realistic test data | Many | ~15s |
| `seed_rooms_simple.py` | Simple room data | 10+ | ~5s |
| `seed_july_2025.py` | Historical July 2025 data | Custom | ~10s |

---

## 🚀 Quick Start

### Recommended: Seed Initial Data

Essential data for Hotel Management System:

```bash
python initial_data.py
```

**What it seeds:**
- ✓ 4 room types (Standard, Deluxe, Suite, Penthouse)
- ✓ 5 booking channels (Direct, Tiket, Traveloka, Booking, Other)
- ✓ 8 default settings (hotel info, times, localization)

**Output:**
```
✓ Initial data seeded successfully!
  - Room types: 4
  - Booking channels: 5
  - Settings: 8
```

**Time:** ~5 seconds

---

## 📝 Script Details

### initial_data.py

**⭐ RECOMMENDED - Essential data for v1.0**

```bash
python initial_data.py
```

**What it seeds:**

**Room Types (4):**
- Standard: IDR 500,000/night
  - 2 adults, 1 child
  - Basic amenities
- Deluxe: IDR 750,000/night
  - 2 adults, 2 children
  - Ocean view
- Suite: IDR 1,200,000/night
  - 4 adults, 2 children
  - Living area, kitchenette
- Penthouse: IDR 2,000,000/night
  - 4 adults, 2 children
  - Terrace, concierge service

**Booking Channels (5):**
- Direct Booking (0% commission) - Walk-in, phone, email, website
- Tiket.com (15% commission) - OTA integration
- Traveloka (18% commission) - OTA integration
- Booking.com (20% commission) - OTA integration
- Other (0% commission) - Other sources

**Settings (8):**
- hotel_name
- hotel_address
- hotel_phone
- check_in_time (14:00)
- check_out_time (12:00)
- timezone (Asia/Jakarta)
- currency (IDR)
- default_language (id)

**Features:**
- ✓ Duplicate checks (safe to re-run)
- ✓ Full audit trail
- ✓ Transaction management
- ✓ Handles existing records gracefully

**Best for:**
- Initial database setup
- Production-ready data
- Standard hotel configuration

---

### seed.py

**Original seeding script**

```bash
python seed.py
```

**Purpose:**
- Populates database with initial test data
- Can be customized for specific needs
- Legacy script maintained for reference

**Use when:**
- Need to re-seed database
- Want to use original seeding logic
- Testing data population

---

### seed_admin_user.py

**Create admin user in database**

```bash
python seed_admin_user.py
```

**Features:**
- ✓ Creates user with admin role
- ✓ Password hashing with bcrypt
- ✓ Audit fields (created_at, updated_at)

**Use when:**
- Adding additional admin accounts
- Recreating admin user
- Testing authentication

**Note:** Use `backend/init_admin.py` for interactive admin creation instead

---

### seed_real_data.py

**Realistic production-like test data**

```bash
python seed_real_data.py
```

**Features:**
- ✓ Realistic guest names and information
- ✓ Multiple reservations and payments
- ✓ Test data for all major entities
- ✓ Good for development and testing

**Use when:**
- Development and testing
- Need realistic data scenarios
- Testing reports and analytics

**Time:** ~15 seconds

---

### seed_rooms_simple.py

**Simple room data for testing**

```bash
python seed_rooms_simple.py
```

**Features:**
- ✓ Creates 10+ rooms
- ✓ Assigned to room types
- ✓ Various floor assignments
- ✓ Good for basic testing

**Use when:**
- Need room data quickly
- Testing room management features
- Basic availability testing

**Time:** ~5 seconds

---

### seed_july_2025.py

**Historical data for July 2025**

```bash
python seed_july_2025.py
```

**Purpose:**
- Creates specific data for July 2025
- Useful for historical data testing
- Month-specific scenarios

**Use when:**
- Testing historical data handling
- Specific month testing needed
- Legacy data recreation

---

## 📊 Data Relationships

### Room Type Hierarchy

```
Room Type (Standard, Deluxe, Suite, Penthouse)
  ↓
  Room (Individual rooms assigned to type)
    ↓
    Reservation (Bookings for specific room)
      ↓
      Guest (Who's booking)
      Payment (Payment tracking)
```

### Booking Channel Tracking

```
Booking Channel (Direct, Tiket, Traveloka, Booking, Other)
  ↓
  Commission Percentage (0%, 15%, 18%, 20%)
  ↓
  Reservation (Tracked by channel)
```

---

## ⚙️ Prerequisites

### Database Tables Must Exist First

Run initialization scripts first:
```bash
cd ../init
python setup_complete.py
```

Or:
```bash
python create_tables.py
```

### Python 3.12

```bash
source $(conda info --base)/etc/profile.d/conda.sh
conda activate py3.12
```

### Environment File (.env)

```env
DATABASE_URL=postgresql://...
DB_HOST=...
DB_USER=...
DB_PASSWORD=...
```

---

## 📝 Usage Workflow

### Complete Setup Sequence

```bash
# 1. Navigate to project
cd backend/scripts

# 2. Initialize database
cd init
python setup_complete.py

# This already includes seeding, OR:

# 3. Create tables (separate step)
cd init
python create_tables.py

# 4. Seed initial data (separate step)
cd ../seed
python initial_data.py

# 5. Verify setup
cd ../verify
python check_setup.py
```

### Adding Custom Seed Data

Create new script following this pattern:

```python
from database import SessionLocal
from models import RoomType, Guest, etc.

db = SessionLocal()

# Your seeding logic
room_type = RoomType(
    name="Custom",
    code="CUS",
    default_rate=1000000,
    ...
)
db.add(room_type)
db.commit()
db.close()
```

---

## 🆘 Troubleshooting

### "Table does not exist"
- Run initialization first: `cd ../init && python create_tables.py`

### "Duplicate entry"
- Scripts check for duplicates automatically
- Safe to re-run existing seeding scripts
- Use `db.query().filter(...).first()` to check

### "Connection error"
- Check .env file
- Verify DATABASE_URL
- Test connection: `cd ../verify && python check_setup.py`

### "Module not found"
```bash
pip install -r backend/requirements.txt
```

---

## 📈 Data Quantities

### initial_data.py
- ✓ 4 room types
- ✓ 5 booking channels
- ✓ 8 settings
- **Total: 17 records**

### seed_real_data.py
- ✓ Multiple guests
- ✓ Multiple reservations
- ✓ Multiple payments
- **Total: 50+ records**

### seed_rooms_simple.py
- ✓ 10+ rooms
- **Total: 10+ records**

---

## 🔄 Idempotency

All seeding scripts are **idempotent** (safe to re-run):

```python
# Check for existing record
existing = db.query(RoomType).filter(
    RoomType.code == 'STD'
).first()

if not existing:
    # Only add if doesn't exist
    db.add(RoomType(...))
    db.commit()
```

---

## 📚 Next Steps

After seeding:

1. **Verify data was seeded:**
   ```bash
   cd ../verify
   python check_setup.py
   ```

2. **Create admin user:**
   ```bash
   python ../../../init_admin.py
   ```

3. **Start backend:**
   ```bash
   cd ../../
   uvicorn app:app --reload
   ```

4. **Access API:**
   - http://localhost:8000/api/docs

---

## 🎯 Best Practices

✅ **Always initialize tables first** - Use `init/setup_complete.py`
✅ **Use initial_data.py** - Contains recommended data for v1.0
✅ **Check for duplicates** - Scripts prevent duplicate entries
✅ **Verify after seeding** - Use `verify/check_setup.py`
✅ **Keep transactions clean** - Proper commit/rollback

---

**Questions?** Check the main scripts README: `../README.md`
