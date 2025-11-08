# Hotel Management System - Backend Architecture Summary

## Project Overview
This is a FastAPI-based Hotel Management System backend designed for Supabase PostgreSQL production. It provides REST API endpoints for managing hotel properties, reservations, payments, guests, and operations.

**Technology Stack:**
- Framework: FastAPI 0.104.1
- Database: PostgreSQL (via SQLAlchemy 2.0.44)
- Authentication: Token-based (Bearer token, 16-hour expiration)
- Server: Uvicorn
- Password: bcrypt hashing
- API Validation: Pydantic v2

---

## Database Models & Schemas

### 1. User Model
**Purpose:** Staff/Admin user accounts with role-based access

**Fields:**
```
- id (Primary Key)
- username (unique, indexed)
- password_hash (bcrypt)
- email (indexed)
- full_name
- phone
- role: 'admin' or 'user'
- status: 'active' or 'inactive'
- last_login
- created_at, updated_at
```

**Methods:**
- `set_password(password)` - Hash and store password
- `check_password(password)` - Verify password
- `to_dict()` - Convert to dictionary

---

### 2. RoomType Model
**Purpose:** Define room categories (e.g., Single, Double, Suite)

**Fields:**
```
- id (Primary Key)
- name (required)
- code (unique, indexed) - e.g., "SNG", "DBL"
- description
- base_capacity_adults (default: 2)
- base_capacity_children (default: 1)
- bed_config - e.g., "1 Queen bed"
- default_rate (Numeric 12,2) - Default nightly rate
- amenities (text)
- max_occupancy
- is_active (indexed)
- created_at, updated_at
```

**Relationships:**
- Rooms (one-to-many)
- RoomTypeImages (one-to-many)
- Guests' preferred room types (one-to-many)

---

### 3. Room Model
**Purpose:** Individual room inventory with occupancy status

**Fields:**
```
- id (Primary Key)
- room_number (unique, indexed) - e.g., "101", "A1"
- floor
- room_type_id (Foreign Key, indexed)
- status (indexed): 'available', 'occupied', 'out_of_order'
- view_type - e.g., "Ocean view", "City view"
- notes
- custom_rate (Numeric 12,2) - Override room type rate
- is_active (indexed)
- created_at, updated_at
```

**Methods:**
- `get_effective_rate()` - Returns custom_rate or room_type default_rate
- `to_dict()` - Convert to dictionary with effective rate

**Relationships:**
- RoomType (many-to-one)
- RoomImages (one-to-many)
- Reservations (one-to-many)

---

### 4. RoomImage & RoomTypeImage Models
**Purpose:** Store images for rooms and room types

**RoomImage Fields:**
```
- image_type: 'main_photo', 'bedroom', 'bathroom', 'living_area', 'amenities', 'other'
- storage_location: 'local', 's3', 'gcs', 'azure'
- image_path, file_size_bytes, mime_type
- uploaded_by (FK to User)
- display_order
```

**RoomTypeImage Fields:**
```
- image_type: 'showcase', 'floorplan', 'amenities', 'other'
- Similar structure to RoomImage
```

---

### 5. Guest Model
**Purpose:** Guest information and identification

**Fields:**
```
- id (Primary Key)
- full_name (indexed, required)
- email (indexed)
- phone (indexed)
- phone_country_code - e.g., "+1"
- id_type (required) - 'passport', 'driver_license', 'national_id', etc.
- id_number (required) - ID document number
- nationality
- birth_date
- is_vip (default: false)
- notes
- preferred_room_type_id (Foreign Key)
- created_at, updated_at
```

**IMPORTANT:** full_name, id_type, and id_number are REQUIRED fields for every guest.

**Relationships:**
- Reservations (one-to-many)
- GuestImages (one-to-many) - For ID photos
- PreferredRoomType (many-to-one)

---

### 6. GuestImage Model
**Purpose:** Store guest ID photos and identity documents

