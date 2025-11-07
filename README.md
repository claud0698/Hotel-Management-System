# 🏨 Hotel Management System

**Modern Property Management Solution for Hotels**

A comprehensive web application built with React + TypeScript + FastAPI to help hotel operators manage daily operations efficiently.

---

## 📋 Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Documentation** | ✅ Complete | PRD, Architecture, Tasks (62 total) |
| **Backend** | 🔄 In Planning | FastAPI + SQLAlchemy + PostgreSQL |
| **Frontend** | 🔄 In Planning | React 19 + TypeScript + Tailwind |
| **Database** | 📝 Designed | 6 tables, 35 API endpoints |
| **Overall** | 📋 **READY FOR DEVELOPMENT** | MVP v1.0 scope defined |

---

## 🎯 What We're Building

### Hotel Management System MVP v1.0

A streamlined hotel operations platform for small to mid-size hotels (10-200 rooms) with:

- **Room inventory management** with room types
- **Reservation booking** with availability checking
- **Guest profile management** and history
- **Check-in/check-out** operations
- **Simple payment tracking** per reservation
- **Basic operational dashboard**
- **Two-tier user access** (Admin + User roles)

### Key Goals
1. **Zero double-bookings** - 100% accurate availability
2. **Fast operations** - Check-in/out in < 3 minutes
3. **Simple & reliable** - Easy to learn (< 1 hour training)

---

## 📚 Documentation

**📖 Complete Documentation**: See [docs/README.md](./docs/README.md) for the full documentation index

### Core Documents

#### 1. [PRD.md](docs/planning/PRD.md) - Product Requirements
**What to build** - Complete feature specifications for MVP v1.0
- 7 core features defined
- User roles (Admin vs User)
- Out of scope (v2.0+)
- 10-week timeline

#### 2. [PROJECT_OVERVIEW.md](docs/architecture/PROJECT_OVERVIEW.md) - Architecture
**How it's built** - Technical architecture and roadmap
- System architecture
- Technology stack
- Database schema (6 tables)
- API structure (35 endpoints)
- Development phases

#### 3. [BACKEND_TASKS.md](docs/planning/BACKEND_TASKS.md) - Backend Development
**Backend guide** - 30 detailed tasks across 9 phases
- 85 hours estimated (6-7 weeks)
- What to salvage from existing code (60%)
- Acceptance criteria per task

#### 4. [FRONTEND_TASKS.md](docs/planning/FRONTEND_TASKS.md) - Frontend Development
**Frontend guide** - 32 detailed tasks across 11 phases
- 100 hours estimated (5-6 weeks)
- What to salvage from existing code (70%)
- Component structure

---

## 🚀 Quick Start (Coming Soon)

### Prerequisites
- **Backend**: Python 3.11+, PostgreSQL 14+
- **Frontend**: Node.js 18+, npm
- **Tools**: Git, VS Code (recommended)

### Setup (Development)
```bash
# Clone repository
git clone <repo-url>
cd Hotel-Management-System

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_hotel_db.py

# Frontend setup
cd ../frontend
npm install
npm run dev
```

Detailed instructions will be added as development progresses.

---

## ✨ Features (MVP v1.0)

### ✅ Two-Tier Authentication
- Admin: Full access (CRUD everything, manage users, dashboard)
- User: Can create/update but not delete, cannot manage users
- JWT token authentication with roles

### ✅ Room Inventory Management
- Room types (Standard, Deluxe, Suite, etc.)
- Individual rooms with status tracking
- Occupancy rate calculation
- Admin-only configuration

### ✅ Reservation Management
- Booking with availability checking
- Conflict detection (no double-booking)
- Unique confirmation numbers
- Extend stay functionality
- Cancel reservations

### ✅ Guest Management
- Guest profiles with contact info
- Guest reservation history
- Search by name/email/phone
- Both admin and user can create guests

### ✅ Front Desk Operations
- Check-in process (assign room, update status)
- Check-out process (settle payment, free room)
- Today's arrivals/departures lists
- In-house guests view
- Walk-in guest handling

### ✅ Simple Payment Tracking
- Record payments per reservation
- Track balance (total - paid)
- Payment methods (cash, card, transfer)
- No invoicing (v1.0 limitation)

### ✅ Basic Dashboard
- Today's arrivals/departures count
- Occupancy rate
- Simple revenue totals
- Quick access links
- No charts/exports (v1.0 limitation)

---

## 🏗️ Architecture

