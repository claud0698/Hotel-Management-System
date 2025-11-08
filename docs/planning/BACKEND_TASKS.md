# Backend Development Tasks - Hotel Management System MVP v1.0

**Version**: 1.1
**Last Updated**: November 8, 2025
**Progress**: 45% Complete
**Estimated Timeline**: 3-4 weeks remaining (backend only)

---

## ⚡ Quick Summary - What's Done / What's Left

### ✅ COMPLETE (Phases 1-5)
- Phase 1: Database models, JWT (16h expiration), User management ✅
- Phase 2: Room types, Room CRUD, Availability checking ✅
- Phase 3: Guest CRUD, ID photo upload, Search ✅
- Phase 4: Reservation CRUD, Confirmation numbers, Filters ✅
- Phase 5: **Check-in (with receptionist tracking), Check-out, Arrivals/departures** ✅

### ⏳ REMAINING (Phases 6-9)
- **Phase 6: Payment Recording** (4 hours) - Record payments, balance calculation
- **Phase 7: Dashboard** (9 hours) - Metrics & summary
- **Phase 8: Testing** (15 hours) - API tests, validation, error handling
- **Phase 9: Deploy** (9 hours) - Alembic migrations, config, docs

---

## Current State Analysis - November 8, 2025

### ✅ COMPLETED - Production Ready

**Infrastructure** (100% Complete):
- ✅ FastAPI app with CORS, GZip, error handlers
- ✅ SQLite dev / PostgreSQL prod support
- ✅ Health check endpoint
- ✅ Swagger/OpenAPI at /api/docs

**Authentication** (100% Complete - JWT with Roles):
- ✅ JWT tokens (HS256) - **16-hour expiration** (shift-based)
- ✅ Role-based access control (admin/user)
- ✅ Password hashing (bcrypt)
- ✅ Token validation with expiration check

**Database Models** (100% Complete):
- ✅ User - role, full_name, status, password_hash
- ✅ RoomType - name, code, capacity, default_rate, amenities
- ✅ Room - room_number, floor, room_type_id, status, view_type
- ✅ Guest - full_name, id_type, id_number, email, phone, nationality
- ✅ GuestImage - guest photos with metadata
- ✅ Reservation - **with checked_in_by (receptionist tracking)**
- ✅ Payment - linked to reservations
- ✅ All relationships, indexes, and to_dict() methods

**API Endpoints Completed**:
- ✅ Phase 1: User management (admin only)
- ✅ Phase 2: Room types CRUD + Room CRUD + Availability checking
- ✅ Phase 3: Guest CRUD + Photo upload + Search
- ✅ Phase 4: Reservation CRUD + Confirmation numbers
- ✅ Phase 5: Check-in (with receptionist tracking) + Check-out + Arrivals/departures

---

## Database Migration Strategy

### Option 1: Fresh Start (Recommended for MVP)
- Create new database schema from scratch
- Keep existing database for reference
- Clean implementation without legacy constraints
- **Pros**: Clean, no migration complexity, faster
- **Cons**: Lose existing data (acceptable for MVP pivot)

### Option 2: Gradual Migration
- Keep User and Room tables
- Add new tables (RoomType, Guest, Reservation, Payment)
- Migrate data from old structure
- **Pros**: Preserve existing data
- **Cons**: Complex, migration scripts needed, more time

**Decision**: **Option 1 - Fresh Start** (recommended for MVP speed)

---

## Task Breakdown by Phase

---

## **PHASE 1: Foundation & Authentication (Week 1-2)**

### ✅ Task 1.1: Update Database Models
**Status**: ✅ COMPLETE
**Estimated Time**: 6 hours
**Priority**: High
**Completed**: November 8, 2025