**Fields:**
```
- guest_id (Foreign Key, indexed)
- image_type - 'id_photo', 'passport_photo', 'license_photo', etc.
- file_path - Storage location (GCS, S3, local, Azure)
- file_name, file_size, mime_type
- uploaded_by_user_id (Foreign Key to User)
- created_at
```

---

### 7. Reservation Model
**Purpose:** Guest room bookings with full lifecycle management

**Fields:**
```
- id (Primary Key)
- confirmation_number (unique, indexed) - Auto-generated hex code
- guest_id (Foreign Key, indexed)
- check_in_date (indexed)
- check_out_date (indexed)
- room_type_id (Foreign Key, required)
- room_id (Foreign Key, indexed) - Assigned during check-in
- adults (default: 1)
- children (default: 0)
- rate_per_night (Numeric 12,2, required)
- number_of_nights - Calculated
- subtotal (Numeric 12,2, required)
- discount_amount (Numeric 12,2, default: 0)
- discount_id (Foreign Key)
- total_amount (Numeric 12,2, required)
- deposit_amount (Numeric 12,2, default: 0) - Refundable security deposit
- special_requests
- status (indexed): 'confirmed', 'checked_in', 'checked_out', 'cancelled'
- booking_source
- booking_channel_id (Foreign Key)
- created_by (Foreign Key, indexed)
- checked_in_by (Foreign Key) - Receptionist who did check-in
- checked_in_at
- checked_out_at
- deposit_returned_at - When deposit was settled
- is_archived
- created_at, updated_at
```

**Methods:**
- `calculate_total_paid()` - Sum of non-refund, non-voided payments
- `calculate_balance()` - total_amount - total_paid
- `to_dict()` - Full reservation details

**Key Indexes:**
- (check_in_date, check_out_date)
- (guest_id, check_in_date, check_out_date)

---

### 8. Payment Model
**Purpose:** Track all payment transactions per reservation

**Fields:**
```
- id (Primary Key)
- reservation_id (Foreign Key, indexed, required)
- payment_date (indexed, required)
- amount (Numeric 12,2, required)
- payment_method (indexed, required):
  - 'cash'
  - 'credit_card'
  - 'debit_card'
  - 'bank_transfer'
  - 'e_wallet'
  - 'other'
- payment_type: 'full', 'downpayment', 'deposit', 'adjustment'
- reference_number - Card number, transfer ID, receipt number
- transaction_id (indexed)
- notes
- created_by (Foreign Key to User)
- is_refund (default: false)
- refund_reason
- is_voided (default: false)
- has_proof (indexed, default: false)
- created_at, updated_at
```

**Methods:**
- `to_dict()` - Full payment details

---

### 9. PaymentAttachment Model
**Purpose:** Proofs of payment (receipts, invoices, transfer confirmations)

**Fields:**
```
- payment_id (Foreign Key, indexed)
- file_type:
  - 'invoice'
  - 'receipt'
  - 'transfer_proof'
  - 'credit_card_slip'
  - 'other'
- file_name, file_path
- storage_location: 'local', 's3', 'gcs', 'azure'
- file_size_bytes, mime_type
- uploaded_by (Foreign Key to User)
- is_verified (indexed, default: false)
- verified_by (Foreign Key to User)
- verified_at
- description
- created_at, updated_at
```

---

### 10. Setting Model
**Purpose:** System configuration and feature flags

**Fields:**
```
- setting_key (unique, indexed) - e.g., "hotel_name", "timezone"
- setting_value (Text)
- setting_type: 'string', 'integer', 'boolean', 'json', 'decimal'
- category - e.g., "general", "payments", "features"
- is_editable (default: true)
- description
- created_at, updated_at
```

---

### 11. Discount Model (v1.1+, not actively used in v1.0)
**Purpose:** Promotional codes and discounts

**Fields:**
```
- code (unique, indexed)
- discount_type: 'percentage' or 'fixed_amount'
- discount_value
- valid_from, valid_until
- usage_limit, usage_count
- min_stay_nights, max_bookings_per_guest
- status: 'active', 'inactive', 'expired'
- is_auto_applied
```

---

