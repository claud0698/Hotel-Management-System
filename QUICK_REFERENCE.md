# Quick Reference - Hotel Management System

**Last Updated:** November 8, 2025 | **Status:** ✅ Foundation Complete | **Progress:** 35%

---

## 🚀 Start Backend Server

```bash
# Option 1: Direct Python (fastest)
cd backend
/opt/homebrew/Caskroom/miniconda/base/envs/py3.12/bin/python app.py

# Option 2: Using uvicorn directly
cd backend
uvicorn app:app --reload

# Option 3: From project root
python backend/app.py
```

**Server runs on:** `http://localhost:8001`

---

## 📍 Key Endpoints

### Health & Status
```
GET  /health              → System health check
GET  /api                 → API info and docs
GET  /api/docs            → Swagger UI (interactive)
GET  /api/redoc           → ReDoc documentation
```

### Authentication
```
POST /api/auth/login      → Login (returns JWT token)
GET  /api/auth/me         → Get current user info
```

### Users (Stub - needs Phase 1 implementation)
```
GET  /api/users           → List users
POST /api/users           → Create user
GET  /api/users/{id}      → Get user details
PUT  /api/users/{id}      → Update user
```

### Rooms (Stub - needs Phase 1 implementation)
```
GET  /api/rooms           → List rooms
POST /api/rooms           → Create room
GET  /api/rooms/{id}      → Get room details
PUT  /api/rooms/{id}      → Update room
```

### Payments
```
GET  /api/payments        → List payments
POST /api/payments        → Create payment
GET  /api/payments/{id}   → Get payment details
PUT  /api/payments/{id}   → Update payment
```

### Dashboard
```
GET  /api/dashboard/metrics  → Occupancy & revenue
GET  /api/dashboard/summary  → Recent activity
GET  /api/dashboard/revenue  → Revenue breakdown
```

---

## 🧪 Quick API Tests

### Test Health Check
```bash
curl http://localhost:8001/health | jq
```

### Test Login
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Test Authenticated Request
```bash
TOKEN="<token_from_login_response>"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/auth/me | jq
```

### Test API Info
```bash
curl http://localhost:8001/api | jq
```

---

## 📁 Important Files & Directories

### Backend Structure
```
backend/
├── app.py                 # Main FastAPI application
├── models.py              # SQLAlchemy database models (12 models)
├── database.py            # Database connection & session
├── security.py            # JWT and password utilities
├── health_check.py        # Standalone health check script
├── routes/
│   ├── auth_router.py     # Authentication endpoints
│   ├── users_router.py    # User management endpoints
│   ├── rooms_router.py    # Room management endpoints
│   ├── payments_router.py # Payment endpoints (refactored)
│   └── dashboard_router.py # Dashboard endpoints (new)
├── scripts/
│   ├── init/              # Database initialization scripts
│   ├── seed/              # Database seeding scripts
│   └── verify/            # Verification scripts
└── requirements.txt       # Python dependencies
```

### Documentation
```
docs/
├── architecture/
│   └── PROJECT_OVERVIEW.md
├── planning/
│   └── PRD.md
└── README.md

PROJECT_PROGRESS.md      # Overall project status
PHASE_1_ROADMAP.md      # 4-week development plan
SESSION_SUMMARY.md      # Today's session recap
QUICK_REFERENCE.md      # This file
README.md               # Main project README
```

---

## 🔧 Database Commands

### Check Database Health
```bash
# From backend directory
python health_check.py

# Or via API
curl http://localhost:8001/health | jq
```

### Initialize Database (if needed)
```bash
cd backend/scripts/init
python setup_complete.py
```

### Seed Initial Data (if needed)
```bash
cd backend/scripts/seed
python initial_data.py
```

### Verify Database
```bash
cd backend/scripts/verify
python check_setup.py
```

---

## 👤 Admin User Credentials

```
Username: admin
Password: admin123
Role: user (can be promoted in database)
```

**To Login:**
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 📊 Current Database Status

```
Tables:        12/12 ✅
Indexes:       42/42 ✅
Initial Data:  17 records ✅
Records by type:
  - Users:     1 (admin)
  - Room Types: 4
  - Channels:  5
  - Settings:  8
```

---

## 🛠️ Common Development Tasks