**Changes Completed**:
- ✅ User model: role, full_name, status fields
- ✅ Room model: room_type_id FK, status values
- ✅ RoomType model: created with all fields
- ✅ Guest model: replaces Tenant with all fields
- ✅ Reservation model: **includes checked_in_by for receptionist tracking**
- ✅ GuestImage model: for ID photo storage
- ✅ Payment model: simplified for reservations
- ✅ Removed: Tenant, RoomHistory, Expense
- ✅ All relationships and indexes defined
- ✅ All models have to_dict() methods

**Files Modified**:
- `backend/models.py` ✅

---

### ✅ Task 1.2: Upgrade Authentication to JWT with Roles
**Status**: ✅ COMPLETE (with Enhancement)
**Estimated Time**: 4 hours
**Priority**: High
**Completed**: November 8, 2025

**Changes Completed**:
- ✅ JWT tokens (HS256) implemented
- ✅ Token includes user_id, username, role
- ✅ **Token expiration: 16 hours** (updated from 12h for flexibility)
- ✅ `create_access_token()` function
- ✅ `verify_token()` function with expiration check
- ✅ `get_current_user()` dependency injection
- ✅ In-memory token storage with expiration tracking

**Files Modified**:
- `backend/security.py` ✅

**Note**: Token expiration set to 16 hours to accommodate both standard (8-12h) and extended (up to 16h) shifts

### Task 1.3: Update User Routes with Role Management
   ```python
   async def require_admin(current_user: dict = Depends(get_current_user)):
       if current_user['role'] != 'admin':
           raise HTTPException(403, "Admin access required")
       return current_user
   ```

**Acceptance Criteria**:
- [ ] JWT tokens working with HS256 algorithm
- [ ] Tokens include user_id, username, role
- [ ] Token expiration enforced (24 hours)
- [ ] `require_admin` decorator working
- [ ] `require_auth` decorator working
- [ ] Login returns JWT token
- [ ] /auth/me returns user with role

**Files to Modify**:
- `backend/security.py`
- `backend/requirements.txt`

---

### Task 1.3: Update User Routes with Role Management
**Estimated Time**: 3 hours
**Priority**: High
**Dependencies**: Task 1.2

**Description**: Update user endpoints to support role management

**Changes Needed**:
1. Update `routes/users_router.py`:
   - Add role field to user creation
   - Add role field to user update
   - Add status field (active/inactive)
   - Add full_name field
   - All endpoints require `require_admin`
   - Prevent self-deletion

2. Update schemas (if using Pydantic):
   - UserCreate: username, password, email, full_name, role
   - UserUpdate: email, full_name, role, status
   - UserResponse: id, username, email, full_name, role, status

**Acceptance Criteria**:
- [ ] Admin can create users with role
- [ ] Admin can update user role and status
- [ ] Admin can list all users
- [ ] **Admin cannot delete self** (check if user_id == current_user.id, raise 403 Forbidden)
- [ ] Non-admin cannot access user routes
- [ ] User status (active/inactive) enforced

**Files to Modify**:
- `backend/routes/users_router.py`
- `backend/schemas.py` (if exists)

---

### Task 1.4: Update App Configuration
**Estimated Time**: 2 hours
**Priority**: High
**Dependencies**: Task 1.1

**Description**: Update app.py for hotel management system

**Changes Needed**:
1. Update `app.py`:
   - Change app title to "Hotel Management API"
   - Change description
   - Keep existing middleware
   - Remove tenant/expense routers
   - Add new routers (when created)

2. Update health check response

3. Update API root endpoint

**Acceptance Criteria**:
- [ ] App title/description updated
- [ ] Database tables created on startup
- [ ] Health check working
- [ ] API docs accessible at /api/docs

**Files to Modify**:
- `backend/app.py`

---

### Task 1.5: Create Database Initialization Script
**Estimated Time**: 2 hours
**Priority**: Medium
**Dependencies**: Task 1.1

**Description**: Script to create fresh database with initial data

**Create**: `backend/scripts/init_hotel_db.py`

**Features**:
1. Drop all existing tables (if exist)
2. Create all tables from models
3. Create default admin user
4. Create sample room types (2-3 types)
5. Create sample rooms (5-10 rooms)
6. Print summary

