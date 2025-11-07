# Product Requirements Document (PRD)
## Hotel Management System - MVP v1.0

**Version**: 1.0 (MVP)
**Last Updated**: November 7, 2025
**Status**: Planning Phase
**Previous System**: KOS Management Dashboard

---

## 1. Executive Summary

The **Hotel Management System (HMS)** is a web-based property management solution designed for small to mid-size hotels. Version 1.0 focuses on core operational features needed to manage daily hotel operations efficiently.

### Business Problem
Hotel operators currently struggle with:
- Managing room inventory and availability manually
- Tracking reservations and preventing double-bookings
- Coordinating guest check-in/check-out processes
- Recording guest information and payment details
- Generating basic operational reports

### Solution Overview - MVP v1.0
A streamlined hotel operations platform that provides:
- Room inventory management with room types
- Reservation booking with availability checking
- Guest profile management
- Check-in/check-out operations
- Simple payment recording
- Basic operational dashboard
- Two-tier user access (Admin + User roles)

### What's NOT in v1.0 (Deferred to v2.0)
- Advanced housekeeping module
- Maintenance tracking
- Complex rate management (yield management, seasonal pricing)
- Invoice generation and accounting
- Email/SMS notifications
- Online booking engine
- Reporting exports (PDF/Excel)
- Multi-property support

---

## 2. Product Vision & Goals

### Vision Statement
"Enable hotel operators to efficiently manage reservations, guests, and rooms through a simple, reliable system."

### Business Goals (v1.0)
1. **Eliminate Double-Bookings**: 100% accuracy in room availability
2. **Streamline Check-In/Out**: Reduce process time by 70%
3. **Centralize Guest Data**: Single source of truth for guest information
4. **Operational Visibility**: Real-time view of occupancy and reservations

### Success Metrics
- Reservation creation in < 2 minutes
- Check-in/check-out in < 3 minutes
- Zero double-booking incidents
- System uptime: 99%
- Dashboard loads in < 3 seconds

---

## 3. Target Users

### Primary Users

#### 1. Admin User
- **Full system access**
- **Responsibilities**:
  - Manage all reservations and guests
  - Configure room inventory
  - View dashboard and reports
  - Manage user accounts
  - Edit and delete all data
  - Record payments

#### 2. User (Staff)
- **Limited access**
- **Responsibilities**:
  - Create and view reservations
  - Check-in/check-out guests
  - View guest information
  - Record check-ins
  - **Cannot delete** reservations or data
  - View dashboard (read-only)

### User Role Matrix (v1.0)
| Feature | Admin | User |
|---------|-------|------|
| Dashboard | Full access | Read-only |
| Reservations | CRUD | Create, Read, Update (no delete) |
| Check-in/Check-out | Full | Full |
| Guests | CRUD | Create, Read, Update |
| Rooms/Room Types | CRUD | Read-only |
| Payments | CRUD | Create, Read |
| Users | CRUD | Cannot access |

---

## 4. Core Features (v1.0 MVP)

### 4.1 Authentication & User Management

#### Feature: Two-Tier Authentication
- **Description**: Simple role-based access with Admin and User roles

**User Roles**:
- `admin`: Full system access, can edit/delete everything, manage users
- `user`: Limited access, can create/update but not delete, no user management

**Acceptance Criteria**:
- Users login with username/password
- JWT token authentication
- Session persists for 24 hours
- Password hashed with bcrypt
- Role determines menu visibility and permissions
- Logout clears session

#### Feature: User Management (Admin Only)
**Acceptance Criteria**:
- Admin can create user accounts
- Admin assigns role (admin or user)
- Admin can activate/deactivate users
- Users cannot access user management
- **Cannot delete own account while logged in** (security: prevents accidental lockout)

---

### 4.2 Room Inventory Management

#### Feature: Room Type Management
**Description**: Define categories of rooms (Standard, Deluxe, Suite, etc.)

**Room Type Attributes**:
- Name (e.g., "Standard Double")
- Code (e.g., "STD")
- Base capacity (adults + children)
- Bed configuration (e.g., "1 King" or "2 Queens")
- Default daily rate
- Amenities (text field)

**Acceptance Criteria**:
- Admin can create/edit/delete room types
- Room types display in room management
- Default rate pre-fills when creating reservations
- Cannot delete room type if rooms exist with that type