### 12. BookingChannel Model
**Purpose:** Integration with OTAs and booking platforms

**Fields:**
```
- code (unique, indexed) - e.g., "OTA_BOOKING", "DIRECT"
- channel_type: 'ota', 'direct', 'corporate', 'api'
- api_url, api_key, api_secret
- webhook_url
- is_enabled (indexed)
- auto_confirm
- sync_enabled
- commission_percentage, commission_fixed_amount
```

---

## API Endpoints

### Authentication (/api/auth)

#### POST /api/auth/login
**Purpose:** Authenticate user and get access token

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "access_token": "token_string",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "claudio",
    "email": "email@example.com",
    "role": "admin",
    "status": "active",
    "created_at": "2025-11-08T10:00:00"
  }
}
```

**Status Codes:**
- 200: Success
- 401: Invalid credentials

---

#### GET /api/auth/me
**Purpose:** Get current authenticated user

**Headers:** Authorization: Bearer {token}

**Response (200 OK):**
```json
{
  "user": { /* User object */ }
}
```

**Status Codes:**
- 200: Success
- 401: Invalid/expired token

---

### Guests (/api/guests)

#### POST /api/guests
**Purpose:** Create a new guest (receptionist registration)

**Request Body (Required: full_name, id_type, id_number):**
```json
{
  "full_name": "John Doe",
  "id_type": "passport",
  "id_number": "A12345678",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "phone_country_code": "+1",
  "nationality": "USA",
  "birth_date": "1990-05-15",
  "is_vip": false,
  "preferred_room_type_id": 2,
  "notes": "Prefers high floor"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "full_name": "John Doe",
  "id_type": "passport",
  "id_number": "A12345678",
  "email": "john@example.com",
  "is_vip": false,
  "created_at": "2025-11-08T10:00:00"
}
```

---

#### GET /api/guests
**Purpose:** List guests with pagination and filters

**Query Parameters:**
- skip (default: 0)
- limit (default: 10, max: 100)
- search (optional) - Search by name or email
- is_vip (optional) - Filter by VIP status

**Response:**
```json
{
  "guests": [ /* GuestResponse array */ ],
  "total": 150,
  "skip": 0,
  "limit": 10
}
```

---

#### GET /api/guests/{guest_id}
**Purpose:** Get specific guest details

**Response (200 OK):**
```json
{
  "id": 1,
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "id_type": "passport",
  "id_number": "A12345678",
  "nationality": "USA",
  "birth_date": "1990-05-15",
  "is_vip": false,
  "preferred_room_type_id": 2,
  "notes": "Prefers high floor",
  "created_at": "2025-11-08T10:00:00",
  "updated_at": "2025-11-08T10:00:00"
}
```

---

#### PUT /api/guests/{guest_id}
**Purpose:** Update guest information

**Request Body:** (all fields optional)
```json
{
  "is_vip": true,
  "preferred_room_type_id": 3,
  "notes": "VIP guest"
}
```

**Response:** Updated GuestResponse

---

#### DELETE /api/guests/{guest_id}
**Purpose:** Delete guest

**Response (200 OK):**
```json
{
  "message": "Guest deleted successfully"
}
```

---

### Reservations (/api/reservations)

#### POST /api/reservations/availability
**Purpose:** Check room availability for a date range

**Query Parameters:**
- room_type_id (required)
- check_in_date (required, YYYY-MM-DD)
- check_out_date (required, YYYY-MM-DD)

**Response (200 OK):**
```json
{
  "room_type_id": 2,
  "room_type_name": "Double Room",
  "check_in_date": "2025-11-10",
  "check_out_date": "2025-11-13",
  "total_rooms": 10,
  "available_rooms": 8,
  "is_available": true,
  "message": "8 of 10 rooms available"
}
```

---

#### POST /api/reservations
**Purpose:** Create a new reservation

**Request Body:**
```json
{
  "guest_id": 1,
  "room_type_id": 2,
  "check_in_date": "2025-11-10",
  "check_out_date": "2025-11-13",
  "adults": 2,
  "children": 1,
  "rate_per_night": 500000,
  "subtotal": 1500000,
  "discount_amount": 100000,
  "total_amount": 1400000,
  "deposit_amount": 500000,
  "special_requests": "Late check-in, breakfast"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "confirmation_number": "ABC123XYZ",
  "guest_id": 1,
  "guest_name": "John Doe",
  "check_in_date": "2025-11-10",
  "check_out_date": "2025-11-13",
  "room_type_id": 2,
  "room_id": null,
  "adults": 2,
  "children": 1,
  "rate_per_night": 500000,
  "subtotal": 1500000,
  "discount_amount": 100000,
  "total_amount": 1400000,
  "deposit_amount": 500000,
  "total_paid": 0,
  "balance": 1400000,
  "status": "confirmed",
  "checked_in_at": null,
  "checked_in_by": null,
  "checked_out_at": null,
  "created_at": "2025-11-09T10:00:00"
}
```

---

#### GET /api/reservations
**Purpose:** List reservations with filters

**Query Parameters:**
- skip (default: 0)
- limit (default: 10)
- status (optional): 'confirmed', 'checked_in', 'checked_out', 'cancelled'
- guest_id (optional)

**Response:**
```json
{
  "reservations": [ /* ReservationResponse array */ ],
  "total": 45,
  "skip": 0,
  "limit": 10
}
```

---

#### GET /api/reservations/{reservation_id}
**Purpose:** Get specific reservation details

**Response:** ReservationResponse with all details

---

#### GET /api/reservations/{reservation_id}/balance
**Purpose:** Get payment and deposit status for a reservation

**Response (200 OK):**
```json
{
  "reservation_id": 1,
  "confirmation_number": "ABC123XYZ",
  "guest_name": "John Doe",
  "total_amount": 1400000,
  "total_paid": 500000,
  "balance": 900000,
  "deposit_amount": 500000,
  "deposit_returned_at": null,
  "final_balance_after_deposit": 400000,
  "payment_status": "partial_paid",
  "reservation_status": "confirmed"
}
```

---

#### PUT /api/reservations/{reservation_id}
**Purpose:** Update reservation

**Request Body:** (all fields optional)
```json
{
  "special_requests": "Early checkout needed",
  "status": "confirmed"
}
```

---

#### DELETE /api/reservations/{reservation_id}
**Purpose:** Cancel reservation

**Response (200 OK):**
```json
{
  "message": "Reservation 1 cancelled successfully"
}
```

---

#### POST /api/reservations/{reservation_id}/check-in
**Purpose:** Check in guest (assign room, track receptionist)

**Query Parameters:**
- room_id (required) - Room to assign
- require_payment (optional, default: false) - Require payment before check-in

**Response (200 OK):**
```json
{
  "message": "Guest checked in successfully",
  "reservation_id": 1,
  "confirmation_number": "ABC123XYZ",
  "guest_name": "John Doe",
  "room_number": "101",
  "room_type": "Double Room",
  "checked_in_at": "2025-11-10T15:30:00",
  "checked_in_by": 2,
  "checked_in_by_name": "receptionist_john",
  "total_amount": 1400000,
  "total_paid": 500000,
  "balance": 900000,
  "payment_status": "partial_paid"
}
```

---

#### POST /api/reservations/{reservation_id}/check-out
**Purpose:** Check out guest, process deposit refund/settlement

**Response (200 OK):**
```json
{
  "message": "Guest checked out successfully",
  "reservation_id": 1,
  "confirmation_number": "ABC123XYZ",
  "guest_name": "John Doe",
  "checked_out_at": "2025-11-13T11:00:00",
  "total_amount": 1400000,
  "total_paid": 1400000,
  "balance_before_deposit": 0,
  "deposit_settlement": {
    "deposit_held": 500000,
    "balance_owed": 0,
    "to_refund": 500000,
    "settlement_note": "All charges paid. Returning full deposit of 500000"
  },
  "final_balance_owed": 0
}
```

---

### Payments (/api/payments)

#### POST /api/payments
**Purpose:** Record a new payment for a reservation

**Request Body:**
```json
{
  "reservation_id": 1,
  "amount": 500000,
  "payment_date": "2025-11-08",
  "payment_method": "bank_transfer",
  "payment_type": "downpayment",
  "reference_number": "TRF123456",
  "notes": "50% downpayment"
}
```

**Response (201 Created):**
```json
{
  "message": "Payment recorded successfully",
  "payment": {
    "id": 1,
    "reservation_id": 1,
    "payment_date": "2025-11-08",
    "amount": 500000,
    "payment_method": "bank_transfer",
    "payment_type": "downpayment",
    "reference_number": "TRF123456",
    "is_refund": false,
    "has_proof": false,
    "created_at": "2025-11-08T10:00:00"
  }
}
```

---

#### GET /api/payments
**Purpose:** List payments with filtering

**Query Parameters:**
- reservation_id (optional)
- status (optional)
- skip (default: 0)
- limit (default: 100, max: 1000)

**Response:**
```json
{
  "payments": [ /* Payment array */ ],
  "total": 50,
  "skip": 0,
  "limit": 100
}
```

---

#### GET /api/payments/{payment_id}
**Purpose:** Get specific payment details

**Response:**
```json
{
  "payment": { /* Payment object */ }
}
```

---

#### PUT /api/payments/{payment_id}
**Purpose:** Update payment

**Request Body:** (any field optional)
```json
{
  "payment_method": "cash",
  "reference_number": "RECEIPT-001"
}
```

---

#### DELETE /api/payments/{payment_id}
**Purpose:** Delete/void payment

**Response:**
```json
{
  "message": "Payment deleted successfully"
}
```

---

### Rooms (/api/rooms)

#### GET /api/rooms
**Purpose:** List all rooms with pagination

**Query Parameters:**
- skip (default: 0)
- limit (default: 100, max: 1000)

**Response:**
```json
{
  "rooms": [ /* Room array */ ],
  "total": 25,
  "skip": 0,
  "limit": 100
}
```

---

#### GET /api/rooms/{room_id}
**Purpose:** Get specific room details

**Response:**
```json
{
  "room": {
    "id": 1,
    "room_number": "101",
    "floor": 1,
    "room_type_id": 2,
    "room_type_name": "Double Room",
    "status": "available",
    "view_type": "Ocean view",
    "custom_rate": null,
    "effective_rate": 500000,
    "is_active": true,
    "created_at": "2025-11-01T10:00:00"
  }
}
```

---

### Dashboard (/api/dashboard)

#### GET /api/dashboard/today
**Purpose:** Get today's operational summary

**Response (200 OK):**
```json
{
  "date": "2025-11-08",
  "arrivals_today": 3,
  "departures_today": 2,
  "in_house": 12,
  "available_rooms": 8,
  "total_rooms": 20,
  "occupancy_rate": 60.0,
  "rooms_by_status": {
    "available": 8,
    "occupied": 12,
    "out_of_order": 0
  }
}
```

---

#### GET /api/dashboard/metrics
**Purpose:** Get period metrics (default: current month)

**Query Parameters:**
- start_date (optional, YYYY-MM-DD)
- end_date (optional, YYYY-MM-DD)

**Response:**
```json
{
  "period": "2025-11-01 to 2025-11-30",
  "total_rooms": 20,
  "occupied_rooms": 15,
  "available_rooms": 5,
  "occupancy_rate": 75.0,
  "total_income": 5000000,
  "total_expenses": 800000,
  "net_profit": 4200000,
  "reservations_completed": 8,
  "reservations_pending": 3
}
```

---

### Health Check (/health)

#### GET /health
**Purpose:** Comprehensive system health check

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T10:00:00",
  "environment": "production",
  "database_type": "postgresql",
  "checks": {
    "database_connection": true,
    "database_tables": true,
    "initial_data": true,
    "api_server": true
  },
  "details": {
    "database_status": "connected",
    "table_counts": {
      "users": 1,
      "room_types": 4,
      "booking_channels": 5,
      "settings": 8,
      "rooms": 20,
      "reservations": 15,
      "payments": 45
    }
  }
}
```