```
Frontend (React 19 + TypeScript)        Backend (FastAPI)
├── Pages (9)                           ├── API Routes (35 endpoints)
│  ├── Login                            │  ├── /auth (3)
│  ├── Dashboard                        │  ├── /users (5)
│  ├── Rooms                            │  ├── /room-types (5)
│  ├── Room Types                       │  ├── /rooms (6)
│  ├── Guests                           │  ├── /guests (5)
│  ├── Reservations                     │  ├── /reservations (9)
│  ├── Check-In                         │  ├── /payments (5)
│  ├── Check-Out                        │  └── /dashboard (2)
│  └── Users                            │
├── Components (Layout, Forms)          └── Database Models (6)
├── Stores (Zustand)                    ├── User
│  ├── Auth                             ├── RoomType
│  ├── Rooms                            ├── Room
│  ├── Guests                           ├── Guest
│  ├── Reservations                     ├── Reservation
│  └── Dashboard                        └── Payment
└── API Client (Type-safe)
```

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend** | React + TypeScript | 19.x |
| **Build Tool** | Vite | 5.x |
| **Styling** | Tailwind CSS | 4.x |
| **State** | Zustand | 4.x |
| **Routing** | React Router | v7 |
| **i18n** | react-i18next | Latest |
| **Backend** | Python FastAPI | 3.11+ |
| **ORM** | SQLAlchemy | 2.x |
| **Database** | PostgreSQL / SQLite | 14+ / 3.x |
| **Auth** | JWT (PyJWT) | Latest |
| **Migrations** | Alembic | Latest |

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Database Tables** | 6 |
| **API Endpoints** | 35 |
| **Frontend Pages** | 9 |
| **User Roles** | 2 (Admin, User) |
| **Development Time** | ~185 hours (11-13 weeks) |
| **Backend Tasks** | 30 (6-7 weeks) |
| **Frontend Tasks** | 32 (5-6 weeks) |
| **Documentation** | 4 core docs + guides |

---

## 📈 Development Roadmap

### Phase 1: Foundation (Week 1-2)
- Backend: Database models, JWT auth with roles, user management
- Frontend: API types, auth store with roles, layout updates

### Phase 2-3: Room & Guest Management (Week 2-3)
- Backend: Room types, rooms, guests endpoints
- Frontend: Room types page, rooms page, guests page

### Phase 4: Reservation System (Week 3-5) ⭐ **Most Complex**
- Backend: Reservation CRUD, conflict detection, availability
- Frontend: New reservation flow, reservations list, availability search

### Phase 5: Check-In/Out (Week 5-6)
- Backend: Check-in/out endpoints, arrivals/departures
- Frontend: Check-in page, check-out page, room assignment

### Phase 6-7: Payments & Dashboard (Week 6-8)
- Backend: Payments, balance calculation, dashboard metrics
- Frontend: Payments page, dashboard redesign

### Phase 8-9: Polish & Deploy (Week 8-10)
- Backend: Testing, validation, migrations, deployment
- Frontend: Mobile responsive, loading states, build optimization

---

## 🎯 Success Criteria

### MVP Launch
- [ ] Zero critical bugs in production
- [ ] All 7 core features functional
- [ ] 100% availability accuracy (no double-bookings)
- [ ] Check-in/out process < 3 minutes
- [ ] System response time < 3 seconds
- [ ] User training < 1 hour
- [ ] Documentation complete

### Post-Launch (First Month)
- [ ] 95%+ staff adoption
- [ ] Zero double-booking incidents
- [ ] 99% uptime maintained
- [ ] Positive user feedback (>4/5)
- [ ] All reports accurate

---

## 🔄 Migration from KOS System

### What We're Keeping
✅ Infrastructure (FastAPI, React, Tailwind setup)
✅ Authentication (upgraded to JWT with roles)
✅ Database setup (SQLAlchemy, migrations)
✅ Layout components (Navbar, Sidebar)
✅ State management (Zustand pattern)

### What's Changing
🔄 **Tenants** → **Guests** (short-term stays)
🔄 **Move-in/Move-out** → **Check-in/Check-out**
🔄 **Monthly payments** → **Reservation payments**
🔄 **Simple rooms** → **Room types + Rooms**
🔄 **Dashboard** → Hotel metrics (occupancy, ADR, RevPAR)

### What's Removed
❌ Expense tracking (deferred to v2.0)
❌ Room history (not needed for v1.0)
❌ KOS-specific terminology

---

## 📦 Project Structure