### Add a New Endpoint
1. Create route in `backend/routes/xxx_router.py`
2. Add schema in `backend/schemas.py` (if needed)
3. Include router in `app.py` (`app.include_router(...)`)
4. Test with curl or Swagger UI
5. Add to documentation

### Modify Database Schema
1. Update model in `backend/models.py`
2. Migration will be automatic on app restart (SQLAlchemy)
3. Test with database health check

### Test Authentication
1. Login to get token: `POST /api/auth/login`
2. Use token in request: `Authorization: Bearer <token>`
3. Test protected endpoint: `GET /api/auth/me`

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| `PROJECT_PROGRESS.md` | Complete project status & metrics |
| `PHASE_1_ROADMAP.md` | Week-by-week Phase 1 plan |
| `SESSION_SUMMARY.md` | Today's session detailed recap |
| `QUICK_REFERENCE.md` | This file - quick lookup |
| `README.md` | Main project overview |
| `docs/planning/PRD.md` | Product requirements |
| `backend/README.md` | Backend setup guide |
| `backend/scripts/README.md` | Script usage guide |

---

## ⚠️ Known Issues (Minor)

| Issue | Severity | Impact | Fix |
|-------|----------|--------|-----|
| SQLAlchemy relationship warnings | LOW | None - informational only | Phase 1.5 refactor |
| Bcrypt version compatibility | LOW | None - works fine | Update passlib |
| CORS allows all origins | MEDIUM | Dev-only, restrict in prod | Update .env |
| No rate limiting | MEDIUM | Phase 1 Week 1 | Add middleware |
| No RBAC middleware | MEDIUM | Phase 1 Week 1 | Add decorators |

---

## 📋 Phase 1 Schedule

**Timeline:** 4 weeks (Weeks 1-4)
**Target:** December 5, 2025

| Week | Focus | Hours | Endpoints |
|------|-------|-------|-----------|
| 1 | Security & Auth | 15-18 | JWT refresh, rate limiting, RBAC |
| 2 | User Management | 12-15 | Register, profile, list, delete |
| 3 | Room Management | 12-15 | CRUD, room types, images |
| 4 | Reservations | 18-20 | Book, modify, check-in/out, payments |

---

## 🎯 Success Criteria

- [ ] All Phase 1 endpoints implemented (25+)
- [ ] Test coverage >70%
- [ ] API documentation 100% complete
- [ ] Security hardening complete
- [ ] Zero critical bugs
- [ ] Performance <200ms average response

---

## 🔗 Useful Links

- **Local API:** http://localhost:8001
- **Swagger Docs:** http://localhost:8001/api/docs
- **ReDoc Docs:** http://localhost:8001/api/redoc
- **Health Check:** http://localhost:8001/health
- **Database:** Supabase PostgreSQL

---

## 💡 Tips & Tricks

### Quick Test All Endpoints
```bash
# Test health
curl http://localhost:8001/health

# Test login
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Test authenticated endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/auth/me
```

### View Swagger UI
```bash
open http://localhost:8001/api/docs
```

### Check Recent Commits
```bash
git log --oneline -10
```

### View Current Git Status
```bash
git status
```

---

## 🚀 Next Steps

1. **Start Phase 1 Development**
   - Read `PHASE_1_ROADMAP.md` for detailed plan
   - Begin Week 1: Security & authentication hardening

2. **Implement User Registration**
   - Create `POST /api/users` endpoint
   - Add email validation
   - Hash password with bcrypt
   - Test with Swagger UI

3. **Add Room Management**
   - CRUD endpoints for rooms
   - Room type management
   - Status tracking

4. **Build Reservation System**
   - Availability checking
   - Rate calculation
   - Confirmation number generation

---

## ❓ Troubleshooting

### Server won't start
```bash
# Check if port 8001 is in use
lsof -i :8001

# Kill process if needed
kill -9 <PID>

# Restart server
python app.py
```

### Database connection error
```bash
# Check .env file
cat backend/.env

# Verify DATABASE_URL format
echo $DATABASE_URL

# Test connection
python backend/health_check.py
```

### Import errors
```bash
# Ensure Python 3.12 is active
python --version

# Reinstall dependencies
pip install -r backend/requirements.txt
```

---

**Last Updated:** 2025-11-08
**Status:** ✅ Ready for Phase 1
**Next Milestone:** Phase 1 Completion (Dec 5, 2025)
