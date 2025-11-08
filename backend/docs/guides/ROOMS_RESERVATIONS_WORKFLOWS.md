# Rooms & Reservations Complete Workflow Guide

**Purpose**: Real-world workflow examples combining rooms and reservations functionality

**Last Updated**: November 8, 2025

**Status**: Ready for Phase 9

---

## Table of Contents

1. [Core Workflows](#core-workflows)
2. [Scenario 1: Standard Booking & Check-in](#scenario-1-standard-booking--check-in)
3. [Scenario 2: Partial Payment Deposit Return](#scenario-2-partial-payment-deposit-return)
4. [Scenario 3: Pre-order Future Booking](#scenario-3-pre-order-future-booking)
5. [Scenario 4: Double-booking Prevention](#scenario-4-double-booking-prevention)
6. [Scenario 5: Deposit Overpayment Refund](#scenario-5-deposit-overpayment-refund)
7. [Edge Cases & Error Handling](#edge-cases--error-handling)
8. [Integration Patterns](#integration-patterns)
9. [Data State Transitions](#data-state-transitions)

---

## Core Workflows

### Overview of Main Flows

```
┌─────────────────────────────────────────────────────────────┐
│              ROOMS & RESERVATIONS WORKFLOW                  │
└─────────────────────────────────────────────────────────────┘

1. AVAILABILITY CHECK
   Check room availability for dates
   ↓
2. CREATE RESERVATION
   Book room with initial deposit
   ↓
3. CHECK-IN (Receptionist)
   Assign specific room, verify payment
   ↓
4. OCCUPIED STATE
   Guest stays in room
   ↓
5. CHECK-OUT (Receptionist)
   Settle deposit, calculate refunds
   ↓
6. RESERVATION COMPLETE
   Room returns to available status

OPTIONAL FLOWS:
- PRE-ORDER: Book >30 days in advance
- PARTIAL PAYMENT: Guest pays less than total amount
- CANCEL: Cancel reservation before check-in
```

---

## Scenario 1: Standard Booking & Check-in

**Situation**: Guest books a room, arrives, and checks out next day with full payment.

### Step 1: Check Availability

```bash
curl -X GET "http://localhost:8001/api/reservations/availability" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "room_type_id": 1,
    "check_in": "2025-11-10",
    "check_out": "2025-11-11"
  }'
```

**Response** (200 OK):
```json
{
  "room_type_id": 1,
  "check_in_date": "2025-11-10",
  "check_out_date": "2025-11-11",
  "available_rooms": 3,
  "total_rooms": 4,
  "is_available": true,
  "message": "3 rooms available for selected dates"
}
```

**What happens**:
- System queries all Reservation records for room_type_id=1
- Checks for overlap: `NOT (res.checkout <= checkin OR res.checkin >= checkout)`
- Counts available rooms: total - overlapping = 3
- Returns availability info

### Step 2: Create Reservation

```bash
curl -X POST "http://localhost:8001/api/reservations" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "guest_id": 5,
    "room_type_id": 1,
    "check_in_date": "2025-11-10",
    "check_out_date": "2025-11-11",
    "total_amount": 500000,
    "deposit_amount": 250000,
    "notes": "Standard 1-night stay"
  }'
```

**Request Validation**:
- ✅ Guest exists (guest_id=5)
- ✅ Room type exists (room_type_id=1)
- ✅ Check-out > check-in (2025-11-11 > 2025-11-10)
- ✅ Check-in not in past (2025-11-10 >= today)
- ✅ Deposit <= total_amount (250000 <= 500000)

**Response** (201 Created):
```json
{
  "id": 42,
  "confirmation_number": "a1b2c3d4e5",
  "guest_id": 5,
  "guest_name": "John Doe",
  "room_type_id": 1,
  "room_type_name": "Deluxe Double",
  "check_in_date": "2025-11-10",
  "check_out_date": "2025-11-11",
  "total_amount": 500000,
  "deposit_amount": 250000,
  "status": "confirmed",
  "room_id": null,
  "checked_in_at": null,
  "checked_out_at": null,
  "checked_in_by": null,
  "deposit_returned_at": null,
  "created_at": "2025-11-08T14:30:00Z",
  "created_by": 1,
  "notes": "Standard 1-night stay"
}
```

**Database Changes**:
- ✅ INSERT into reservations table
- ✅ status = 'confirmed'
- ✅ room_id = NULL (not assigned yet)
- ✅ created_by = current user ID

### Step 3: Record Payment

```bash
curl -X POST "http://localhost:8001/api/payments" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "reservation_id": 42,
    "amount": 250000,
    "payment_type": "cash",
    "notes": "Deposit payment on booking"
  }'
```

**Response** (201 Created):
```json
{
  "id": 78,
  "reservation_id": 42,
  "amount": 250000,
  "payment_type": "cash",
  "payment_date": "2025-11-08T14:31:00Z",
  "notes": "Deposit payment on booking"
}
```

### Step 4: Guest Arrives - Check-in

**Time: 2025-11-10 15:00**

Receptionist checks in guest and assigns room:

```bash
curl -X POST "http://localhost:8001/api/reservations/42/check-in" \
  -H "Authorization: Bearer receptionist_token" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 105,
    "require_payment": false
  }'
```

**Request Validation**:
- ✅ Reservation exists (id=42)
- ✅ Reservation status='confirmed' (not already checked in/out)
- ✅ Room exists (room_id=105)
- ✅ Room is available (status='available')
- ✅ Room belongs to correct room type (RoomType=1)

**Response** (200 OK):
```json
{
  "id": 42,
  "confirmation_number": "a1b2c3d4e5",
  "guest_name": "John Doe",
  "room_id": 105,
  "room_number": "105",
  "room_type_name": "Deluxe Double",
  "check_in_date": "2025-11-10",
  "check_out_date": "2025-11-11",
  "total_amount": 500000,
  "deposit_amount": 250000,
  "deposit_held": 250000,
  "total_paid": 250000,
  "status": "checked_in",
  "checked_in_at": "2025-11-10T15:00:00Z",
  "checked_in_by": 2,
  "checked_in_by_name": "Maria Garcia",
  "payment_status": "Partial: 250000/500000 IDR paid",
  "balance": 250000,
  "notes": "Standard 1-night stay"
}
```

**Database Changes**:
- ✅ UPDATE reservations SET status='checked_in', room_id=105, checked_in_at=NOW, checked_in_by=2
- ✅ UPDATE rooms SET status='occupied' WHERE id=105
- ✅ Receptionist "Maria Garcia" (user_id=2) recorded in checked_in_by field

### Step 5: Guest Stays

**Guest enjoys room for 24 hours**

### Step 6: Guest Checks Out

**Time: 2025-11-11 11:00**

```bash
curl -X POST "http://localhost:8001/api/reservations/42/check-out" \
  -H "Authorization: Bearer receptionist_token" \
  -H "Content-Type: application/json" \
  -d '{
    "amount_paid": 250000,
    "payment_type": "cash",
    "notes": "Final payment at checkout"
  }'
```

**Database State Before Check-out**:
- total_amount = 500000
- deposit_amount = 250000
- total_paid = 250000 (deposit only)
- balance = 500000 - 250000 = 250000

**Deposit Settlement Logic**:
```
balance = total_amount - total_paid
        = 500000 - 250000
        = 250000 (still owes)

Since balance > 0 AND deposit >= balance:
  deposit_settlement = deposit - balance
                     = 250000 - 250000
                     = 0 (no refund)
```

**Response** (200 OK):
```json
{
  "id": 42,
  "confirmation_number": "a1b2c3d4e5",
  "guest_name": "John Doe",
  "room_number": "105",
  "status": "checked_out",
  "check_in_date": "2025-11-10",
  "check_out_date": "2025-11-11",
  "total_amount": 500000,
  "total_paid": 500000,
  "deposit_held": 250000,
  "to_refund": 0,
  "settlement_note": "Full payment received. No deposit refund.",
  "checked_out_at": "2025-11-11T11:00:00Z",
  "deposit_returned_at": "2025-11-11T11:00:00Z"
}
```

**Database Changes**:
- ✅ UPDATE reservations SET status='checked_out', checked_out_at=NOW, deposit_returned_at=NOW
- ✅ UPDATE rooms SET status='available' WHERE id=105
- ✅ INSERT into payments (final payment of 250000)

**Final State**:
- Reservation: complete
- Room: available for next guest
- Guest: checked out, no refund owed

---

## Scenario 2: Partial Payment Deposit Return

**Situation**: Guest books for 2 nights, pays partial deposit, then owes balance that's less than deposit.

### Setup

```bash
curl -X POST "http://localhost:8001/api/reservations" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "guest_id": 7,
    "room_type_id": 2,
    "check_in_date": "2025-11-15",
    "check_out_date": "2025-11-17",
    "total_amount": 1000000,
    "deposit_amount": 400000,
    "notes": "2-night deluxe stay"
  }'
```

**Response**: Reservation created (id=43)

### Payment Phase 1: Initial Deposit

```bash
curl -X POST "http://localhost:8001/api/payments" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "reservation_id": 43,
    "amount": 400000,
    "payment_type": "card",
    "notes": "Initial deposit"
  }'
```

### Check-in

```bash
curl -X POST "http://localhost:8001/api/reservations/43/check-in" \
  -H "Authorization: Bearer receptionist_token" \
  -d '{
    "room_id": 205,
    "require_payment": false
  }'
```

**State**: checked_in, room_id=205, total_paid=400000

### Payment Phase 2: Partial Final Payment

**Guest pays only 500000 of remaining 600000 balance:**

```bash
curl -X POST "http://localhost:8001/api/payments" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "reservation_id": 43,
    "amount": 500000,
    "payment_type": "card",
    "notes": "Final partial payment"
  }'
```

**State Before Check-out**:
- total_amount = 1000000
- deposit_held = 400000
- total_paid = 400000 + 500000 = 900000
- balance = 1000000 - 900000 = 100000 (still owes)

### Check-out with Deposit Return

```bash
curl -X POST "http://localhost:8001/api/reservations/43/check-out" \
  -H "Authorization: Bearer receptionist_token" \
  -d '{
    "amount_paid": 0,
    "payment_type": "none",
    "notes": "Checkout - deposit settlement"
  }'
```

**Deposit Settlement Logic**:
```
balance = total_amount - total_paid
        = 1000000 - 900000
        = 100000 (still owes)

Since balance > 0 AND deposit >= balance:
  to_refund = deposit - balance
            = 400000 - 100000
            = 300000 (REFUND THIS AMOUNT)
```

**Response** (200 OK):
```json
{
  "id": 43,
  "guest_name": "Jane Smith",
  "status": "checked_out",
  "total_amount": 1000000,
  "total_paid": 900000,
  "balance_owed": 100000,
  "deposit_held": 400000,
  "to_refund": 300000,
  "settlement_note": "Guest balance: 100000 IDR. Deposit refund: 300000 IDR",
  "checked_out_at": "2025-11-17T11:00:00Z",
  "deposit_returned_at": "2025-11-17T11:00:00Z"
}
```

**Accounting Summary**:
- Deposit received: 400000
- Used against balance: 100000
- Refund to guest: 300000
- Unpaid balance: 100000 (follow-up collection)

---

## Scenario 3: Pre-order Future Booking

**Situation**: Guest books 45 days in advance with deposit.

### Create Pre-order Reservation

```bash
curl -X POST "http://localhost:8001/api/reservations" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "guest_id": 10,
    "room_type_id": 1,
    "check_in_date": "2025-12-23",
    "check_out_date": "2025-12-25",
    "total_amount": 1500000,
    "deposit_amount": 750000,
    "notes": "Holiday pre-order booking"
  }'
```

**Validation**:
- ✅ check_in_date = 2025-12-23 (45 days in future)
- ✅ check_out_date = 2025-12-25
- ✅ Checkout > checkin

**Response** (201 Created):
```json
{
  "id": 55,
  "confirmation_number": "f4e3d2c1b0",
  "guest_id": 10,
  "room_type_id": 1,
  "check_in_date": "2025-12-23",
  "check_out_date": "2025-12-25",
  "total_amount": 1500000,
  "deposit_amount": 750000,
  "status": "confirmed",
  "room_id": null,
  "notes": "Holiday pre-order booking",
  "created_at": "2025-11-08T16:00:00Z"
}
```

**Timeline**:
- Nov 8: Reservation created, deposit recorded
- Dec 1-22: System monitors availability
- Dec 23: Guest arrives, receptionist assigns room and checks in
- Dec 25: Guest checks out, deposit settled

**Key Feature**: Pre-order enables advance bookings while rooms remain flexible (room assignment only at check-in)

---

## Scenario 4: Double-booking Prevention

**Situation**: Two guests try to book overlapping dates.

### Guest A Books

```bash
curl -X POST "http://localhost:8001/api/reservations" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "guest_id": 3,
    "room_type_id": 1,
    "check_in_date": "2025-11-12",
    "check_out_date": "2025-11-15",
    "total_amount": 800000,
    "deposit_amount": 400000
  }'
```

**Response** (201 Created): Reservation id=60 created successfully

**Database State**:
```
reservations table:
- id=60, room_type_id=1, check_in=2025-11-12, check_out=2025-11-15, status='confirmed'
```

### Guest B Attempts Same Dates

```bash
curl -X POST "http://localhost:8001/api/reservations" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "guest_id": 4,
    "room_type_id": 1,
    "check_in_date": "2025-11-13",
    "check_out_date": "2025-11-14",
    "total_amount": 600000,
    "deposit_amount": 300000
  }'
```

**Overlap Detection Logic**:
```python
# Check for overlapping reservations
overlapping = db.query(Reservation).filter(
    Reservation.room_type_id == 1,
    Reservation.status.in_(['confirmed', 'checked_in']),
    ~or_(
        Reservation.check_out_date <= 2025-11-13,  # They checkout before we checkin
        Reservation.check_in_date >= 2025-11-14    # They checkin after we checkout
    )
).count()

# Results:
# Guest A: check_out=2025-11-15 > checkin=2025-11-13? YES ✓
# Guest A: check_in=2025-11-12 < checkout=2025-11-14? YES ✓
# OVERLAP DETECTED!
```

**Response** (409 Conflict):
```json
{
  "detail": "No rooms available for selected dates",
  "error_code": "AVAILABILITY_ERROR",
  "available_rooms": 0,
  "requested_dates": "2025-11-13 to 2025-11-14"
}
```

### Guest B Attempts Different Dates

```bash
curl -X POST "http://localhost:8001/api/reservations" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "guest_id": 4,
    "room_type_id": 1,
    "check_in_date": "2025-11-15",
    "check_out_date": "2025-11-17",
    "total_amount": 600000,
    "deposit_amount": 300000
  }'
```

**Overlap Check**:
```
Guest A: check_out=2025-11-15 <= checkin=2025-11-15? YES (no overlap)
AVAILABLE!
```

**Response** (201 Created): Reservation id=61 created successfully

---

## Scenario 5: Deposit Overpayment Refund

**Situation**: Guest pays more than the room cost and should receive a refund.

### Setup

```bash
curl -X POST "http://localhost:8001/api/reservations" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "guest_id": 8,
    "room_type_id": 3,
    "check_in_date": "2025-11-18",
    "check_out_date": "2025-11-19",
    "total_amount": 400000,
    "deposit_amount": 300000
  }'
```

**Response**: Reservation id=70 created

### Guest Overpays Deposit

```bash
curl -X POST "http://localhost:8001/api/payments" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "reservation_id": 70,
    "amount": 450000,
    "payment_type": "card",
    "notes": "Guest paid extra by mistake"
  }'
```

**Database State Before Check-out**:
- total_amount = 400000
- total_paid = 450000 (OVERPAID!)
- deposit_amount = 300000
- balance = 400000 - 450000 = -50000 (guest paid EXTRA)

### Check-in

```bash
curl -X POST "http://localhost:8001/api/reservations/70/check-in" \
  -H "Authorization: Bearer receptionist_token" \
  -d '{
    "room_id": 305,
    "require_payment": false
  }'
```

### Check-out with Overpayment Return

```bash
curl -X POST "http://localhost:8001/api/reservations/70/check-out" \
  -H "Authorization: Bearer receptionist_token" \
  -d '{
    "amount_paid": 0,
    "payment_type": "none",
    "notes": "Overpayment checkout"
  }'
```

**Deposit Settlement Logic**:
```
balance = total_amount - total_paid
        = 400000 - 450000
        = -50000 (guest OVERPAID)

Since balance <= 0:
  to_refund = deposit_amount + abs(balance)
            = 300000 + 50000
            = 350000 (RETURN THIS AMOUNT)
```

**Response** (200 OK):
```json
{
  "id": 70,
  "guest_name": "Robert Chen",
  "status": "checked_out",
  "total_amount": 400000,
  "total_paid": 450000,
  "deposit_held": 300000,
  "to_refund": 350000,
  "settlement_note": "Guest overpaid by 50000 IDR. Total refund: 350000 IDR",
  "checked_out_at": "2025-11-19T11:00:00Z",
  "deposit_returned_at": "2025-11-19T11:00:00Z"
}
```

**Accounting**:
- Guest paid: 450000
- Total charge: 400000
- Overpayment: 50000
- Refund calculation:
  - Return all deposit: 300000
  - Plus overpayment: 50000
  - Total refund: 350000

---

## Edge Cases & Error Handling

### Edge Case 1: Attempt Check-in with Wrong Room Type

**Scenario**: Reservation is for Deluxe (room_type_id=1), but receptionist tries to assign Standard room (room_type_id=2).

```bash
curl -X POST "http://localhost:8001/api/reservations/42/check-in" \
  -H "Authorization: Bearer receptionist_token" \
  -d '{
    "room_id": 201,  # This is Standard room, not Deluxe
    "require_payment": false
  }'
```

**Validation**:
```python
# Check room type matches reservation
room = db.query(Room).get(201)  # room_type_id = 2
reservation = db.query(Reservation).get(42)  # room_type_id = 1

if room.room_type_id != reservation.room_type_id:
    raise ValidationError("Room type mismatch")
```

**Response** (422 Unprocessable Entity):
```json
{
  "detail": "Room type mismatch. Reservation requires room type 'Deluxe Double' but room 201 is 'Standard Single'",
  "error_code": "VALIDATION_ERROR",
  "expected_type": "Deluxe Double",
  "assigned_type": "Standard Single"
}
```

### Edge Case 2: Attempt Check-in on Already Occupied Room

**Scenario**: Room is currently occupied, can't assign to new guest.

```bash
curl -X POST "http://localhost:8001/api/reservations/45/check-in" \
  -H "Authorization: Bearer receptionist_token" \
  -d '{
    "room_id": 105,  # Still occupied from previous guest
    "require_payment": false
  }'
```

**Validation**:
```python
room = db.query(Room).get(105)
if room.status != 'available':
    raise ValidationError(f"Room not available (status: {room.status})")
```

**Response** (409 Conflict):
```json
{
  "detail": "Room 105 is not available (currently: occupied)",
  "error_code": "ROOM_NOT_AVAILABLE",
  "room_id": 105,
  "current_status": "occupied"
}
```

### Edge Case 3: Attempt Check-out Before Check-in

**Scenario**: Receptionist tries to check out guest who was never checked in.

```bash
curl -X POST "http://localhost:8001/api/reservations/42/check-out" \
  -H "Authorization: Bearer receptionist_token" \
  -d '{
    "amount_paid": 100000,
    "payment_type": "cash"
  }'
```

**Validation**:
```python
if reservation.status != 'checked_in':
    raise ValidationError("Reservation must be checked in before checkout")
```

**Response** (422 Unprocessable Entity):
```json
{
  "detail": "Cannot check out. Reservation status is 'confirmed' (must be 'checked_in')",
  "error_code": "INVALID_STATE_TRANSITION",
  "current_status": "confirmed",
  "allowed_statuses": ["checked_in"]
}
```

### Edge Case 4: Attempt Check-in with Negative Room ID

**Scenario**: API receives invalid room ID.

```bash
curl -X POST "http://localhost:8001/api/reservations/42/check-in" \
  -H "Authorization: Bearer receptionist_token" \
  -d '{
    "room_id": -1,
    "require_payment": false
  }'
```

**Validation** (Pydantic):
```python
class CheckInRequest(BaseModel):
    room_id: int = Field(..., gt=0)  # Must be > 0
```

**Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["body", "room_id"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### Edge Case 5: Check Out with Amount Paid but No Payment Type

**Scenario**: Receptionist provides amount_paid but forgets payment_type.

```bash
curl -X POST "http://localhost:8001/api/reservations/42/check-out" \
  -H "Authorization: Bearer receptionist_token" \
  -d '{
    "amount_paid": 250000,
    "payment_type": "",
    "notes": "Final payment"
  }'
```

**Validation**:
```python
class CheckOutRequest(BaseModel):
    payment_type: str = Field(..., min_length=1)
```

**Response** (422 Unprocessable Entity):
```json
{
  "detail": "payment_type is required when amount_paid > 0"
}
```

### Edge Case 6: Cancel Reservation After Check-in

**Scenario**: Guest wants to cancel AFTER checking in (not allowed).

```bash
curl -X DELETE "http://localhost:8001/api/reservations/42" \
  -H "Authorization: Bearer your_token"
```

**Validation**:
```python
if reservation.status in ['checked_in', 'checked_out']:
    raise ValidationError("Cannot cancel reservation that has been checked in")
```

**Response** (409 Conflict):
```json
{
  "detail": "Cannot cancel reservation in status 'checked_in'",
  "error_code": "INVALID_STATE_TRANSITION",
  "current_status": "checked_in",
  "allowed_states_for_cancel": ["confirmed", "cancelled"]
}
```

### Edge Case 7: Double Check-in Attempt

**Scenario**: Receptionist clicks check-in button twice.

**First Check-in** (200 OK):
```json
{
  "id": 42,
  "status": "checked_in",
  "checked_in_at": "2025-11-10T15:00:00Z"
}
```

**Second Check-in Attempt**:
```bash
curl -X POST "http://localhost:8001/api/reservations/42/check-in" \
  -H "Authorization: Bearer receptionist_token" \
  -d '{
    "room_id": 105,
    "require_payment": false
  }'
```

**Validation**:
```python
if reservation.status != 'confirmed':
    raise ValidationError("Reservation already checked in")
```

**Response** (409 Conflict):
```json
{
  "detail": "Reservation has already been checked in",
  "error_code": "ALREADY_CHECKED_IN",
  "checked_in_at": "2025-11-10T15:00:00Z",
  "checked_in_by": "Maria Garcia"
}
```

### Edge Case 8: Deposit Amount Greater Than Total

**Scenario**: Trying to book with deposit > total amount.

```bash
curl -X POST "http://localhost:8001/api/reservations" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "guest_id": 5,
    "room_type_id": 1,
    "check_in_date": "2025-11-10",
    "check_out_date": "2025-11-11",
    "total_amount": 300000,
    "deposit_amount": 500000  # INVALID: > total
  }'
```

**Validation**:
```python
if deposit_amount > total_amount:
    raise ValidationError("Deposit cannot exceed total amount")
```

**Response** (422 Unprocessable Entity):
```json
{
  "detail": "Deposit amount (500000) cannot exceed total amount (300000)",
  "error_code": "VALIDATION_ERROR"
}
```

---

## Integration Patterns

### Pattern 1: Synchronized Room Status Updates

**Requirement**: Room status must always match reservation state.

**State Transitions**:

```
ROOM STATUS TRANSITIONS:

available
    ↓
[CHECKOUT → CHECK-IN happens]
    ↓
occupied
    ↓
[CHECK-OUT happens]
    ↓
available
```

**Database Constraints**:

```python
# When checking in
room.status = 'occupied'

# When checking out
room.status = 'available'

# Manual room status changes (maintenance)
room.status = 'out_of_order'  # Removes from availability
room.status = 'available'      # Returns to availability
```

**Verification Script**:
```python
# Verify consistency
for reservation in db.query(Reservation).filter(status='checked_in').all():
    room = db.query(Room).get(reservation.room_id)
    assert room.status == 'occupied', f"Mismatch: reservation {reservation.id} checked in but room {room.id} not occupied"

for reservation in db.query(Reservation).filter(status='checked_out').all():
    # Room should be available or in another reservation
    pass
```

### Pattern 2: Receptionist Audit Trail

**Requirement**: Track which receptionist performed check-in/out.

**Data Structure**:

```python
class Reservation(Base):
    checked_in_by = Column(Integer, ForeignKey("users.id"))  # User ID of receptionist
    checked_in_by_name = property(lambda self: self.checked_in_user.username if self.checked_in_user else None)
```

**Audit Report**:

```python
# Get all check-ins by specific receptionist
check_ins_by_maria = db.query(Reservation).filter(
    Reservation.checked_in_by == 2,  # Maria's user_id
    Reservation.checked_in_at >= date(2025, 11, 1)
).all()

for res in check_ins_by_maria:
    print(f"{res.guest_name} - {res.check_in_date} - {res.checked_in_at}")
```

**Example Output**:
```
John Doe - 2025-11-10 - 2025-11-10T15:00:00Z
Jane Smith - 2025-11-15 - 2025-11-15T14:30:00Z
Robert Chen - 2025-11-18 - 2025-11-18T16:00:00Z
```

### Pattern 3: Multi-Night Booking Flow

**Requirement**: Handle reservations spanning multiple nights correctly.

**Example: 3-Night Stay**

```bash
# Create 3-night reservation
curl -X POST "http://localhost:8001/api/reservations" \
  -d '{
    "guest_id": 5,
    "room_type_id": 1,
    "check_in_date": "2025-11-20",
    "check_out_date": "2025-11-23",  # 3 nights
    "total_amount": 1500000,
    "deposit_amount": 750000
  }'
```

**Night 1 (Nov 20)**:
- Guest checks in
- Room marked occupied
- Deposit recorded

**Night 2-3 (Nov 21-22)**:
- Guest remains in room
- No additional transactions

**Check-out (Nov 23)**:
- Guest checks out
- Deposit settled (refund if needed)
- Room returned to available

**Key Point**: System treats multi-night as single reservation (not separate per-night bookings)

---

## Data State Transitions

### Complete State Machine

```
CREATE RESERVATION
    ↓
[status = 'confirmed', room_id = NULL]
    ↓
    ├─→ (CANCEL) ─→ [status = 'cancelled']
    │
    └─→ CHECK-IN ─→ [status = 'checked_in', room_id = assigned]
                       ↓
                       └─→ (CHECKOUT) ─→ [status = 'checked_out']
```

### Status Definitions

| Status | Meaning | Room Assigned | Can Cancel | Can Check-in | Can Check-out |
|--------|---------|---------------|------------|--------------|---------------|
| **confirmed** | Booked, awaiting arrival | No | ✅ Yes | ✅ Yes | ❌ No |
| **checked_in** | Guest in room | Yes | ❌ No | ❌ No | ✅ Yes |
| **checked_out** | Guest departed | Yes | ❌ No | ❌ No | ❌ No |
| **cancelled** | Booking cancelled | No | ❌ No | ❌ No | ❌ No |

### Timestamp Tracking

```
created_at          : When reservation created
checked_in_at       : When guest checked in
checked_out_at      : When guest checked out
deposit_returned_at : When deposit settled

Example Timeline:
2025-11-08 14:30:00  → created_at
2025-11-10 15:00:00  → checked_in_at
2025-11-11 11:00:00  → checked_out_at & deposit_returned_at
```

---

## Real-World Query Patterns

### Query 1: Tonight's Check-ins

```python
from datetime import date

today = date.today()
check_ins_today = db.query(Reservation).filter(
    Reservation.check_in_date == today,
    Reservation.status == 'confirmed'
).order_by(Reservation.created_at).all()

for res in check_ins_today:
    print(f"{res.guest_name} - {res.room_type_name} - Deposit: {res.deposit_amount}")
```

### Query 2: Outstanding Balance Report

```python
from sqlalchemy import func

outstanding = db.query(
    Reservation.id,
    Reservation.guest_name,
    Reservation.total_amount,
    func.sum(Payment.amount).label('paid'),
    (Reservation.total_amount - func.sum(Payment.amount)).label('balance')
).outerjoin(Payment).filter(
    Reservation.status.in_(['confirmed', 'checked_in']),
    (Reservation.total_amount - func.sum(Payment.amount)) > 0
).group_by(Reservation.id).all()

for res in outstanding:
    print(f"{res.guest_name}: {res.balance} IDR outstanding")
```

### Query 3: Room Occupancy Status

```python
room_status = db.query(
    Room.room_number,
    RoomType.name,
    Room.status,
    Reservation.guest_name,
    Reservation.check_out_date
).outerjoin(RoomType).outerjoin(
    Reservation,
    (Room.id == Reservation.room_id) & (Reservation.status == 'checked_in')
).all()

for room in room_status:
    if room.status == 'occupied':
        print(f"Room {room.room_number}: {room.guest_name} (checkout {room.check_out_date})")
    else:
        print(f"Room {room.room_number}: {room.status}")
```

### Query 4: Revenue Report

```python
monthly_revenue = db.query(
    func.count(Reservation.id).label('reservations'),
    func.sum(Reservation.total_amount).label('total_amount'),
    func.sum(Payment.amount).label('collected'),
    func.sum(Reservation.total_amount) - func.sum(Payment.amount).label('outstanding')
).outerjoin(Payment).filter(
    Reservation.checked_out_at >= date(2025, 11, 1),
    Reservation.checked_out_at < date(2025, 12, 1)
).first()

print(f"November Revenue Report")
print(f"Reservations: {monthly_revenue.reservations}")
print(f"Total Amount: {monthly_revenue.total_amount}")
print(f"Collected: {monthly_revenue.collected}")
print(f"Outstanding: {monthly_revenue.outstanding}")
```

---

## Summary

This guide demonstrates:

✅ **Complete workflows**: From availability check to checkout
✅ **Real payment scenarios**: Full payment, partial payment, overpayment
✅ **Deposit settlement**: All 3 scenarios with exact calculations
✅ **Error handling**: 8 common edge cases with responses
✅ **Integration patterns**: Room status sync, audit trails, multi-night bookings
✅ **Queries**: Revenue, occupancy, outstanding balance reports

**Key Takeaways**:
- Always check availability before creating reservation
- Deposit settlement happens at checkout, not at check-in
- Room status is the source of truth for availability
- Receptionist tracking provides audit trail
- Pre-orders enable advance bookings with flexible room assignment

---

**Last Updated**: November 8, 2025
**Status**: Complete
**Next**: Document edge cases in separate document