---

### API Root (/api)

#### GET /api
**Purpose:** API information endpoint

**Response:**
```json
{
  "message": "Hotel Management System API",
  "version": "1.0.0",
  "status": "active",
  "docs": "/api/docs",
  "openapi": "/api/openapi.json"
}
```

---

## Authentication & Authorization

### Token System
- **Type:** Bearer token (custom implementation in `security.py`)
- **Expiration:** 16 hours (shift-based)
- **Storage:** In-memory token dictionary (development only - use Redis in production)
- **Header:** `Authorization: Bearer {token}`

### Authorization Checks
All endpoints except `/health` and `/api` require valid authentication via `get_current_user` dependency.

### User Roles
- `admin` - Full access (planned for future implementation)
- `user` - Standard access (planned for future implementation)

Currently, role-based access control is not enforced - all authenticated users have access to all endpoints.

---

## Error Handling

**Standard Error Response:**
```json
{
  "error": "Error message",
  "detail": "Detailed error message"
}
```

**Common Status Codes:**
- 200: Success
- 201: Created
- 400: Bad request (validation error)
- 401: Unauthorized (invalid/missing token)
- 402: Payment required
- 404: Not found
- 409: Conflict (duplicate, unavailable resource)
- 500: Server error

---

## Data Validation

### Pydantic Schemas
All request/response data validated via Pydantic v2 models in `schemas.py`:

