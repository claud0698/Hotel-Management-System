# Hotel Management System - Status System Documentation

## Overview

The Hotel Management System uses **two independent status fields** that serve different purposes:

1. **Room Status** - Represents the physical/operational state of a room
2. **Reservation Status** - Represents the lifecycle of a guest booking

These statuses work together to provide a complete picture of room and booking management.

---

## 1. Room Status

**Location**: `Room.status` field in database and API responses

**Purpose**: Tracks the physical and operational condition of a room at any given time.

### Allowed Values

| Status | Value | Description | Use Case |
|--------|-------|-------------|----------|
| Available | `available` | Room is clean, ready, and can be booked | Guest can check in immediately |
| Occupied | `occupied` | Room is currently occupied by a guest | Active reservation with guest present |
| Out of Order | `out_of_order` | Room has structural/safety issues | Room unsafe for guests (e.g., broken plumbing, electrical hazard) |
| Maintenance | `maintenance` | Room is being cleaned/maintained | Scheduled maintenance, housekeeping, minor repairs |

### Room Status Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                   ROOM STATUS FLOW                      │
└─────────────────────────────────────────────────────────┘

available ──(guest checks in)──> occupied
            <--(guest checks out)--

occupied ──(repair needed)──> maintenance
            <--(after cleaning)--

maintenance ──(issue found)──> out_of_order
             <--(repair complete)--

out_of_order ──(repair complete)──> available

available ──(issue detected)──> out_of_order
          <--(repair complete)--
```

### Example Scenarios

**Scenario 1: Normal Guest Checkout**
- Room Status: `occupied` → Guest checks out → `available`
- Reservation Status: `checked_in` → Guest checks out → `checked_out`

**Scenario 2: Room Needs Cleaning**
- Room Status: `available` → Housekeeping starts → `maintenance`
- After cleaning: `maintenance` → `available`
- No reservation is affected

**Scenario 3: Emergency Maintenance**
- Room Status: `occupied` → AC breaks down → Manager marks as `maintenance`
- Guest may need to be relocated
- Reservation Status remains `checked_in` until guest relocates

**Scenario 4: Structural Damage**
- Room Status: `available` → Foundation crack discovered → `out_of_order`
- Room cannot be booked until repairs are complete
- New reservations are prevented

---

## 2. Reservation Status

**Location**: `Reservation.status` field in database and API responses

**Purpose**: Tracks the progression of a guest booking from confirmation to checkout.

### Allowed Values

| Status | Value | Description | Use Case |
|--------|-------|-------------|----------|
| Confirmed | `confirmed` | Reservation is booked but guest hasn't checked in | Guest hasn't arrived yet |
| Checked In | `checked_in` | Guest is currently in the room | Active stay in progress |
| Checked Out | `checked_out` | Guest has left the room | Stay is complete |
| Cancelled | `cancelled` | Reservation was cancelled | Guest cancelled or no-show |

### Reservation Status Lifecycle

```
┌──────────────────────────────────────────────────────────┐
│              RESERVATION STATUS FLOW                     │
└──────────────────────────────────────────────────────────┘

         ┌──> checked_in ──> checked_out
         │
confirmed┤
         │
         └──> cancelled
```

### Example Scenarios

**Scenario 1: Successful Booking & Checkout**
1. Booking created: `confirmed`
2. Guest arrives, check-in happens: `checked_in`
3. Guest leaves: `checked_out`
4. Payment processed and recorded

**Scenario 2: Guest Cancels**
1. Booking created: `confirmed`
2. Guest cancels before arrival: `cancelled`
3. Room is now available for other guests
4. Refund may be processed

**Scenario 3: No-Show Guest**
1. Booking created: `confirmed`
2. Scheduled check-in date arrives, guest doesn't show: Still `confirmed`
3. After no-show period: Manager marks as `cancelled`
4. Room becomes available
5. Penalty may apply

**Scenario 4: Early Checkout**
1. Guest checks in: `checked_in`
2. Guest leaves early: `checked_out`
3. Reservation ends prematurely
4. Refund or charge adjustment may apply

---

## 3. Combined Status Logic

Both statuses interact to provide complete context:

### Example: Guest Check-in Process

```
BEFORE CHECK-IN:
├── Reservation Status: confirmed
└── Room Status: available

DURING CHECK-IN:
├── Reservation Status: checked_in
└── Room Status: occupied

AFTER CHECK-OUT:
├── Reservation Status: checked_out
└── Room Status: available (after housekeeping)
```

### Example: Room Maintenance During Occupancy

```
BEFORE MAINTENANCE:
├── Reservation Status: checked_in
└── Room Status: occupied

DURING MAINTENANCE:
├── Reservation Status: checked_in (guest may be relocated)
└── Room Status: maintenance

AFTER MAINTENANCE:
├── Reservation Status: checked_in
└── Room Status: occupied
```

---

## 4. Database Schema

### Room Table

```sql
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    floor INTEGER,
    room_type_id INTEGER NOT NULL REFERENCES room_types(id),
    status VARCHAR(20) DEFAULT 'available' NOT NULL
        CHECK (status IN ('available', 'occupied', 'maintenance', 'out_of_order')),
    custom_rate DECIMAL(10,2),
    amenities TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Reservation Table