**Acceptance Criteria**:
- [ ] Script creates clean database
- [ ] Default admin user created (admin/admin123)
- [ ] Sample room types created
- [ ] Sample rooms created
- [ ] Script is idempotent (can run multiple times)

**Files to Create**:
- `backend/scripts/init_hotel_db.py`

---

## **PHASE 2: Room Management (Week 3)**

### Task 2.1: Room Type CRUD Endpoints
**Estimated Time**: 4 hours
**Priority**: High
**Dependencies**: Task 1.1

**Description**: Create room type management endpoints

**Create**: `backend/routes/room_types_router.py`

**Endpoints**:
- GET /api/room-types - List all (auth required)
- GET /api/room-types/{id} - Get one (auth required)
- POST /api/room-types - Create (admin only)
- PUT /api/room-types/{id} - Update (admin only)
- DELETE /api/room-types/{id} - Delete (admin only)

**Business Logic**:
- Cannot delete room type if rooms exist with that type
- Code must be unique
- Default rate must be positive

**Acceptance Criteria**:
- [ ] All 5 endpoints working
- [ ] Admin-only routes protected
- [ ] Cannot delete room type with rooms
- [ ] Unique code validation
- [ ] Proper error messages

**Files to Create**:
- `backend/routes/room_types_router.py`

**Files to Modify**:
- `backend/app.py` (include router)

---

### Task 2.2: Update Room Endpoints
**Estimated Time**: 4 hours
**Priority**: High
**Dependencies**: Task 2.1

**Description**: Update existing room routes for hotel system

**Modify**: `backend/routes/rooms_router.py`

**Changes**:
1. Update room model references
2. Add room_type_id to creation/update
3. Remove tenant-related logic
4. Update status values (available, occupied, out_of_order)
5. Add room status endpoint (PUT /rooms/{id}/status)
6. Add eager loading for room_type relationship

**Endpoints**:
- GET /api/rooms - List with filters (auth)
- GET /api/rooms/{id} - Get one (auth)
- POST /api/rooms - Create (admin only)
- PUT /api/rooms/{id} - Update (admin only)
- DELETE /api/rooms/{id} - Delete (admin only)
- PUT /api/rooms/{id}/status - Update status (admin only)

**Acceptance Criteria**:
- [ ] All endpoints updated
- [ ] Room type relationship loaded
- [ ] **Cannot delete room with active/confirmed reservations** (check room_id in reservations where status IN ('confirmed', 'checked_in'))
- [ ] Status values validated (available, occupied, out_of_order)
- [ ] Filters working (by floor, type, status)

**Files to Modify**:
- `backend/routes/rooms_router.py`

---

### Task 2.3: Availability Checking Endpoint
**Estimated Time**: 6 hours
**Priority**: High
**Dependencies**: Task 2.2

**Description**: Create availability checking logic

**Add to**: `backend/routes/rooms_router.py`

**Endpoint**:
- GET /api/rooms/availability?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD&room_type_id=N

**Logic**:
```python
# For each room of requested type:
# 1. Check if room is not out_of_order
# 2. Check for overlapping reservations:
#    - reservation.check_in < checkout AND
#    - reservation.check_out > checkin AND
#    - reservation.status IN ('confirmed', 'checked_in')
# 3. If no conflict, room is available
```

**Response**:
```json
{
  "check_in": "2025-12-01",
  "check_out": "2025-12-05",
  "nights": 4,
  "available_room_types": [
    {
      "room_type_id": 1,
      "name": "Standard Double",
      "available_count": 5,
      "default_rate": 500000,
      "available_rooms": [101, 102, 103]
    }
  ]
}
```

**Acceptance Criteria**:
- [ ] Correctly identifies available rooms
- [ ] No double-booking possible
- [ ] Handles edge cases (same-day check-in/out)
- [ ] Returns room type details
- [ ] Fast query (< 500ms for 200 rooms)

