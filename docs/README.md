# Hotel Management System - Documentation

**Version**: 1.0 (MVP)
**Last Updated**: November 7, 2025
**Status**: Ready for Development

---

## 📚 Documentation Index

### Core Planning Documents

#### 1. [PRD.md](planning/PRD.md) - Product Requirements Document
**What to build** - Complete feature specifications for MVP v1.0

- Executive summary and business goals
- Target users (Admin vs User roles)
- 7 core features in detail
- Out of scope (deferred to v2.0)
- Success criteria
- Timeline: 10 weeks

**Read this to understand**: Product scope, features, and requirements

---

#### 2. [PROJECT_OVERVIEW.md](architecture/PROJECT_OVERVIEW.md) - Architecture Overview
**How it's built** - Technical architecture and development roadmap

- System architecture (layered monolithic)
- Technology stack (FastAPI + React + PostgreSQL)
- Database schema (6 tables)
- API structure (35 endpoints)
- Frontend structure (9 pages)
- Development phases (9 phases)
- Key business logic

**Read this to understand**: Technical decisions, architecture, and structure

---

#### 3. [BACKEND_TASKS.md](planning/BACKEND_TASKS.md) - Backend Development Tasks
**Backend implementation guide** - 30 detailed tasks across 9 phases

- Phase-by-phase breakdown
- What to salvage from KOS system (60% reusable)
- Database migration strategy
- Task estimates (85 hours / 6-7 weeks)
- Acceptance criteria per task
- Dependencies and order

**Read this to**: Start backend development

---

#### 4. [FRONTEND_TASKS.md](planning/FRONTEND_TASKS.md) - Frontend Development Tasks
**Frontend implementation guide** - 32 detailed tasks across 11 phases

- Phase-by-phase breakdown
- What to salvage from KOS system (70% reusable)
- Component structure
- Task estimates (100 hours / 5-6 weeks)
- Acceptance criteria per task
- New dependencies needed

**Read this to**: Start frontend development

---

## 🎯 Quick Navigation

### For Product Managers / Stakeholders:
1. Start with [PRD.md](planning/PRD.md) to understand **what** we're building
2. Review [PROJECT_OVERVIEW.md](architecture/PROJECT_OVERVIEW.md) for high-level architecture
3. Check timeline and milestones in both documents

### For Backend Developers:
1. Read [PROJECT_OVERVIEW.md](architecture/PROJECT_OVERVIEW.md) - Database & API sections
2. Start with [BACKEND_TASKS.md](planning/BACKEND_TASKS.md)
3. Begin with Phase 1: Foundation (Week 1-2)

### For Frontend Developers:
1. Read [PROJECT_OVERVIEW.md](architecture/PROJECT_OVERVIEW.md) - Frontend section
2. Start with [FRONTEND_TASKS.md](planning/FRONTEND_TASKS.md)
3. Begin with Phase 1: Foundation & Types (Week 1)

### For Full-Stack Developers:
1. Review all 4 core documents
2. Start backend first (frontend depends on API)
3. Work through both task lists in parallel (if possible)

---

## 📊 Project Statistics

### Scope
- **Features**: 7 core features (MVP v1.0)
- **User Roles**: 2 (Admin, User)
- **Database Tables**: 6
- **API Endpoints**: 35
- **Frontend Pages**: 9

### Development Estimates
- **Backend**: 85 hours (6-7 weeks)
- **Frontend**: 100 hours (5-6 weeks)
- **Total**: ~185 hours (11-13 weeks full-time)

### Technology Stack
- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Zustand
- **Infrastructure**: Vercel (frontend), Google Cloud Run (backend)

---

## 🗂️ Documentation Structure

```
docs/
├── README.md                          # This file
│
├── planning/                          # Planning & requirements
│   ├── PRD.md                         # Product requirements (MVP v1.0)
│   ├── BACKEND_TASKS.md               # Backend task breakdown (30 tasks)
│   └── FRONTEND_TASKS.md              # Frontend task breakdown (32 tasks)
│
└── architecture/                      # Architecture & design
    └── PROJECT_OVERVIEW.md            # Technical architecture overview
```

---

## 🚀 Getting Started

### Prerequisites
- **Backend**: Python 3.11+, PostgreSQL 14+
- **Frontend**: Node.js 18+, npm
- **Tools**: Git, VS Code (recommended)