```
Hotel-Management-System/
├── backend/                          # Python FastAPI backend
│   ├── app.py                        # Main application
│   ├── models.py                     # SQLAlchemy models (6 tables)
│   ├── security.py                   # JWT auth + roles
│   ├── database.py                   # Database config
│   ├── routes/                       # API endpoints
│   │   ├── auth_router.py
│   │   ├── users_router.py
│   │   ├── room_types_router.py
│   │   ├── rooms_router.py
│   │   ├── guests_router.py
│   │   ├── reservations_router.py
│   │   ├── payments_router.py
│   │   └── dashboard_router.py
│   ├── scripts/                      # Database utilities
│   └── requirements.txt              # Python dependencies
│
├── frontend/                         # React TypeScript frontend
│   ├── src/
│   │   ├── pages/                    # 9 page components
│   │   │   ├── LoginPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── RoomsPage.tsx
│   │   │   ├── RoomTypesPage.tsx
│   │   │   ├── GuestsPage.tsx
│   │   │   ├── ReservationsPage.tsx
│   │   │   ├── NewReservationPage.tsx
│   │   │   ├── CheckInPage.tsx
│   │   │   └── CheckOutPage.tsx
│   │   ├── components/               # Reusable components
│   │   ├── stores/                   # Zustand state stores
│   │   ├── services/                 # API client
│   │   └── locales/                  # i18n translations (EN/ID)
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                             # 📚 Documentation
│   ├── README.md                     # Documentation index
│   ├── planning/
│   │   ├── PRD.md                    # Product requirements
│   │   ├── BACKEND_TASKS.md          # 30 backend tasks
│   │   └── FRONTEND_TASKS.md         # 32 frontend tasks
│   └── architecture/
│       └── PROJECT_OVERVIEW.md       # Technical architecture
│
├── README.md                          # This file
└── SECURITY_ASSESSMENT_REPORT.md     # Security audit
```

---

## 🎓 Core Concepts

### Availability Checking
Room is available if NOT occupied during requested dates:
```
Conflict = (check_in < existing.check_out) AND (check_out > existing.check_in)
```

### Check-In Process
1. Find reservation (status = confirmed)
2. Assign room if not assigned
3. Update reservation status → checked_in
4. Update room status → occupied
5. Record timestamp

### Check-Out Process
1. Find reservation (status = checked_in)
2. Calculate balance (total - paid)
3. Record final payment (optional)
4. Update reservation status → checked_out
5. Update room status → available

---

## 🔐 Security

### Implemented
- ✅ JWT token authentication
- ✅ Role-based access control (RBAC)
- ✅ Password hashing (bcrypt)
- ✅ Protected routes
- ✅ SQL injection prevention
- ✅ XSS protection

### Production TODO
- [ ] HTTPS/SSL enforcement
- [ ] Rate limiting
- [ ] Token refresh mechanism
- [ ] CSRF protection
- [ ] Security headers
- [ ] Database encryption at rest

---

## ❓ Troubleshooting

### Documentation Issues
Check [docs/README.md](./docs/README.md) for complete documentation

### Development Issues
- Backend: See [BACKEND_TASKS.md](docs/planning/BACKEND_TASKS.md)
- Frontend: See [FRONTEND_TASKS.md](docs/planning/FRONTEND_TASKS.md)

### Common Questions
- **How long to develop?** ~11-13 weeks (185 hours)
- **Can I start now?** Yes! Start with Phase 1 tasks
- **What's the tech stack?** FastAPI + React + PostgreSQL
- **Mobile support?** Responsive web UI (mobile-friendly)

---

## 📞 Support

For questions about:
- **Features**: See [PRD.md](docs/planning/PRD.md)
- **Architecture**: See [PROJECT_OVERVIEW.md](docs/architecture/PROJECT_OVERVIEW.md)
- **Backend tasks**: See [BACKEND_TASKS.md](docs/planning/BACKEND_TASKS.md)
- **Frontend tasks**: See [FRONTEND_TASKS.md](docs/planning/FRONTEND_TASKS.md)

---

## 🎉 What's Next?

### Immediate
- [ ] Review all documentation
- [ ] Set up development environment
- [ ] Start with Phase 1: Foundation

### Phase 1 (Week 1-2)
- [ ] Update database models (6 tables)
- [ ] Upgrade to JWT with roles
- [ ] Update API types and client
- [ ] Update navigation and layout

### Ready to Start?
1. Read [docs/README.md](./docs/README.md) - Documentation overview
2. Review [PRD.md](docs/planning/PRD.md) - What we're building
3. Start [BACKEND_TASKS.md](docs/planning/BACKEND_TASKS.md) - Begin development

---

## 📄 License

Private project for Hotel Management System

---

## 👤 About

**Hotel Management System** is designed to help hotel operators manage daily operations efficiently with:
- Intuitive user interface
- Real-time operational metrics
- Automated availability checking
- Simple data entry workflows
- Mobile-responsive design
- Reliable data integrity

**Built with** ❤️ using modern web technologies

**Status**: 📋 **READY FOR DEVELOPMENT**

---

**Last Updated**: November 7, 2025
**Version**: 1.0 (MVP Planning Phase)

🚀 **Ready to start?** → [docs/README.md](./docs/README.md) | [PRD](docs/planning/PRD.md) | [Backend Tasks](docs/planning/BACKEND_TASKS.md)