**Files to Modify**:
- `backend/routes/rooms_router.py`
- `backend/utils.py` (add availability logic)

---

## **PHASE 3: Guest Management (Week 3)**

### Task 3.1: Guest CRUD Endpoints
**Estimated Time**: 4 hours
**Priority**: High
**Dependencies**: Task 1.1

**Description**: Create guest management endpoints

**Create**: `backend/routes/guests_router.py`

**Endpoints**:
- GET /api/guests - List all with search (auth)
- GET /api/guests/{id} - Get one (auth)
- POST /api/guests - Create (auth)
- PUT /api/guests/{id} - Update (auth)
- GET /api/guests/{id}/reservations - Get guest history (auth)

**Features**:
- Search by name, email, phone (fuzzy matching)
- Pagination support
- Cannot delete guest (soft delete or prevent)

**Acceptance Criteria**:
- [ ] All endpoints working
- [ ] Search working (LIKE query on name, email, phone)
- [ ] Pagination working (skip/limit)
- [ ] Guest history returns reservations
- [ ] Both admin and user can create guests
- [ ] **Cannot delete guest with active/confirmed reservations** (optional: remove DELETE endpoint entirely or add validation)

**Files to Create**:
- `backend/routes/guests_router.py`

**Files to Modify**:
- `backend/app.py` (include router)

---

## **PHASE 4: Reservation System (Week 4-5)**

### Task 4.1: Reservation CRUD Endpoints
**Estimated Time**: 8 hours
**Priority**: Critical
**Dependencies**: Task 2.3, Task 3.1

**Description**: Create core reservation management

**Create**: `backend/routes/reservations_router.py`

**Endpoints**:
- GET /api/reservations - List with filters (auth)
- GET /api/reservations/{id} - Get one (auth)
- POST /api/reservations - Create with availability check (auth)
- PUT /api/reservations/{id} - Update (auth)
- DELETE /api/reservations/{id} - Cancel (admin only)

**Business Logic for POST**:
1. Validate guest exists
2. Validate room type exists
3. Check availability for dates
4. If room_id provided, verify it's available
5. Generate unique confirmation number
6. Calculate nights and total_amount
7. Create reservation with status='confirmed'
8. If room assigned, update room status

**Validation**:
- check_out must be after check_in
- adults >= 1
- rate_per_night > 0
- Prevent double-booking

**Acceptance Criteria**:
- [ ] Can create reservation without room assignment
- [ ] Can create reservation with room assignment
- [ ] Availability checked before creation
- [ ] Confirmation number is unique
- [ ] Total amount calculated correctly
- [ ] Cannot double-book
- [ ] User cannot delete (only admin can)

**Files to Create**:
- `backend/routes/reservations_router.py`

---

### Task 4.2: Confirmation Number Generator
**Estimated Time**: 2 hours
**Priority**: High
**Dependencies**: None

**Description**: Create unique confirmation number utility

**Add to**: `backend/utils.py`

**Format**: `HT-YYYYMMDD-XXXX`
- HT = Hotel
- YYYYMMDD = Date
- XXXX = Random 4-digit number or counter

**Features**:
- Guaranteed unique
- Readable
- Sortable by date

**Acceptance Criteria**:
- [ ] Generates unique numbers
- [ ] Format is readable
- [ ] No collisions

**Files to Modify**:
- `backend/utils.py`

---

### Task 4.3: Reservation List Filters
**Estimated Time**: 3 hours
**Priority**: Medium
**Dependencies**: Task 4.1

**Description**: Add comprehensive filtering to reservation list

**Filters**:
- By status (confirmed, checked_in, checked_out, cancelled)
- By date range (check_in, check_out)
- By guest_id
- By room_id
- By confirmation number (search)
- By guest name (search)

**Acceptance Criteria**:
- [ ] All filters working
- [ ] Can combine multiple filters
- [ ] **Search by confirmation number (exact match or LIKE query)**
- [ ] **Search by guest name (join guests table, LIKE query)**
- [ ] Pagination working