**Auth Schemas:**
- `UserLogin` - username, password
- `TokenResponse` - access_token, token_type, user

**Guest Schemas:**
- `GuestCreate` - full_name, id_type, id_number (required), optional fields
- `GuestUpdate` - all fields optional
- `GuestResponse` - full guest object

**Reservation Schemas:**
- `ReservationCreate` - guest_id, room_type_id, dates, amounts
- `ReservationUpdate` - all fields optional
- `ReservationResponse` - full reservation with calculations

**Payment Schemas:**
- `PaymentCreate` - reservation_id, amount, payment_method, payment_date
- `PaymentUpdate` - all fields optional
- `PaymentResponse` - full payment object

---

## Key Business Logic

### Reservation Workflow
1. Create guest (receptionist inputs ID details)
2. Check availability (query available rooms for dates)
3. Create reservation (system generates confirmation number)
4. Process payment(s) (partial, deposit, or full)
5. Check-in guest (assign room, track receptionist)
6. Check-out guest (process deposit settlement)

### Payment System
- **Payment Types:** full, downpayment, deposit, adjustment
- **Payment Methods:** cash, credit_card, debit_card, bank_transfer, e_wallet, other
- **Refunds:** Mark as refund with reason
- **Void:** Mark payment as voided (not counted in totals)
- **Balance Calculation:** total_amount - total_paid

