# Hotel Management System - Project Overview
## MVP v1.0

**Version**: 1.0 (MVP)
**Last Updated**: November 7, 2025
**Status**: Ready for Development
**Previous System**: KOS Management Dashboard

---

## Table of Contents
1. [System Overview](#system-overview)
2. [MVP Scope](#mvp-scope)
3. [Architecture](#architecture)
4. [Technology Stack](#technology-stack)
5. [Database Design](#database-design)
6. [API Structure](#api-structure)
7. [Frontend Structure](#frontend-structure)
8. [Development Roadmap](#development-roadmap)

---

## System Overview

### What We're Building
A **focused hotel management system** for small to mid-size hotels (up to 200 rooms) to manage daily operations:
- Room inventory and availability
- Guest reservations with conflict detection
- Check-in/check-out processes
- Simple payment tracking
- Operational dashboard

### Target Users
- **Admin**: Hotel manager with full system access
- **User**: Front desk staff with limited permissions

### Key Goals
1. **Zero double-bookings**: 100% accurate availability
2. **Fast operations**: Check-in/out in < 3 minutes
3. **Simple & reliable**: Easy to learn (< 1 hour training)

---

## MVP Scope

### ✅ What's IN v1.0

**Core Features**:
1. **Two-Tier Authentication**
   - Admin: Full CRUD, user management, dashboard
   - User: Create/update only, no delete, no user management

2. **Room Inventory**
   - Room types (Standard, Deluxe, Suite, etc.)
   - Individual rooms with status (available, occupied, out_of_order)
   - Occupancy tracking

3. **Guest Management**
   - Guest profiles with contact info
   - Guest reservation history
   - Search by name/email/phone

4. **Reservations**
   - Create reservations with availability checking
   - Conflict detection (prevents double-booking)
   - Unique confirmation numbers
   - Extend stay functionality
   - Cancel reservations

5. **Front Desk Operations**
   - Check-in process (assign room, update status)
   - Check-out process (settle payment, free room)
   - Today's arrivals/departures lists
   - In-house guests view
   - Walk-in guest handling

6. **Simple Payments**
   - Record payments per reservation
   - Track balance (total - paid)
   - Payment methods (cash, card, transfer)
   - No invoicing, no tax calculation

7. **Basic Dashboard**
   - Today's arrivals/departures count
   - Occupancy rate
   - Simple revenue totals
   - Quick access links
   - No charts, no exports

### ❌ What's OUT (v2.0+)
- Housekeeping module
- Maintenance tracking
- Advanced rate management
- Invoice generation
- Email/SMS notifications
- Report exports (PDF/Excel)
- Online booking engine
- Multi-property support

---

## Architecture

### Architecture Pattern
**Layered Monolithic Architecture** - Simple, proven, easy to maintain

```
┌─────────────────────────────────────────────┐
│         Frontend (React SPA)                │
│    React 19 + TypeScript + Tailwind         │
└─────────────────────────────────────────────┘
                    │
              HTTPS/JSON API
                    │
┌─────────────────────────────────────────────┐
│         Backend (FastAPI)                   │
│  ┌──────────┬──────────┬──────────────┐    │
│  │   Auth   │  Rooms   │ Reservations │    │
│  │  Guests  │ Payments │  Dashboard   │    │
│  └──────────┴──────────┴──────────────┘    │
└─────────────────────────────────────────────┘
                    │
              SQLAlchemy ORM
                    │
┌─────────────────────────────────────────────┐
│      Database (PostgreSQL/SQLite)           │
└─────────────────────────────────────────────┘
```

### Design Principles
1. **Keep It Simple**: No over-engineering
2. **API-First**: All logic accessible via REST API
3. **Mobile-Responsive**: Works on tablets/phones
4. **Role-Based**: Admin vs User permissions
5. **Type-Safe**: TypeScript frontend, Pydantic backend

---

## Technology Stack

### Backend
```
FastAPI (Python 3.11+)     - Modern, fast web framework
├── SQLAlchemy 2.x         - ORM for database
├── Alembic                - Database migrations
├── Pydantic v2            - Data validation
├── PyJWT                  - Authentication tokens
└── Passlib + Bcrypt       - Password hashing
```

**Database**:
- **Development**: SQLite (zero config)
- **Production**: PostgreSQL 14+ (Google Cloud SQL)

### Frontend
```
React 19 + TypeScript      - UI framework
├── Vite                   - Build tool (fast!)
├── Tailwind CSS           - Styling
├── Zustand                - State management
├── React Router v7        - Routing
├── Axios                  - HTTP client
└── react-i18next          - Internationalization
```

### Infrastructure
```
Frontend: Vercel           - Automatic deployments, CDN
Backend:  Google Cloud Run - Serverless containers
Database: Google Cloud SQL - Managed PostgreSQL
Monitoring: Sentry         - Error tracking
```

---

## Database Design

### Tables (6 total)

#### 1. users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100),
    role VARCHAR(10) NOT NULL CHECK(role IN ('admin', 'user')),
    status VARCHAR(10) DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
```

#### 2. room_types
```sql
CREATE TABLE room_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    base_capacity_adults INTEGER DEFAULT 2,
    base_capacity_children INTEGER DEFAULT 1,
    bed_config VARCHAR(50),
    default_rate DECIMAL(10,2) NOT NULL,
    amenities TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_room_types_code ON room_types(code);
```

#### 3. rooms
```sql
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY,
    room_number VARCHAR(10) UNIQUE NOT NULL,
    floor INTEGER,
    room_type_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'available'
        CHECK(status IN ('available', 'occupied', 'out_of_order')),
    view_type VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_type_id) REFERENCES room_types(id)
);

CREATE INDEX idx_rooms_number ON rooms(room_number);
CREATE INDEX idx_rooms_status ON rooms(status);
CREATE INDEX idx_rooms_type ON rooms(room_type_id);
```

#### 4. guests
```sql
CREATE TABLE guests (
    id INTEGER PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    id_type VARCHAR(50),
    id_number VARCHAR(50),
    nationality VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_guests_name ON guests(full_name);
CREATE INDEX idx_guests_email ON guests(email);
CREATE INDEX idx_guests_phone ON guests(phone);
```

#### 5. reservations
```sql
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY,
    confirmation_number VARCHAR(20) UNIQUE NOT NULL,
    guest_id INTEGER NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    room_type_id INTEGER NOT NULL,
    room_id INTEGER,
    adults INTEGER DEFAULT 1,
    children INTEGER DEFAULT 0,
    rate_per_night DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    special_requests TEXT,
    status VARCHAR(20) DEFAULT 'confirmed'
        CHECK(status IN ('confirmed', 'checked_in', 'checked_out', 'cancelled')),
    booking_source VARCHAR(20),
    created_by INTEGER NOT NULL,
    checked_in_at TIMESTAMP,
    checked_out_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES guests(id),
    FOREIGN KEY (room_type_id) REFERENCES room_types(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE INDEX idx_reservations_dates ON reservations(check_in_date, check_out_date);
CREATE INDEX idx_reservations_status ON reservations(status);
CREATE INDEX idx_reservations_guest ON reservations(guest_id);
CREATE INDEX idx_reservations_room ON reservations(room_id);
CREATE INDEX idx_reservations_confirmation ON reservations(confirmation_number);
```

#### 6. payments
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    reservation_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL
        CHECK(payment_method IN ('cash', 'credit_card', 'debit_card', 'bank_transfer', 'other')),
    reference_number VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id)
);

CREATE INDEX idx_payments_reservation ON payments(reservation_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
```

### Key Relationships
```
users (1) ──< (N) reservations (created_by)
room_types (1) ──< (N) rooms
room_types (1) ──< (N) reservations
rooms (1) ──< (N) reservations (optional FK)
guests (1) ──< (N) reservations
reservations (1) ──< (N) payments
```

---

## API Structure

### Base URL
`/api/v1`

### Endpoints (35 total)

#### Authentication (3 endpoints)
```
POST   /auth/login               - Login user
POST   /auth/logout              - Logout user
GET    /auth/me                  - Get current user
```

#### Users (5 endpoints) - Admin only
```
GET    /users                    - List all users
GET    /users/{id}               - Get user details
POST   /users                    - Create user
PUT    /users/{id}               - Update user
PUT    /users/{id}/status        - Activate/deactivate
```

#### Room Types (5 endpoints)
```
GET    /room-types               - List all room types
GET    /room-types/{id}          - Get room type details
POST   /room-types               - Create room type (admin)
PUT    /room-types/{id}          - Update room type (admin)
DELETE /room-types/{id}          - Delete room type (admin)
```

#### Rooms (6 endpoints)
```
GET    /rooms                    - List all rooms
GET    /rooms/{id}               - Get room details
POST   /rooms                    - Create room (admin)
PUT    /rooms/{id}               - Update room (admin)
DELETE /rooms/{id}               - Delete room (admin)
PUT    /rooms/{id}/status        - Update room status
GET    /rooms/availability       - Check availability
       ?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD&room_type_id=N
```

#### Guests (5 endpoints)
```
GET    /guests                   - List all guests
GET    /guests/{id}              - Get guest details
POST   /guests                   - Create guest
PUT    /guests/{id}              - Update guest
GET    /guests/{id}/reservations - Get guest reservation history
```

#### Reservations (9 endpoints)
```
GET    /reservations             - List all reservations
GET    /reservations/{id}        - Get reservation details
POST   /reservations             - Create reservation
PUT    /reservations/{id}        - Update reservation
DELETE /reservations/{id}        - Cancel reservation (admin)
POST   /reservations/{id}/check-in      - Check in guest
POST   /reservations/{id}/check-out     - Check out guest
PUT    /reservations/{id}/extend        - Extend stay
GET    /reservations/arrivals    - Today's arrivals
       ?date=YYYY-MM-DD
GET    /reservations/departures  - Today's departures
       ?date=YYYY-MM-DD
GET    /reservations/in-house    - Currently checked-in
```

#### Payments (5 endpoints)
```
GET    /payments                 - List payments
       ?reservation_id=N
GET    /payments/{id}            - Get payment details
POST   /payments                 - Record payment
PUT    /payments/{id}            - Update payment (admin)
DELETE /payments/{id}            - Delete payment (admin)
```

#### Dashboard (2 endpoints)
```
GET    /dashboard/metrics        - Key metrics
GET    /dashboard/summary        - Summary data
       ?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
```

---

## Frontend Structure

### Pages (9 pages)
```
/login              - LoginPage          - Authentication
/                   - DashboardPage      - Main dashboard
/rooms              - RoomsPage          - Room inventory list
/room-types         - RoomTypesPage      - Room type management
/guests             - GuestsPage         - Guest list
/reservations       - ReservationsPage   - Reservation list
/reservations/new   - NewReservationPage - Create booking
/check-in           - CheckInPage        - Arrivals today
/check-out          - CheckOutPage       - Departures today
```

### Components Structure
```
src/
├── pages/                  - Page components
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── RoomsPage.tsx
│   ├── RoomTypesPage.tsx
│   ├── GuestsPage.tsx
│   ├── ReservationsPage.tsx
│   ├── NewReservationPage.tsx
│   ├── CheckInPage.tsx
│   └── CheckOutPage.tsx
│
├── components/             - Shared components
│   ├── layout/
│   │   ├── Layout.tsx
│   │   ├── Navbar.tsx
│   │   └── Sidebar.tsx
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Modal.tsx
│   │   ├── Table.tsx
│   │   └── Badge.tsx
│   └── features/
│       ├── AvailabilitySearch.tsx
│       ├── GuestSelector.tsx
│       ├── RoomAssignment.tsx
│       └── PaymentForm.tsx
│
├── stores/                 - Zustand state
│   ├── authStore.ts
│   ├── roomStore.ts
│   ├── guestStore.ts
│   ├── reservationStore.ts
│   └── dashboardStore.ts
│
├── services/               - API client
│   └── api.ts
│
├── types/                  - TypeScript types
│   └── index.ts
│
├── i18n/                   - Translations
│   ├── en.json
│   └── id.json
│
└── App.tsx                 - Main app
```

### State Management (Zustand)
```typescript
// authStore
- user: User | null
- token: string | null
- login(username, password)
- logout()

// roomStore
- rooms: Room[]
- roomTypes: RoomType[]
- fetchRooms()
- fetchRoomTypes()

// guestStore
- guests: Guest[]
- fetchGuests()
- searchGuests(query)

// reservationStore
- reservations: Reservation[]
- fetchReservations()
- checkAvailability(checkIn, checkOut, roomTypeId)

// dashboardStore
- metrics: DashboardMetrics
- fetchMetrics()
```

---

## Development Roadmap

### Timeline: 10 Weeks

#### **Phase 1: Foundation (Week 1-2)**
**Backend**:
- [x] Project setup (FastAPI + SQLAlchemy)
- [ ] Database models (all 6 tables)
- [ ] Alembic migrations setup
- [ ] Authentication (JWT + roles)
- [ ] User CRUD endpoints

**Frontend**:
- [ ] Project setup (React + Vite + Tailwind)
- [ ] Auth store and login page
- [ ] Layout components (Navbar, Sidebar)
- [ ] API client setup
- [ ] Protected routes

**Deliverable**: Login system working end-to-end

---

#### **Phase 2: Room Management (Week 3)**
**Backend**:
- [ ] Room type CRUD endpoints
- [ ] Room CRUD endpoints
- [ ] Room status management
- [ ] Availability checking logic

**Frontend**:
- [ ] Room types page (admin only)
- [ ] Rooms page with status view
- [ ] Occupancy visualization
- [ ] Room type/room forms

**Deliverable**: Complete room inventory management

---

#### **Phase 3: Guest Management (Week 3)**
**Backend**:
- [ ] Guest CRUD endpoints
- [ ] Guest search functionality
- [ ] Guest reservation history

**Frontend**:
- [ ] Guests list page
- [ ] Guest search
- [ ] Guest form (create/edit)
- [ ] Guest detail view with history

**Deliverable**: Guest database functional

---

#### **Phase 4: Reservation System (Week 4-5)**
**Backend**:
- [ ] Reservation CRUD endpoints
- [ ] Availability search API
- [ ] Conflict detection logic
- [ ] Confirmation number generation
- [ ] Extend stay endpoint

**Frontend**:
- [ ] Availability search component
- [ ] New reservation page
- [ ] Reservation list with filters
- [ ] Reservation detail/edit
- [ ] Extend stay modal

**Deliverable**: Full reservation booking system

---

#### **Phase 5: Check-In/Out (Week 6)**
**Backend**:
- [ ] Check-in endpoint (update statuses)
- [ ] Check-out endpoint (update statuses)
- [ ] Arrivals/departures list endpoints
- [ ] In-house guests endpoint

**Frontend**:
- [ ] Check-in page (today's arrivals)
- [ ] Check-out page (today's departures)
- [ ] Room assignment during check-in
- [ ] Walk-in guest flow

**Deliverable**: Front desk operations complete

---

#### **Phase 6: Payments (Week 7)**
**Backend**:
- [ ] Payment CRUD endpoints
- [ ] Balance calculation logic
- [ ] Payment history per reservation

**Frontend**:
- [ ] Payment recording form
- [ ] Payment history display
- [ ] Balance indicator
- [ ] Payment during check-out

**Deliverable**: Payment tracking functional

---

#### **Phase 7: Dashboard (Week 8)**
**Backend**:
- [ ] Metrics calculation endpoint
- [ ] Summary data endpoint
- [ ] Aggregation queries

**Frontend**:
- [ ] Dashboard metrics cards
- [ ] Quick access links
- [ ] Date range selector
- [ ] Today's summary

**Deliverable**: Operational dashboard complete

---

#### **Phase 8: Polish & Testing (Week 9)**
- [ ] UI/UX refinement
- [ ] Mobile responsiveness
- [ ] Error handling
- [ ] Loading states
- [ ] Form validations
- [ ] Role permissions enforcement
- [ ] Integration testing

**Deliverable**: Production-ready UI

---

#### **Phase 9: Deployment (Week 10)**
- [ ] Database migration to PostgreSQL
- [ ] Environment configuration
- [ ] Backend deployment (Google Cloud Run)
- [ ] Frontend deployment (Vercel)
- [ ] User acceptance testing
- [ ] Documentation
- [ ] Training materials

**Deliverable**: System live in production

---

## Key Business Logic

### Availability Checking Algorithm
```python
def check_availability(check_in, check_out, room_type_id):
    """
    Room is available if:
    1. Has the requested room type
    2. NOT occupied during requested dates
    3. NOT out_of_order

    Overlap logic:
    Conflict exists if:
        check_in < existing.check_out AND
        check_out > existing.check_in
    """

    # Get all rooms of requested type
    rooms = Room.query.filter_by(
        room_type_id=room_type_id,
        status!='out_of_order'
    ).all()

    # For each room, check for conflicts
    available_rooms = []
    for room in rooms:
        has_conflict = Reservation.query.filter(
            Reservation.room_id == room.id,
            Reservation.status.in_(['confirmed', 'checked_in']),
            Reservation.check_in_date < check_out,
            Reservation.check_out_date > check_in
        ).first()

        if not has_conflict:
            available_rooms.append(room)

    return available_rooms
```

### Check-In Process
```python
def check_in(reservation_id, room_id):
    """
    1. Verify reservation status is 'confirmed'
    2. Assign room if not already assigned
    3. Update reservation status to 'checked_in'
    4. Update room status to 'occupied'
    5. Record check-in timestamp
    """
    reservation = get_reservation(reservation_id)

    if reservation.status != 'confirmed':
        raise ValueError("Reservation must be confirmed")

    if not reservation.room_id:
        reservation.room_id = room_id

    reservation.status = 'checked_in'
    reservation.checked_in_at = datetime.now()

    room = get_room(reservation.room_id)
    room.status = 'occupied'

    db.commit()
```

### Check-Out Process
```python
def check_out(reservation_id):
    """
    1. Verify reservation status is 'checked_in'
    2. Update reservation status to 'checked_out'
    3. Update room status to 'available'
    4. Record check-out timestamp
    """
    reservation = get_reservation(reservation_id)

    if reservation.status != 'checked_in':
        raise ValueError("Reservation must be checked in")

    reservation.status = 'checked_out'
    reservation.checked_out_at = datetime.now()

    room = get_room(reservation.room_id)
    room.status = 'available'

    db.commit()
```

---

## Migration from KOS System

### What We Keep
✅ Backend structure (FastAPI + SQLAlchemy)
✅ Frontend structure (React + Tailwind)
✅ Authentication framework (upgrade to roles)
✅ State management (Zustand)
✅ i18n setup

### What We Change
🔄 Database schema (6 new tables)
🔄 Room model (add room types)
🔄 Replace tenants → guests + reservations
🔄 Replace monthly payments → reservation payments
🔄 Dashboard metrics (hotel-specific)

### What We Remove
❌ Tenant management
❌ Monthly payment tracking
❌ Expense tracking
❌ Room history

---

## Success Criteria

### Technical
- [ ] Zero double-bookings (100% accuracy)
- [ ] All API endpoints functional
- [ ] All user roles enforced
- [ ] Dashboard loads < 3 seconds
- [ ] Mobile responsive

### Business
- [ ] Check-in process < 3 minutes
- [ ] Reservation creation < 2 minutes
- [ ] User training < 1 hour
- [ ] 99% uptime
- [ ] Zero data loss

---

## Next Steps

1. ✅ PRD approved
2. ✅ Project overview complete
3. ⏳ Start Phase 1: Backend setup
4. ⏳ Create initial database models
5. ⏳ Setup authentication system

---

**Document Status**: ✅ Ready for Development

**Start Here**: Phase 1 - Week 1 (Backend Setup)

---

**Last Updated**: November 7, 2025
**Version**: 1.0 (MVP)