```sql
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    confirmation_number VARCHAR(20) UNIQUE,
    guest_id INTEGER NOT NULL REFERENCES guests(id),
    room_id INTEGER REFERENCES rooms(id),
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed' NOT NULL
        CHECK (status IN ('confirmed', 'checked_in', 'checked_out', 'cancelled')),
    total_amount DECIMAL(10,2),
    total_paid DECIMAL(10,2) DEFAULT 0,
    balance DECIMAL(10,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. API Response Examples

### Get Room with Status

```json
{
  "id": 1,
  "room_number": "101",
  "floor": 1,
  "room_type_name": "Standard Room",
  "nightly_rate": 300000,
  "status": "occupied",
  "amenities": "AC, TV, Shower (tanpa water heater), Kettle, Mineral Water",
  "created_at": "2025-11-08T10:00:00",
  "updated_at": "2025-11-08T15:30:00"
}
```

### Get Reservation with Status

```json
{
  "id": 1,
  "confirmation_number": "CONF-001",
  "guest_id": 1,
  "room_id": 1,
  "check_in_date": "2025-11-08",
  "check_out_date": "2025-11-10",
  "status": "checked_in",
  "total_amount": 600000,
  "total_paid": 600000,
  "balance": 0,
  "created_at": "2025-11-07T09:00:00",
  "updated_at": "2025-11-08T14:45:00"
}
```

---

## 6. Business Rules

### Room Status Rules

1. **Only one room can be occupied at a time**: A room cannot have `occupied` status if it doesn't have an active reservation with `checked_in` status
2. **Out of order blocks new bookings**: Rooms with `out_of_order` status cannot accept new reservations
3. **Maintenance can block check-ins**: A room in `maintenance` status should not have guests checking in
4. **Status must be updated with actions**: Changing room status should have a documented reason

### Reservation Status Rules

1. **Confirmed → Checked In**: A reservation can only move to `checked_in` when the room status is `available` or `occupied`
2. **Checked In → Checked Out**: A reservation can move to `checked_out` when the guest leaves
3. **Confirmed → Cancelled**: Can be cancelled anytime before `checked_in`
4. **Checked In → Cancelled**: Can be cancelled (guest early departure) with potential charges
5. **Checked Out → Cannot Change**: Once `checked_out`, status is final
6. **Cancelled → Cannot Change**: Once `cancelled`, status cannot be changed (immutable)

---

## 7. Frontend Display

### RoomsPage Status Filters

The RoomsPage allows filtering by room status:

```
┌─────────────────────────────────┐
│  Filter: [All ▼]                │
│  • All (show all statuses)       │
│  • Available (available)         │
│  • Occupied (occupied)           │
└─────────────────────────────────┘
```

**Available/Occupied Filter Interpretation**:
- `Available`: Rooms with `status = 'available'`
- `Occupied`: Rooms with `status = 'occupied'`

The filter does NOT directly show reservation status (confirmed/checked_in). It shows room status.

### Views Available

1. **Floor View** (default): Rooms grouped by floor number (1-4)
2. **By Type View**: Rooms grouped by room type with status indicators
3. **Grid View**: All rooms in a single grid layout

All views apply the same status filter.

---

## 8. Implementation Status

### ✅ Completed

- [x] Room Status field in database (available, occupied, maintenance, out_of_order)
- [x] Reservation Status field in database (confirmed, checked_in, checked_out, cancelled)
- [x] Room status display in UI (status badges with color coding)
- [x] Room status filtering (available/occupied)
- [x] Per-room-type view with status filtering
- [x] Floor-based view with status filtering

### 🔄 In Progress

- [ ] Check-in endpoint (`POST /reservations/{id}/check-in`) - implementation started
- [ ] Check-out endpoint (`POST /reservations/{id}/check-out`) - implementation started
- [ ] Automated room status updates on reservation check-in/check-out

### 📋 Not Yet Implemented

- [ ] Admin dashboard showing room status overview
- [ ] Alerts for rooms in `out_of_order` status
- [ ] Automated status recovery for maintenance (schedule-based)
- [ ] Guest cancellation with automatic room release
- [ ] Reservation conflict detection before booking
- [ ] Room status history tracking (audit log)

---

## 9. Testing Scenarios

### Test Case 1: Guest Check-in
```
1. Create reservation (status: confirmed, room: available)
2. Perform check-in operation
3. Verify: Reservation status → checked_in, Room status → occupied
```

### Test Case 2: Guest Check-out
```
1. Reservation in checked_in status, room occupied
2. Perform check-out operation
3. Verify: Reservation status → checked_out, Room status → available
4. Verify: Housekeeping can then set status → maintenance for cleaning
```

### Test Case 3: Room Maintenance Override
```
1. Room status: occupied (guest is staying)
2. Maintenance needed (e.g., AC broken)
3. Manager marks room as maintenance
4. Verify: Room status → maintenance, Reservation status stays checked_in
5. Verify: Guest is notified for relocation or compensation
```

### Test Case 4: Out of Order Recovery
```
1. Room status: out_of_order (structural damage)
2. Repairs completed
3. Manager marks room as available
4. Verify: Room can accept new reservations
5. Verify: All conflicting reservations are cancelled/rebooked
```

---

## 10. Quick Reference

| Aspect | Room Status | Reservation Status |
|--------|------------|-------------------|
| **Purpose** | Physical/operational condition | Booking progression |
| **Entity** | Room | Reservation |
| **Values** | available, occupied, maintenance, out_of_order | confirmed, checked_in, checked_out, cancelled |
| **Affects** | Room availability, housekeeping tasks | Guest access, billing, check-in/out |
| **Changed By** | Room manager, housekeeping | Receptionist, guest |
| **Impact on Bookings** | out_of_order blocks new bookings | cancelled frees the room |

---

## References

- [Room Management Documentation](./ROOM_MANAGEMENT.md)
- [Reservation Management Documentation](./RESERVATION_MANAGEMENT.md)
- [API Documentation](./API.md)