### Deposit System
- Security/holding deposit collected at booking
- At check-out:
  - If guest balance > 0: Use deposit to cover
  - If guest balance = 0: Return full deposit
  - If guest overpaid: Calculate refund amount

### Receptionist Check-In Tracking
- Stores checked_in_by (user ID)
- Stores checked_in_at (timestamp)
- Tracks payment status at check-in time
- Can require payment before check-in (optional)

---

## Database Connection

**Connection Configuration (`database.py`):**
```python
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./kos.db')

# PostgreSQL (Production):
# DATABASE_URL=postgresql://user:password@host:5432/dbname

# SQLite (Development):
# DATABASE_URL=sqlite:///./kos.db
```

**Connection Pool Settings:**
- pool_size: 20
- max_overflow: 10
- pool_recycle: 3600 seconds (1 hour)
- pool_pre_ping: True (verify connections)

---

## Frontend Development Guide

### Common API Usage Patterns

**1. Authentication Flow:**
```
POST /api/auth/login -> Get token
Use token in all subsequent requests: Authorization: Bearer {token}
GET /api/auth/me -> Verify current user
```

**2. Create Reservation:**
```
1. GET /api/guests (search existing or create new)
2. POST /api/guests (if creating new guest)
3. GET /api/reservations/availability (check availability)
4. POST /api/reservations (create reservation)
5. POST /api/payments (collect payment)
```