**Files to Modify**:
- `backend/routes/reservations_router.py`

---

### Task 4.4: Extend Stay Endpoint
**Estimated Time**: 4 hours
**Priority**: High
**Dependencies**: Task 4.1, Task 2.3

**Description**: Allow extending reservation dates

**Endpoint**:
- PUT /api/reservations/{id}/extend

**Request Body**:
```json
{
  "new_check_out_date": "2025-12-10"
}
```

**Logic**:
1. Verify reservation is confirmed or checked_in
2. Verify new date is after current check_out
3. Check room availability for extended period
4. Recalculate total_amount
5. Update reservation

**Acceptance Criteria**:
- [ ] Can extend checked-in reservations
- [ ] Cannot extend checked-out or cancelled
- [ ] Availability checked for extension
- [ ] Total recalculated correctly
- [ ] Cannot create conflicts

**Files to Modify**:
- `backend/routes/reservations_router.py`

---

## **PHASE 5: Check-In/Out Operations (Week 6)**

### Task 5.1: Check-In Endpoint
**Estimated Time**: 4 hours
**Priority**: Critical
**Dependencies**: Task 4.1

**Description**: Process guest check-in

**Endpoint**:
- POST /api/reservations/{id}/check-in

**Request Body**:
```json
{
  "room_id": 101  // Required if not already assigned
}
```

**Logic**:
1. Verify reservation status is 'confirmed'
2. Verify room is available (if provided)
3. Assign room if not already assigned
4. Update reservation.status = 'checked_in'
5. Update reservation.checked_in_at = now()
6. Update room.status = 'occupied'

**Acceptance Criteria**:
- [ ] Can check in with room assignment
- [ ] Cannot check in without room
- [ ] Room status updated to occupied
- [ ] Check-in timestamp recorded
- [ ] Cannot check in if already checked-in

**Files to Modify**:
- `backend/routes/reservations_router.py`

---

### Task 5.2: Check-Out Endpoint
**Estimated Time**: 4 hours
**Priority**: Critical
**Dependencies**: Task 5.1

**Description**: Process guest check-out

**Endpoint**:
- POST /api/reservations/{id}/check-out

**Logic**:
1. Verify reservation status is 'checked_in'
2. Update reservation.status = 'checked_out'
3. Update reservation.checked_out_at = now()
4. Update room.status = 'available'
5. Return balance info (total - paid)

**Response**:
```json
{
  "reservation_id": 123,
  "status": "checked_out",
  "checked_out_at": "2025-11-07T14:30:00Z",
  "total_amount": 2000000,
  "total_paid": 1500000,
  "balance": 500000
}
```

**Acceptance Criteria**:
- [ ] Can check out checked-in guest
- [ ] Room status updated to available
- [ ] Check-out timestamp recorded
- [ ] Balance calculated correctly
- [ ] Cannot check out if not checked-in

**Files to Modify**:
- `backend/routes/reservations_router.py`

---

### Task 5.3: Arrivals/Departures Endpoints
**Estimated Time**: 3 hours
**Priority**: High
**Dependencies**: Task 4.1

**Description**: Get today's arrivals and departures

**Endpoints**:
- GET /api/reservations/arrivals?date=YYYY-MM-DD (defaults to today)
- GET /api/reservations/departures?date=YYYY-MM-DD
- GET /api/reservations/in-house

**Logic**:
- Arrivals: reservations where check_in_date = date AND status = 'confirmed'
- Departures: reservations where check_out_date = date AND status = 'checked_in'
- In-house: reservations where status = 'checked_in'

**Acceptance Criteria**:
- [ ] Arrivals list shows today's expected arrivals
- [ ] Departures list shows today's expected departures
- [ ] In-house list shows all checked-in guests
- [ ] All include guest and room details
- [ ] Eager loading to prevent N+1 queries