#### Feature: Room Management
**Description**: Individual room inventory

**Room Attributes**:
- Room number (unique, required)
- Floor number
- Room type (FK to room types)
- Status (available, occupied, out_of_order)
- View type (city, garden, ocean, etc.) - optional
- Notes (optional)

**Acceptance Criteria**:
- Admin can create/edit/delete rooms
- Room number must be unique
- Status updates automatically on check-in/check-out
- Can manually change status to out_of_order
- **Cannot delete room if it has active/confirmed reservations** (prevents data integrity issues)
- Bulk room creation (optional: create multiple rooms at once)

#### Feature: Room Availability View
**Acceptance Criteria**:
- Display all rooms with current status
- Color-coded: Green (available), Blue (occupied), Red (out of order)
- Filter by floor, room type, status
- Click room to view details
- Show occupancy percentage

---

### 4.3 Guest Management

#### Feature: Guest Profile System
**Description**: Maintain guest database

**Guest Data**:
- Full name (required)
- Email
- Phone number
- ID document type (Passport, Driver's License, etc.)
- ID document number
- Nationality
- Notes (special requests, preferences)

**Acceptance Criteria**:
- Create guest profile during reservation or separately
- Search guests by name, email, or phone
- View guest reservation history
- Edit guest information
- Merge duplicate guests (admin only)
- **Cannot delete guest with active/confirmed reservations** (prevents data integrity issues)

---

### 4.4 Reservation Management

#### Feature: Reservation Creation
**Description**: Book rooms with availability checking

**Reservation Data**:
- Guest (FK to guests table)
- Check-in date (arrival)
- Check-out date (departure)
- Room type requested
- Room number (assigned now or later)
- Number of adults
- Number of children
- Rate per night
- Total amount (auto-calculated: nights × rate)
- Special requests
- Status (confirmed, checked_in, checked_out, cancelled)
- Booking source (walk-in, phone, email, other)
- Created by (user who made reservation)

**Acceptance Criteria**:
- Search available rooms by date range and room type
- System prevents double-booking (conflict detection)
- Auto-calculate total based on nights and rate
- Can create reservation without assigning specific room
- Can assign specific room during creation or later
- Generate unique confirmation number
- Special requests field for guest notes

#### Feature: Availability Checking
**Description**: Real-time room availability

**Logic**:
- Room is available if NOT occupied during requested dates
- Check overlapping reservations:
  - NOT (check-in < existing.check-out AND check-out > existing.check-in)
- Exclude cancelled reservations
- Exclude checked-out reservations
- Include out_of_order rooms in unavailable count

**Acceptance Criteria**:
- Availability search by date range
- Show available rooms by type
- Display total available vs total rooms
- Real-time updates after booking
- Visual calendar view (optional for v1.0)

#### Feature: Reservation Management
**Acceptance Criteria**:
- View all reservations (list and calendar views)
- Filter by status, date range, room type
- **Search by guest name or confirmation number** (critical for front desk operations)
- Edit reservation details (dates, room, rate)
- Cancel reservation (changes status, frees room)
- Extend stay (update check-out date, recalculate total)
- View upcoming arrivals (check-ins today/tomorrow)
- View upcoming departures (check-outs today/tomorrow)

#### Feature: Conflict Detection
**Acceptance Criteria**:
- Prevent double-booking same room for overlapping dates
- Show warning if trying to book unavailable room
- Suggest alternative rooms if conflict exists
- Admin can override (with warning confirmation)

---

### 4.5 Front Desk Operations

#### Feature: Check-In Process
**Description**: Guest arrival and room assignment

**Check-In Steps**:
1. Search reservation (by confirmation number or guest name)
2. Verify guest details
3. Assign room (if not already assigned)
4. Confirm payment method
5. Update status to "checked_in"
6. Update room status to "occupied"

**Acceptance Criteria**:
- Today's arrivals list (reservations with check-in = today)
- Search reservation by confirmation or guest
- Assign room from available rooms
- Cannot check-in without room assignment
- Room status auto-updates to occupied
- Reservation status changes to checked_in
- Record check-in time (timestamp)
- Walk-in guests: staff manually creates new reservation with today's dates, then immediately checks in using normal check-in flow (no special walk-in workflow needed)

#### Feature: Check-Out Process
**Description**: Guest departure

**Check-Out Steps**:
1. Find reservation (by room number or guest name)
2. Review charges (simple payment list)
3. Record final payment
4. Update status to "checked_out"
5. Update room status to "available"

**Acceptance Criteria**:
- Today's departures list (reservations with check-out = today)
- Search by room number or guest name
- View total charges and payments
- Record checkout payment
- Room status auto-updates to available
- Reservation status changes to checked_out
- Record check-out time (timestamp)
- Late checkout handling (manual date extension)

#### Feature: In-House Guests
**Acceptance Criteria**:
- List currently checked-in guests
- Show room number, guest name, check-out date
- Filter/sort by room, name, or checkout date
- Quick access to extend stay
- Quick access to early checkout

---

### 4.6 Billing & Payments (Simple)

#### Feature: Payment Recording
**Description**: Simple payment tracking per reservation

**Payment Data**:
- Reservation (FK)
- Payment date
- Amount
- Payment method (Cash, Credit Card, Debit Card, Bank Transfer, Other)
- Reference number (optional, for card/transfer)
- Notes

**Acceptance Criteria**:
- Record payments against reservations
- View payment history per reservation
- Calculate total paid vs total amount due
- Show balance (total amount - total paid)
- Multiple payments per reservation allowed
- Cannot delete payments (admin can void/edit)

#### Feature: Simple Balance Tracking
**Acceptance Criteria**:
- Show reservation total amount
- Show total payments received
- Calculate and display balance
- Color-code: Green (fully paid), Yellow (partial), Red (unpaid)
- Dashboard shows total outstanding balances

**Note**: No invoicing, no itemized charges, no tax calculations in v1.0. Just track room rate and payments.

---

### 4.7 Dashboard & Reporting (Basic)

#### Feature: Operations Dashboard
**Description**: Real-time operational metrics

**Dashboard Sections**:

1. **Today's Summary**
   - Arrivals today (count)
   - Departures today (count)
   - In-house guests (count)
   - Available rooms (count)

2. **Occupancy Metrics**
   - Current occupancy rate (%)
   - Occupied rooms / Total rooms
   - Rooms by status (available, occupied, out of order)

3. **Revenue Summary (Simple)**
   - Total revenue this month
   - Total payments received this month
   - Outstanding balance

4. **Upcoming**
   - Next 7 days arrivals (count by day)
   - Next 7 days departures (count by day)

5. **Quick Access**
   - Today's arrivals list (clickable)
   - Today's departures list (clickable)
   - In-house guests list (clickable)

**Acceptance Criteria**:
- Dashboard loads in < 3 seconds
- Real-time data (no caching for v1.0)
- Date range selector (This Month, Last Month, Custom)
- Click metrics to view detailed lists
- Responsive design for tablets

**Note**: No charts, no exports, no advanced analytics in v1.0.

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Dashboard loads in < 3 seconds
- Reservation search returns in < 1 second
- API responses < 500ms
- Support up to 200 rooms
- Support up to 50 concurrent users

### 5.2 Security
- JWT token authentication
- Password hashing (bcrypt, cost 12)
- Role-based access control (admin/user)
- HTTPS in production
- SQL injection prevention (parameterized queries)
- XSS protection (React auto-escaping)

### 5.3 Reliability
- 99% uptime target
- Daily automated backups
- Data validation on all inputs
- Graceful error handling

### 5.4 Usability
- Intuitive interface (< 1 hour training)
- Mobile-responsive design
- Clear error messages
- Loading indicators for all async operations
- Multi-language support (English, Indonesian)

### 5.5 Maintainability
- Clean, documented code
- Modular architecture
- API documentation (Swagger/OpenAPI)
- Database migration support (Alembic)

---

## 6. Technical Architecture

### 6.1 Technology Stack

**Backend**:
- FastAPI (Python 3.11+)
- SQLAlchemy 2.x ORM
- PostgreSQL (production) / SQLite (development)
- PyJWT for authentication
- Pydantic for validation
- Alembic for migrations

**Frontend**:
- React 19 + TypeScript
- Vite (build tool)
- Tailwind CSS
- Zustand (state management)
- React Router v7
- Axios (HTTP client)
- react-i18next (internationalization)

**Infrastructure**:
- Frontend: Vercel
- Backend: Google Cloud Run
- Database: Google Cloud SQL (PostgreSQL)
- Monitoring: Sentry

### 6.2 Database Schema (v1.0)

#### users
```sql
id (PK), username (unique), password_hash, email, full_name,
role (admin/user), status (active/inactive),
created_at, updated_at
```

#### room_types
```sql
id (PK), name, code (unique), base_capacity_adults,
base_capacity_children, bed_config, default_rate, amenities,
created_at, updated_at
```

#### rooms
```sql
id (PK), room_number (unique), floor, room_type_id (FK),
status (available/occupied/out_of_order), view_type, notes,
created_at, updated_at
```

#### guests
```sql
id (PK), full_name, email, phone, id_type, id_number,
nationality, notes,
created_at, updated_at
```

#### reservations
```sql
id (PK), confirmation_number (unique), guest_id (FK),
check_in_date, check_out_date, room_type_id (FK), room_id (FK, nullable),
adults, children, rate_per_night, total_amount,
special_requests, status (confirmed/checked_in/checked_out/cancelled),
booking_source, created_by (FK to users),
checked_in_at, checked_out_at,
created_at, updated_at
```

#### payments
```sql
id (PK), reservation_id (FK), payment_date, amount,
payment_method, reference_number, notes,
created_at, updated_at
```

**Indexes**:
- reservations: (check_in_date, check_out_date), (status), (guest_id), (room_id)
- rooms: (status), (room_type_id), (room_number)
- guests: (email), (phone), (full_name)
- users: (username)

### 6.3 API Endpoints (v1.0)

**Base URL**: `/api/v1`

**Authentication**
- POST /auth/login
- POST /auth/logout
- GET /auth/me

**Users** (Admin only)
- GET /users
- GET /users/{id}
- POST /users
- PUT /users/{id}
- PUT /users/{id}/status (activate/deactivate)

**Room Types**
- GET /room-types
- GET /room-types/{id}
- POST /room-types (admin only)
- PUT /room-types/{id} (admin only)
- DELETE /room-types/{id} (admin only)

**Rooms**
- GET /rooms
- GET /rooms/{id}
- POST /rooms (admin only)
- PUT /rooms/{id} (admin only)
- DELETE /rooms/{id} (admin only)
- PUT /rooms/{id}/status
- GET /rooms/availability?check_in=date&check_out=date&room_type_id=id

**Guests**
- GET /guests
- GET /guests/{id}
- POST /guests
- PUT /guests/{id}
- GET /guests/{id}/reservations

**Reservations**
- GET /reservations
- GET /reservations/{id}
- POST /reservations
- PUT /reservations/{id}
- DELETE /reservations/{id} (admin only - soft delete/cancel)
- POST /reservations/{id}/check-in
- POST /reservations/{id}/check-out
- PUT /reservations/{id}/extend
- GET /reservations/arrivals?date=today
- GET /reservations/departures?date=today
- GET /reservations/in-house

**Payments**
- GET /payments?reservation_id={id}
- GET /payments/{id}
- POST /payments
- PUT /payments/{id} (admin only)
- DELETE /payments/{id} (admin only)

**Dashboard**
- GET /dashboard/metrics
- GET /dashboard/summary?date_from=date&date_to=date

---

## 7. User Flows

### 7.1 Create Reservation (Walk-In Guest)
1. User clicks "New Reservation"
2. User searches for existing guest OR creates new guest
3. User selects check-in and check-out dates
4. System shows available room types
5. User selects room type
6. User enters number of adults/children
7. System shows default rate (editable)
8. User optionally assigns specific room
9. User adds special requests (optional)
10. System generates confirmation number
11. Reservation created with status "confirmed"

### 7.2 Check-In Guest
1. User views "Arrivals Today" list
2. User selects reservation
3. System displays guest details
4. User assigns room (if not already assigned)
5. User confirms details
6. User clicks "Check In"
7. System updates:
   - Reservation status → checked_in
   - Room status → occupied
   - Records check-in timestamp
8. Optional: User records deposit/payment

### 7.3 Check-Out Guest
1. User views "Departures Today" list or searches by room
2. User selects reservation
3. System shows:
   - Guest details
   - Total amount
   - Payments made
   - Balance due
4. User records final payment (if needed)
5. User clicks "Check Out"
6. System updates:
   - Reservation status → checked_out
   - Room status → available
   - Records check-out timestamp

### 7.4 Extend Stay
1. User finds in-house guest
2. User clicks "Extend Stay"
3. User enters new check-out date
4. System checks room availability for extension period
5. If available, system recalculates total amount
6. System updates reservation

---

## 8. Migration from KOS System

### 8.1 Reusable Components
- ✅ Authentication framework (upgrade to JWT with roles)
- ✅ Room management structure (extend with room types)
- ✅ Database infrastructure (SQLAlchemy)
- ✅ Frontend component structure (React + Tailwind)
- ✅ State management (Zustand)
- ✅ i18n setup (react-i18next)

### 8.2 New Components to Build
- Room types management
- Guest profiles (replace tenant)
- Reservation system with availability checking
- Check-in/check-out workflows
- Simple payment tracking (replace complex payment system)
- Updated dashboard for hotel metrics

### 8.3 Components to Remove
- Tenant management (replaced by guests + reservations)
- Monthly payment tracking (replaced by simple payments)
- Expense tracking (deferred to v2.0)
- Room history tracking (deferred to v2.0)

---

## 9. Out of Scope (v2.0+)

### Deferred to v2.0
- **Housekeeping Module**: Task assignments, room status tracking
- **Maintenance Tracking**: Work orders, maintenance requests
- **Advanced Rate Management**: Yield management, seasonal pricing, multiple rate plans
- **Invoicing System**: Itemized invoices, tax calculations, invoice templates
- **Email/SMS Notifications**: Booking confirmations, reminders
- **Advanced Reporting**: Custom reports, PDF/Excel exports, charts
- **Channel Management**: OTA integrations
- **Online Booking Engine**: Customer-facing booking
- **Payment Gateway**: Automatic card processing
- **Multi-property**: Support multiple hotels

### Deferred to v3.0+
- Mobile apps (staff + guest)
- Advanced analytics and BI
- Loyalty program
- AI-powered pricing
- POS integration
- Event management

---

## 10. Success Criteria

### MVP Launch Success
- [ ] Zero critical bugs in production
- [ ] All v1.0 features functional
- [ ] 100% availability accuracy (no double-bookings)
- [ ] Check-in/out process < 3 minutes
- [ ] System response time < 3 seconds
- [ ] User training completed (< 1 hour)
- [ ] Documentation complete

### Post-Launch Success (First Month)
- [ ] 95%+ staff adoption
- [ ] Zero double-booking incidents
- [ ] 99% uptime maintained
- [ ] Positive user feedback
- [ ] All reports accurate

---

## 11. Glossary

| Term | Definition |
|------|-----------|
| **Check-In** | Guest arrival and room assignment process |
| **Check-Out** | Guest departure and payment settlement |
| **Confirmation Number** | Unique identifier for each reservation |
| **In-House** | Currently checked-in guests |
| **Occupancy Rate** | Percentage of occupied rooms vs total rooms |
| **Room Type** | Category of room (Standard, Deluxe, etc.) |
| **Walk-In** | Guest who arrives without prior reservation |
| **Availability** | Rooms that are not occupied for given dates |
| **Balance** | Amount owed (total - payments) |

---

## 12. Acceptance Testing Checklist

### Authentication & Users
- [ ] Admin can login and access all features
- [ ] User can login with limited permissions
- [ ] User cannot delete reservations/data
- [ ] User cannot access user management
- [ ] Admin can create/manage users
- [ ] Session persists after page refresh
- [ ] Logout clears session

### Room Management
- [ ] Admin can create room types
- [ ] Admin can create rooms with room type
- [ ] Room status updates on check-in/check-out
- [ ] Cannot delete room type with existing rooms
- [ ] Occupancy percentage displays correctly

### Guest Management
- [ ] Can create guest profiles
- [ ] Can search guests by name/email/phone
- [ ] View guest reservation history
- [ ] Cannot delete guest with active reservations

### Reservations
- [ ] Can create reservation with guest
- [ ] Availability checking prevents double-booking
- [ ] Confirmation number is unique
- [ ] Total amount auto-calculates correctly
- [ ] Can assign room during or after creation
- [ ] Can extend reservation
- [ ] Can cancel reservation (admin)
- [ ] Arrivals list shows today's check-ins
- [ ] Departures list shows today's check-outs

### Check-In/Out
- [ ] Check-in updates reservation and room status
- [ ] Cannot check-in without room assignment
- [ ] Check-out updates statuses correctly
- [ ] Room becomes available after checkout
- [ ] Can handle walk-in guests

### Payments
- [ ] Can record payment against reservation
- [ ] Balance calculates correctly
- [ ] Multiple payments per reservation work
- [ ] Payment history displays correctly

### Dashboard
- [ ] Today's metrics display correctly
- [ ] Occupancy rate is accurate
- [ ] Revenue totals are correct
- [ ] Quick access links work
- [ ] Dashboard loads < 3 seconds

### Security
- [ ] Passwords are hashed
- [ ] JWT tokens expire appropriately
- [ ] Role permissions enforced
- [ ] SQL injection prevented
- [ ] XSS prevented

---

## 13. Development Timeline (Estimate)

### Phase 1: Setup & Core Models (Week 1-2)
- Database schema design
- Backend models (User, RoomType, Room, Guest, Reservation, Payment)
- Authentication with roles
- Database migrations

### Phase 2: Room & Guest Management (Week 3)
- Room type CRUD
- Room CRUD
- Guest CRUD
- Availability checking logic

### Phase 3: Reservation System (Week 4-5)
- Reservation CRUD
- Availability search
- Conflict detection
- Confirmation number generation

### Phase 4: Check-In/Out (Week 6)
- Check-in workflow
- Check-out workflow
- Arrivals/departures lists
- Walk-in handling

### Phase 5: Payments (Week 7)
- Payment recording
- Balance calculation
- Payment history

### Phase 6: Dashboard (Week 8)
- Metrics calculation
- Dashboard UI
- Summary views

### Phase 7: Frontend Polish (Week 9)
- UI/UX refinement
- Mobile responsiveness
- Error handling
- Loading states

### Phase 8: Testing & Deployment (Week 10)
- Integration testing
- User acceptance testing
- Bug fixes
- Production deployment

**Total: ~10 weeks (2.5 months)**

---

## Appendix A: Feature Comparison

| Feature | KOS v1.0 | Hotel MVP v1.0 |
|---------|----------|----------------|
| **Authentication** | Single admin | Admin + User roles |
| **Room Management** | Simple rooms | Room types + rooms |
| **Guest/Tenant** | Tenant (long-term) | Guest (short-term) |
| **Booking** | Move-in/out | Reservations + check-in/out |
| **Availability** | Simple status | Date-based availability |
| **Payments** | Monthly tracking | Per-reservation tracking |
| **Dashboard** | Income/expenses | Occupancy/revenue |
| **Expenses** | Yes | No (v2.0) |
| **Housekeeping** | No | No (v2.0) |
| **Reports** | Basic | Basic |

---

## Appendix B: API Response Examples

### Availability Check Response
```json
{
  "check_in": "2025-12-01",
  "check_out": "2025-12-05",
  "available_room_types": [
    {
      "room_type_id": 1,
      "name": "Standard Double",
      "available_count": 5,
      "default_rate": 500000,
      "available_rooms": [101, 102, 103, 104, 105]
    }
  ]
}
```

### Dashboard Metrics Response
```json
{
  "date": "2025-11-07",
  "arrivals_today": 5,
  "departures_today": 3,
  "in_house": 45,
  "available_rooms": 15,
  "total_rooms": 60,
  "occupancy_rate": 75.0,
  "revenue_month": 125000000,
  "outstanding_balance": 5000000
}
```

---

**Document Approval**

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | Claudio | Pending | — |
| Developer | — | Pending | — |

---

**Change Log**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-07 | MVP scope: Core hotel operations only | Claude |

---

**Next Steps**

1. ✅ Review and approve MVP scope
2. ⏳ Create detailed database schema
3. ⏳ Design API endpoints in detail
4. ⏳ Create UI wireframes
5. ⏳ Begin development Phase 1

---

**Status**: ✅ **Ready for Review**

This PRD defines a focused MVP that delivers core hotel management functionality without the complexity of advanced features. All deferred features are documented for v2.0 planning.