**3. Check-In Guest:**
```
1. GET /api/reservations (find reservation)
2. GET /api/rooms (list available rooms)
3. POST /api/reservations/{id}/check-in?room_id=X
4. Track response for receptionist name and payment status
```

**4. Check-Out & Deposit Settlement:**
```
1. POST /api/reservations/{id}/check-out
2. Review deposit_settlement details
3. Process any refunds to guest
```

### Important Frontend Considerations

**1. Date Handling:**
- All dates in ISO format: YYYY-MM-DD
- All timestamps in ISO format with timezone: YYYY-MM-DDTHH:MM:SS[+TZ]
- Use date picker for date inputs

**2. Numeric Handling:**
- Amounts (money) are Numeric(12,2) - handle as decimals
- Rates per night: handle as currency
- Use proper number formatting for display

**3. Confirmation Numbers:**
- Auto-generated as 10-character hex (e.g., "ABC123XYZ")
- Display to guest for reference
- Use for lookup/inquiries

**4. Status Handling:**
- Reservation: confirmed -> checked_in -> checked_out (or cancelled)
- Room: available -> occupied -> available (or out_of_order)
- Payment: pending -> paid (or refunded/voided)

**5. Error Handling:**
- Check status codes (400 validation, 401 auth, 404 not found, 409 conflict)
- Display detail messages to user
- Log errors for debugging

**6. Pagination:**
- Default skip=0, limit=10
- Increment skip by limit for next page
- Show total count for pagination controls

**7. Filtering & Queries:**
- Use query parameters for filters
- Common filters: status, guest_id, reservation_id
- Chain multiple filters with &

---

## File Structure

```
backend/
├── app.py                 # Main FastAPI application
├── models.py              # SQLAlchemy ORM models (12 models total)
├── schemas.py             # Pydantic validation schemas
├── database.py            # Database connection & session
├── security.py            # Authentication & token management
├── error_handlers.py      # Error handling middleware
├── requirements.txt       # Python dependencies
├── routes/
│   ├── auth_router.py     # Authentication endpoints
│   ├── guests_router.py   # Guest management endpoints
│   ├── reservations_router.py  # Reservation endpoints
│   ├── payments_router.py  # Payment endpoints
│   ├── rooms_router.py    # Room management endpoints
│   ├── users_router.py    # User management endpoints
│   ├── dashboard_router.py # Dashboard & analytics
│   ├── expenses_router.py # Expense tracking (future)
│   └── tenants_router.py  # Tenant management (future)
├── docs/                  # Documentation
└── scripts/               # Setup and utility scripts
```

---

## Configuration & Environment Variables

**Required Environment Variables:**
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
PORT=8001
DEBUG=False
FLASK_ENV=production
CORS_ORIGINS=https://frontend-domain.com
```

**Development Environment:**
```
DATABASE_URL=sqlite:///./kos.db
PORT=8001
DEBUG=True
FLASK_ENV=development
CORS_ORIGINS=*
```

---

## Key Features Summary

- Multi-user authentication with role support
- Guest management with ID document tracking
- Reservation system with availability checking
- Advanced payment tracking (multiple payment types, deposits, refunds)
- Room inventory with status management
- Receptionist check-in/check-out tracking
- Deposit collection and settlement
- Dashboard metrics and reporting
- Comprehensive data validation
- PostgreSQL-ready (production-grade)
- RESTful API design with pagination
- Transaction-based operations

---

## Next Steps for Frontend Development

1. Implement authentication UI (login form, token storage)
2. Create guest management interface (list, create, search)
3. Build reservation workflow (create, search, manage)
4. Implement payment tracking & UI
5. Create check-in/check-out screens with receptionist tracking
6. Build dashboard with metrics and reports
7. Add room management interface
8. Implement image upload for guest IDs and room photos

All API endpoints are documented with request/response examples above.