**Files to Modify**:
- `backend/routes/reservations_router.py`

---

## **PHASE 6: Payment Tracking (Week 7)**

### Task 6.1: Payment CRUD Endpoints
**Estimated Time**: 4 hours
**Priority**: High
**Dependencies**: Task 4.1

**Description**: Simple payment recording

**Create**: `backend/routes/payments_router.py`

**Endpoints**:
- GET /api/payments?reservation_id=N - List payments (auth)
- GET /api/payments/{id} - Get one (auth)
- POST /api/payments - Create (auth)
- PUT /api/payments/{id} - Update (admin only)
- DELETE /api/payments/{id} - Delete (admin only)

**Business Logic**:
- Payments linked to reservations
- No validation of total (can overpay or underpay)
- Just track: date, amount, method, reference

**Acceptance Criteria**:
- [ ] Can record payment against reservation
- [ ] Multiple payments per reservation allowed
- [ ] User can create, admin can edit/delete
- [ ] Payment methods validated

**Files to Create**:
- `backend/routes/payments_router.py`

**Files to Modify**:
- `backend/app.py` (include router)

---

### Task 6.2: Balance Calculation Utility
**Estimated Time**: 2 hours
**Priority**: Medium
**Dependencies**: Task 6.1

**Description**: Calculate reservation balance

**Add to**: `backend/utils.py` or `backend/routes/reservations_router.py`

**Function**:
```python
def calculate_balance(reservation_id, db):
    reservation = get_reservation(reservation_id)
    payments = get_payments_for_reservation(reservation_id)

    total_paid = sum(p.amount for p in payments)
    balance = reservation.total_amount - total_paid

    return {
        'total_amount': reservation.total_amount,
        'total_paid': total_paid,
        'balance': balance,
        'status': 'paid' if balance <= 0 else 'partial' if total_paid > 0 else 'unpaid'
    }
```

**Acceptance Criteria**:
- [ ] Correctly calculates balance
- [ ] Returns payment status
- [ ] Fast query

**Files to Modify**:
- `backend/utils.py`

---

## **PHASE 7: Dashboard (Week 8)**

### Task 7.1: Dashboard Metrics Endpoint
**Estimated Time**: 5 hours
**Priority**: High
**Dependencies**: All previous tasks

**Description**: Real-time operational metrics

**Update**: `backend/routes/dashboard_router.py`

**Endpoint**:
- GET /api/dashboard/metrics

**Metrics**:
```json
{
  "date": "2025-11-07",
  "arrivals_today": 5,
  "departures_today": 3,
  "in_house": 45,
  "available_rooms": 15,
  "total_rooms": 60,
  "occupancy_rate": 75.0,
  "rooms_by_status": {
    "available": 15,
    "occupied": 45,
    "out_of_order": 0
  }
}
```

**Logic**:
- Count reservations where check_in_date = today AND status = 'confirmed'
- Count reservations where check_out_date = today AND status = 'checked_in'
- Count reservations where status = 'checked_in'
- Count rooms by status
- Calculate occupancy = (occupied / total) * 100

**Acceptance Criteria**:
- [ ] All metrics calculated correctly
- [ ] Fast query (< 500ms)
- [ ] Returns accurate data

**Files to Modify**:
- `backend/routes/dashboard_router.py`

---

### Task 7.2: Dashboard Summary Endpoint
**Estimated Time**: 4 hours
**Priority**: Medium
**Dependencies**: Task 7.1, Task 6.1

**Description**: Revenue and payment summary

**Endpoint**:
- GET /api/dashboard/summary?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD

**Data**:
```json
{
  "date_from": "2025-11-01",
  "date_to": "2025-11-30",
  "total_revenue": 50000000,
  "total_payments": 45000000,
  "outstanding_balance": 5000000,
  "reservations_count": 100,
  "new_guests": 30
}
```