### Setup (Quick Start)
```bash
# Clone repository
git clone <repo-url>
cd Hotel-Management-System

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_hotel_db.py  # Initialize database

# Frontend setup
cd ../frontend
npm install
npm run dev
```

Detailed setup instructions will be added as development progresses.

---

## 📈 Development Roadmap

### Phase 1: Foundation (Week 1-2)
- Backend: Database models, JWT auth with roles, user management
- Frontend: API types, auth store with roles, layout updates

### Phase 2: Room Management (Week 2-3)
- Backend: Room types & rooms endpoints, availability checking
- Frontend: Room types page, rooms page, room store

### Phase 3: Guest Management (Week 3)
- Backend: Guest endpoints, search functionality
- Frontend: Guests page, guest store

### Phase 4: Reservation System (Week 3-5) ← **Most Complex**
- Backend: Reservation CRUD, conflict detection, extend stay
- Frontend: Availability search, new reservation flow, reservations list

### Phase 5: Check-In/Out (Week 5-6)
- Backend: Check-in/out endpoints, arrivals/departures
- Frontend: Check-in page, check-out page, room assignment

### Phase 6: Payments (Week 6-7)
- Backend: Payment CRUD, balance calculation
- Frontend: Payments page, payment form

### Phase 7: Dashboard (Week 7-8)
- Backend: Metrics calculation, summary endpoints
- Frontend: Dashboard redesign for hotel metrics

### Phase 8: Polish (Week 8-9)
- Backend: Testing, validation, error handling, migrations
- Frontend: User management, loading states, mobile responsive

### Phase 9: Deployment (Week 9-10)
- Backend: Production config, documentation, deployment
- Frontend: Build optimization, environment config, deployment

---

## 🎓 Key Concepts

### From KOS to Hotel System

**What Changed**:
- **Tenants** → **Guests** (short-term stays)
- **Move-in/Move-out** → **Check-in/Check-out** (daily operations)
- **Monthly payments** → **Reservation-based payments** (per stay)
- **Simple rooms** → **Room types + rooms** (categorized inventory)

**What Stayed**:
- Authentication system (enhanced with roles)
- Room management (enhanced with types)
- Database infrastructure (SQLAlchemy + FastAPI)
- Frontend infrastructure (React + Tailwind)

### Core Business Logic

**Availability Checking**:
- Room is available if NOT occupied during requested dates
- Conflict detection: `check_in < existing.check_out AND check_out > existing.check_in`
- Excludes cancelled and checked-out reservations

**Check-In Process**:
1. Find reservation (status = confirmed)
2. Assign room if not assigned
3. Update reservation status → checked_in
4. Update room status → occupied
5. Record timestamp

**Check-Out Process**:
1. Find reservation (status = checked_in)
2. Calculate balance (total - paid)
3. Record final payment (optional)
4. Update reservation status → checked_out
5. Update room status → available
6. Record timestamp

---

## ✅ Success Criteria

### MVP Launch
- [ ] Zero critical bugs
- [ ] All 7 core features functional
- [ ] 100% availability accuracy (no double-bookings)
- [ ] Check-in/out process < 3 minutes
- [ ] System response time < 3 seconds
- [ ] Documentation complete

### Post-Launch (First Month)
- [ ] 95%+ staff adoption
- [ ] Zero double-booking incidents
- [ ] 99% uptime
- [ ] Positive user feedback (>4/5)
- [ ] All reports accurate

---

## 🔄 Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2025-11-07 | Initial documentation for Hotel Management System MVP |
| 0.x | 2025-10-24 | Previous KOS Management Dashboard documentation (archived) |

---

## 📞 Support & Questions

### For Technical Questions:
- Check [PROJECT_OVERVIEW.md](architecture/PROJECT_OVERVIEW.md) for architecture details
- Review specific task files for implementation guidance

### For Feature Questions:
- Check [PRD.md](planning/PRD.md) for feature specifications
- Review acceptance criteria in task files

### For Development Questions:
- Backend: See [BACKEND_TASKS.md](planning/BACKEND_TASKS.md)
- Frontend: See [FRONTEND_TASKS.md](planning/FRONTEND_TASKS.md)

---

**Status**: ✅ **Documentation Complete - Ready for Development**

Start with Phase 1 tasks and work sequentially through the phases!

🚀 **Let's build a great hotel management system!**