**Logic**:
- Sum reservation.total_amount where created_at in range
- Sum payments.amount where payment_date in range
- Calculate outstanding balance
- Count reservations created in range
- Count new guests created in range

**Acceptance Criteria**:
- [ ] Calculates revenue correctly
- [ ] Calculates payments correctly
- [ ] Date range filtering working
- [ ] Defaults to current month

**Files to Modify**:
- `backend/routes/dashboard_router.py`

---

## **PHASE 8: Testing & Refinement (Week 9)**

### Task 8.1: Create API Tests
**Estimated Time**: 8 hours
**Priority**: High
**Dependencies**: All previous tasks

**Description**: Pytest tests for key endpoints

**Create**: `backend/tests/`

**Test Files**:
- `test_auth.py` - Login, token, permissions
- `test_rooms.py` - Room CRUD, availability
- `test_guests.py` - Guest CRUD, search
- `test_reservations.py` - Booking, check-in/out, conflicts
- `test_payments.py` - Payment recording, balance

**Key Test Cases**:
- [ ] Authentication and roles
- [ ] Room availability algorithm
- [ ] Double-booking prevention
- [ ] Check-in/out workflow
- [ ] Balance calculation
- [ ] Permission enforcement

**Files to Create**:
- `backend/tests/test_*.py`
- `backend/conftest.py` (pytest fixtures)

---

### Task 8.2: Add Input Validation
**Estimated Time**: 4 hours
**Priority**: High
**Dependencies**: All route tasks

**Description**: Comprehensive Pydantic schemas

**Update**: `backend/schemas.py`

**Schemas Needed**:
- UserCreate, UserUpdate, UserResponse
- RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse
- RoomCreate, RoomUpdate, RoomResponse
- GuestCreate, GuestUpdate, GuestResponse
- ReservationCreate, ReservationUpdate, ReservationResponse
- PaymentCreate, PaymentUpdate, PaymentResponse

**Validation**:
- Required fields
- Data types
- String lengths
- Date formats
- Enum values
- Custom validators

**Acceptance Criteria**:
- [ ] All endpoints use Pydantic schemas
- [ ] Validation errors are clear
- [ ] Invalid data rejected with 422

**Files to Modify**:
- `backend/schemas.py`
- All router files

---

### Task 8.3: Error Handling & Logging
**Estimated Time**: 3 hours
**Priority**: Medium
**Dependencies**: None

**Description**: Improve error handling and add logging

**Changes**:
1. Add structured logging (loguru or stdlib)
2. Log all errors with context
3. Consistent error response format
4. Handle edge cases gracefully

**Acceptance Criteria**:
- [ ] All errors logged with details
- [ ] Consistent error JSON format
- [ ] No stack traces in production
- [ ] 400, 401, 403, 404, 422, 500 handled

**Files to Modify**:
- `backend/app.py`
- All router files

---

## **PHASE 9: Documentation & Deployment (Week 10)**

### Task 9.1: Update API Documentation
**Estimated Time**: 3 hours
**Priority**: Medium
**Dependencies**: All previous tasks

**Description**: Complete OpenAPI docs

**Changes**:
1. Add descriptions to all endpoints
2. Add example requests/responses
3. Document query parameters
4. Document error responses
5. Add tags and grouping

**Acceptance Criteria**:
- [ ] All endpoints documented
- [ ] Examples provided
- [ ] Swagger UI looks professional
- [ ] Easy to understand for frontend dev

**Files to Modify**:
- All router files (add docstrings)

---

### Task 9.2: Environment Configuration
**Estimated Time**: 2 hours
**Priority**: High
**Dependencies**: None

**Description**: Production-ready environment setup

**Create/Update**:
- `.env.example` - Template with all variables
- `backend/config.py` - Centralized config management

**Environment Variables**:
```
# Database
DATABASE_URL=postgresql://...

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# CORS
CORS_ORIGINS=https://yourdomain.com

# App
DEBUG=False
LOG_LEVEL=INFO
```

**Acceptance Criteria**:
- [ ] All config in environment variables
- [ ] .env.example complete
- [ ] Secrets not in code
- [ ] Different configs for dev/prod

**Files to Create**:
- `.env.example`
- `backend/config.py`

---

### Task 9.3: Database Migrations with Alembic
**Estimated Time**: 4 hours
**Priority**: High
**Dependencies**: Task 1.1

**Description**: Setup Alembic for database migrations

**Steps**:
1. Install Alembic
2. Initialize Alembic: `alembic init alembic`
3. Configure `alembic.ini`
4. Update `alembic/env.py` to use models
5. Create initial migration: `alembic revision --autogenerate -m "initial"`
6. Test migrations up/down

**Acceptance Criteria**:
- [ ] Alembic configured correctly
- [ ] Initial migration created
- [ ] Can upgrade/downgrade
- [ ] Works with both SQLite and PostgreSQL

**Files to Create**:
- `backend/alembic/` (directory)
- `backend/alembic.ini`

---

## Summary

### Total Estimated Time: **85 hours (~10-11 weeks at 8 hours/week or 6-7 weeks full-time)**

### Task Count: **30 tasks**

### Critical Path:
1. Phase 1: Foundation (Week 1-2)
2. Phase 2-3: Rooms & Guests (Week 3)
3. Phase 4: Reservations (Week 4-5) ← Most complex
4. Phase 5: Check-in/out (Week 6)
5. Phase 6: Payments (Week 7)
6. Phase 7: Dashboard (Week 8)
7. Phase 8-9: Testing & Deploy (Week 9-10)

### Priority Distribution:
- **Critical**: 3 tasks (Check-in, Check-out, Reservations)
- **High**: 19 tasks
- **Medium**: 8 tasks

---

## Quick Start Checklist

Ready to start development? Follow this order:

**Week 1:**
- [ ] Task 1.1: Update database models
- [ ] Task 1.2: JWT authentication with roles
- [ ] Task 1.3: User routes with roles
- [ ] Task 1.4: Update app configuration
- [ ] Task 1.5: Database init script

**Week 2:**
- [ ] Task 2.1: Room type endpoints
- [ ] Task 2.2: Update room endpoints
- [ ] Task 2.3: Availability checking
- [ ] Task 3.1: Guest endpoints

**Week 3-4:**
- [ ] Task 4.1: Reservation CRUD
- [ ] Task 4.2: Confirmation numbers
- [ ] Task 4.3: Reservation filters
- [ ] Task 4.4: Extend stay

**Week 5:**
- [ ] Task 5.1: Check-in
- [ ] Task 5.2: Check-out
- [ ] Task 5.3: Arrivals/departures

**Week 6:**
- [ ] Task 6.1: Payment endpoints
- [ ] Task 6.2: Balance calculation
- [ ] Task 7.1: Dashboard metrics
- [ ] Task 7.2: Dashboard summary

**Week 7:**
- [ ] Task 8.1: API tests
- [ ] Task 8.2: Input validation
- [ ] Task 8.3: Error handling

**Week 8:**
- [ ] Task 9.1: API documentation
- [ ] Task 9.2: Environment config
- [ ] Task 9.3: Alembic migrations

---

## Dependencies

### New Python Packages Needed:
```
PyJWT>=2.8.0          # JWT tokens
python-multipart      # File uploads (future)
pytest>=7.4.0         # Testing
pytest-asyncio        # Async tests
alembic>=1.12.0       # Database migrations
```

### Already Have:
```
fastapi
sqlalchemy
passlib[bcrypt]
python-dotenv
uvicorn
psycopg2-binary       # PostgreSQL driver
```

---

## Next Steps

1. **Review this document** and adjust estimates/priorities
2. **Start with Task 1.1** (Update models)
3. **Work sequentially** through Phase 1
4. **Test frequently** after each task
5. **Commit often** with clear messages

**Ready to code?** Start with Phase 1, Task 1.1! 🚀
