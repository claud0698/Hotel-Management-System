# Hotel Management System - Real-World Workflow Scenarios

**Complete End-to-End Usage Examples**

This document provides concrete, real-world scenarios showing how the Hotel Management System works from the hotel staff's perspective.

---

## Scenario 1: Pre-Order Booking with Deposit (30 days advance)

**Setting**: Guest books 30 days in advance for December 20-25

### Step 1: Guest Searches for Room Availability
**Frontend**: Guest uses search form
**API**: `GET /api/reservations/availability`
```http
GET /api/reservations/availability?
    room_type_id=1&
    check_in_date=2025-12-20&
    check_out_date=2025-12-25
```

**Response** (Available):
```json
{
  "room_type_id": 1,
  "room_type_name": "Standard",
  "check_in_date": "2025-12-20",
  "check_out_date": "2025-12-25",
  "total_rooms": 5,
  "available_rooms": 3,
  "is_available": true,
  "message": "3 of 5 rooms available"
}
```

### Step 2: Receptionist Creates Reservation (Pre-order)
**Frontend**: Receptionist opens New Reservation form
**Input Data**:
- Guest: John Smith (ID: 1)
- Room Type: Standard Deluxe (ID: 1)
- Check-in: 2025-12-20
- Check-out: 2025-12-25
- Adults: 2, Children: 1
- Rate per night: 500,000 IDR
- Subtotal: 2,500,000 IDR (5 nights)
- Discount: 0
- Total: 2,500,000 IDR
- **Deposit: 500,000 IDR** (20% security deposit)

**API**: `POST /api/reservations`
```json
{
  "guest_id": 1,
  "room_type_id": 1,
  "check_in_date": "2025-12-20",
  "check_out_date": "2025-12-25",
  "adults": 2,
  "children": 1,
  "rate_per_night": 500000,
  "subtotal": 2500000,
  "discount_amount": 0,
  "total_amount": 2500000,
  "deposit_amount": 500000,
  "special_requests": "High floor, breakfast included"
}
```

**Response** (201 Created):
```json
{
  "id": 42,
  "confirmation_number": "ABC2025120042",
  "guest_id": 1,
  "room_id": null,
  "room_type_id": 1,
  "check_in_date": "2025-12-20",
  "check_out_date": "2025-12-25",
  "adults": 2,
  "children": 1,
  "rate_per_night": 500000,
  "subtotal": 2500000,
  "discount_amount": 0,
  "total_amount": 2500000,
  "deposit_amount": 500000,
  "special_requests": "High floor, breakfast included",
  "status": "confirmed",
  "created_at": "2025-11-08T10:30:00"
}
```

**System Action**:
- ✅ Confirmation number generated: ABC2025120042
- ✅ Reservation saved as "confirmed" (not yet checked in)
- ✅ Room not assigned yet (will assign at check-in)
- ✅ Deposit amount recorded: 500,000 IDR

### Step 3: Guest Pays Downpayment (Optional before check-in)
**Frontend**: Receptionist records payment
**API**: `POST /api/payments`
```json
{
  "reservation_id": 42,
  "amount": 500000,
  "payment_date": "2025-11-08",
  "payment_method": "bank_transfer",
  "payment_type": "downpayment",
  "reference_number": "TRF202511081234",
  "notes": "50% downpayment received"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "reservation_id": 42,
  "amount": 500000,
  "payment_date": "2025-11-08",
  "payment_method": "bank_transfer",
  "payment_type": "downpayment",
  "reference_number": "TRF202511081234",
  "notes": "50% downpayment received",
  "created_at": "2025-11-08T10:30:00"
}
```

### Step 4: Check Balance Before Arrival
**Frontend**: Admin/Receptionist clicks "Check Balance"
**API**: `GET /api/reservations/42/balance`

**Response**:
```json
{
  "reservation_id": 42,
  "confirmation_number": "ABC2025120042",
  "guest_name": "John Smith",
  "total_amount": 2500000,
  "total_paid": 500000,
  "balance": 2000000,
  "deposit_amount": 500000,
  "final_balance_after_deposit": 1500000,
  "payment_status": "partial_paid",
  "reservation_status": "confirmed"
}
```

**Interpretation**:
- Guest has paid: 500,000 IDR
- Still owes: 2,000,000 IDR
- Security deposit held: 500,000 IDR
- After deposit applied at checkout: Guest will owe 1,500,000 IDR more

---

## Scenario 2: Check-In (December 20)

**Setting**: Guest arrives on Dec 20, 2025 (12 days after booking)

### Step 1: Receptionist Searches for Reservation
**Frontend**: Receptionist searches by confirmation number
**API**: `GET /api/reservations?confirmation_number=ABC2025120042`

**Response**: Returns reservation with status "confirmed"

### Step 2: Assign Room and Check In
**Frontend**: Receptionist selects available room (e.g., Room 301)
**API**: `POST /api/reservations/42/check-in`
```json
{
  "room_id": 5
}
```

**Response** (200 OK):
```json
{
  "id": 42,
  "confirmation_number": "ABC2025120042",
  "guest_id": 1,
  "room_id": 5,
  "room_type_id": 1,
  "status": "checked_in",
  "checked_in_at": "2025-12-20T15:30:00",
  "checked_in_by": 2,
  "checked_in_by_name": "receptionist_john",
  "deposit_amount": 500000,
  "total_amount": 2500000,
  "total_paid": 500000,
  "balance": 2000000
}
```

**System Actions**:
- ✅ Room 301 assigned to guest
- ✅ Room status changed from "available" to "occupied"
- ✅ Reservation status changed to "checked_in"
- ✅ Check-in time recorded: 2025-12-20 15:30
- ✅ Receptionist tracked: John (user_id: 2)
- ✅ Deposit held: 500,000 IDR (still held, refundable)

### Step 3: Display Check-In Receipt
**Frontend Shows**:
```
✓ CHECK-IN SUCCESSFUL

Guest: John Smith
Confirmation: ABC2025120042
Room: 301 (Standard Deluxe)
Check-in: 2025-12-20 15:30
Check-out: 2025-12-25

Total Reservation: 2,500,000 IDR
Already Paid: 500,000 IDR
Balance Remaining: 2,000,000 IDR

💰 SECURITY DEPOSIT HELD: 500,000 IDR
   (Refundable at checkout)

Still due on checkout: 2,000,000 IDR
```

---

## Scenario 3: Guest Pays Remaining Balance (Mid-Stay)

**Setting**: Guest pays remaining 2,000,000 IDR on Dec 22 (mid-stay)

### Step 1: Receptionist Records Payment
**Frontend**: Receptionist records full payment
**API**: `POST /api/payments`
```json
{
  "reservation_id": 42,
  "amount": 2000000,
  "payment_date": "2025-12-22",
  "payment_method": "cash",
  "payment_type": "full",
  "reference_number": "CASH-001234",
  "notes": "Balance paid in full"
}
```

**Response** (201 Created):
```json
{
  "id": 2,
  "reservation_id": 42,
  "amount": 2000000,
  "payment_date": "2025-12-22",
  "payment_method": "cash",
  "payment_type": "full",
  "reference_number": "CASH-001234"
}
```

### Step 2: Check Updated Balance
**API**: `GET /api/reservations/42/balance`

**Response**:
```json
{
  "reservation_id": 42,
  "confirmation_number": "ABC2025120042",
  "guest_name": "John Smith",
  "total_amount": 2500000,
  "total_paid": 2500000,
  "balance": 0,
  "deposit_amount": 500000,
  "deposit_returned_at": null,
  "final_balance_after_deposit": 0,
  "payment_status": "paid_in_full",
  "reservation_status": "checked_in"
}
```

**Interpretation**:
- Guest has paid everything: 2,500,000 IDR ✓
- No balance owed: 0 IDR
- Security deposit (500,000) will be fully refunded at checkout
- Guest is all set!

---

## Scenario 4: Check-Out with Deposit Settlement (December 25)

**Setting**: Guest checks out on Dec 25 (5 nights completed)

### Step 1: Initiate Check-Out
**Frontend**: Receptionist clicks "Check Out"
**API**: `POST /api/reservations/42/check-out`

**Response** (200 OK):
```json
{
  "message": "Guest checked out successfully",
  "reservation_id": 42,
  "confirmation_number": "ABC2025120042",
  "guest_name": "John Smith",
  "checked_out_at": "2025-12-25T11:00:00",
  "total_amount": 2500000,
  "total_paid": 2500000,
  "balance_before_deposit": 0,
  "deposit_settlement": {
    "deposit_held": 500000,
    "balance_owed": 0,
    "to_refund": 500000,
    "settlement_note": "All charges paid. Returning full deposit of 500000"
  },
  "final_balance_owed": 0,
  "deposit_returned_at": "2025-12-25T11:00:00"
}
```

### Step 2: Display Check-Out Receipt
**Frontend Shows**:
```
✓ CHECK-OUT SUCCESSFUL

Guest: John Smith
Room: 301
Check-out: 2025-12-25 11:00

=== CHARGES SUMMARY ===
Room Rate: 2,500,000 IDR (5 nights @ 500k/night)

=== PAYMENT SUMMARY ===
Total Charged: 2,500,000 IDR
Total Paid: 2,500,000 IDR
Balance Owed: 0 IDR

=== DEPOSIT SETTLEMENT ===
Security Deposit Held: 500,000 IDR
Amount Applied: 0 IDR (guest paid in full)
Refund Amount: 500,000 IDR ✓

Guest Status: SETTLED ✓
```

### Step 3: System Actions
- ✅ Room 301 status changed from "occupied" to "available"
- ✅ Reservation status changed to "checked_out"
- ✅ Deposit returned: 500,000 IDR
- ✅ Deposit timestamp recorded: 2025-12-25 11:00

---

## Scenario 5: Partial Payment at Check-Out (Different Outcome)

**Alternative Scenario**: Guest only paid 1,200,000 IDR before checkout

### Initial State (Before Check-out)
- Total: 2,500,000 IDR
- Paid: 1,200,000 IDR
- Balance: 1,300,000 IDR
- Deposit Held: 500,000 IDR

### Check-Out API Response
```json
{
  "message": "Guest checked out successfully",
  "reservation_id": 42,
  "total_amount": 2500000,
  "total_paid": 1200000,
  "balance_before_deposit": 1300000,
  "deposit_settlement": {
    "deposit_held": 500000,
    "balance_owed": 1300000,
    "to_refund": 0,
    "settlement_note": "Deposit 500000 applied. Guest still owes 800000"
  },
  "final_balance_owed": 800000,
  "deposit_returned_at": "2025-12-25T11:00:00"
}
```

### Check-Out Receipt
```
✓ CHECK-OUT PROCESS COMPLETED

Guest: John Smith
Room: 301

=== DEPOSIT SETTLEMENT ===
Security Deposit Held: 500,000 IDR
Balance Owed: 1,300,000 IDR
Deposit Applied: 500,000 IDR
Remaining Balance: 800,000 IDR

⚠️  GUEST STILL OWES: 800,000 IDR

Action Items:
[ ] Follow up on payment
[ ] Invoice for remaining balance
[ ] Arrange payment plan if needed
```

---

## Scenario 6: Walk-in Guest (Same Day Booking)

**Setting**: Walk-in guest arrives on Nov 8, wants 2-night stay (Nov 8-10)

### Step 1: Check Availability for Tonight
**API**: `GET /api/reservations/availability`
```http
GET /api/reservations/availability?
    room_type_id=2&
    check_in_date=2025-11-08&
    check_out_date=2025-11-10
```

**Response**:
```json
{
  "room_type_id": 2,
  "room_type_name": "Deluxe",
  "check_in_date": "2025-11-08",
  "check_out_date": "2025-11-10",
  "total_rooms": 3,
  "available_rooms": 2,
  "is_available": true,
  "message": "2 of 3 rooms available"
}
```

### Step 2: Create Reservation Immediately
**API**: `POST /api/reservations`
```json
{
  "guest_id": 10,
  "room_type_id": 2,
  "check_in_date": "2025-11-08",
  "check_out_date": "2025-11-10",
  "adults": 1,
  "children": 0,
  "rate_per_night": 750000,
  "subtotal": 1500000,
  "discount_amount": 0,
  "total_amount": 1500000,
  "deposit_amount": 0,
  "special_requests": "Early check-in, needs WiFi"
}
```

**Response**: Reservation created, status "confirmed"

### Step 3: Immediate Check-In
**API**: `POST /api/reservations/{id}/check-in`
```json
{
  "room_id": 8
}
```

**Response**: Guest is checked in immediately

**Timeline**:
- Availability checked → Reservation created → Room assigned → Guest checked in
- All within 5 minutes!

---

## Scenario 7: Room Unavailable - Double-Booking Prevention

**Setting**: Receptionist tries to book room that's already reserved

### Step 1: Check Availability (Hidden in System)
Two reservations already exist for Dec 20-25:
- Res #1: Dec 20-23 (John Smith)
- Res #2: Dec 23-25 (Jane Doe)

All 5 Standard rooms are booked for this period.

### Step 2: Try to Create Overlapping Reservation
**API**: `POST /api/reservations`
```json
{
  "guest_id": 15,
  "room_type_id": 1,
  "check_in_date": "2025-12-22",
  "check_out_date": "2025-12-26",
  "adults": 2,
  "children": 0,
  "rate_per_night": 500000,
  "subtotal": 2000000,
  "discount_amount": 0,
  "total_amount": 2000000,
  "deposit_amount": 0
}
```

**Response** (409 Conflict):
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "No available rooms of type 'Standard' for the selected dates (2025-12-22 to 2025-12-26)",
    "timestamp": "2025-11-08T10:30:00.123456",
    "details": {
      "room_type": "Standard",
      "check_in": "2025-12-22",
      "check_out": "2025-12-26",
      "available_rooms": 0,
      "total_rooms": 5
    }
  }
}
```

**System Action**:
- ❌ Booking rejected
- ✅ Double-booking prevented
- ✓ Clear error message helps receptionist offer alternative

---

## Scenario 8: Validation Error - Invalid Input

**Setting**: Receptionist enters invalid dates

### Step 1: Try to Create Reservation with Past Date
**API**: `POST /api/reservations`
```json
{
  "guest_id": 20,
  "room_type_id": 1,
  "check_in_date": "2025-10-15",
  "check_out_date": "2025-10-20",
  ...
}
```

**Response** (422 Unprocessable Entity):
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "timestamp": "2025-11-08T10:30:00.123456",
    "details": {
      "errors": [
        {
          "field": "check_in_date",
          "type": "value_error",
          "message": "Check-in date cannot be in the past"
        }
      ]
    }
  }
}
```

**Frontend Response**:
```
❌ VALIDATION ERROR

Check-in date cannot be in the past

Select a future date to continue.
```

---

## Scenario 9: Dashboard - Daily Operations View

**Setting**: Manager opens Dashboard at start of day (Nov 8)

### Step 1: View Today's Summary
**API**: `GET /api/dashboard/today`

**Response**:
```json
{
  "arrivals_today": 3,
  "departures_today": 2,
  "occupancy_rate": 68.5,
  "checked_in_count": 12,
  "total_rooms": 15,
  "occupied_rooms": 11,
  "available_rooms": 4,
  "revenue_today": 3500000,
  "pending_payments": 2500000
}
```

### Step 2: View Period Metrics (Last 7 Days)
**API**: `GET /api/dashboard/metrics`
```http
GET /api/dashboard/metrics?
    start_date=2025-11-01&
    end_date=2025-11-08
```

**Response**:
```json
{
  "period": {
    "start": "2025-11-01",
    "end": "2025-11-08"
  },
  "total_reservations": 18,
  "total_revenue": 22500000,
  "collected_payments": 15000000,
  "average_occupancy": 72.3,
  "check_ins_completed": 16,
  "check_outs_completed": 14
}
```

### Dashboard Display
```
HOTEL MANAGEMENT DASHBOARD
Nov 8, 2025

TODAY'S ACTIVITY
├─ Arrivals: 3 guests
├─ Departures: 2 guests
├─ Occupancy: 68.5% (11/15 rooms)
└─ Revenue: 3,500,000 IDR

PENDING ITEMS
├─ Unpaid balances: 2,500,000 IDR
├─ Expected departures: 2
└─ Arriving guests: 3

LAST 7 DAYS
├─ Total bookings: 18
├─ Revenue collected: 15,000,000 IDR
├─ Avg occupancy: 72.3%
└─ Complete check-outs: 14

Quick Actions:
[√] Check arrivals list
[√] Check departures list
[√] Follow up on payments
[√] Room maintenance schedule
```

---

## Scenario 10: Authentication & Permissions

**Setting**: Different user roles with different permissions

### Scenario A: Regular User (Receptionist)
**Can Do**:
- ✓ Create/read reservations
- ✓ Create/read guests
- ✓ Record payments
- ✓ Check-in/check-out
- ✓ View dashboard

**Cannot Do**:
- ✗ Delete users
- ✗ Delete guests
- ✗ Delete reservations
- ✗ Manage admin settings

**Login**:
```json
POST /api/auth/login
{
  "username": "receptionist_john",
  "password": "secure123"
}

Response (200 OK):
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "username": "receptionist_john",
    "role": "user"
  }
}
```

**Token Lifetime**: 16 hours (shift-based operations)

### Scenario B: Admin User
**Can Do**:
- ✓ All receptionist permissions
- ✓ Create/update/delete users
- ✓ Create/update/delete room types
- ✓ Configure system settings
- ✓ Access financial reports

**Try Delete Guest as Receptionist**:
```json
DELETE /api/guests/5
Authorization: Bearer {receptionist_token}

Response (403 Forbidden):
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions to delete guest",
    "timestamp": "2025-11-08T10:30:00"
  }
}
```

---

## Complete Workflow Timeline

**Example: A 5-Night Reservation Journey**

```
Day -30: Pre-order Booking
─────────────────────────────
Nov 8  [Receptionist creates reservation]
       ├─ Check availability: 3 rooms available ✓
       ├─ Create reservation with 20% deposit
       └─ Confirmation #ABC2025120042

Nov 8  [Guest pays 50% downpayment]
       ├─ Payment recorded: 500,000 IDR
       └─ Balance: 2,000,000 IDR

Day -1: Pre-Arrival
──────────────────
Dec 19 [Receptionist reviews upcoming arrival]
       ├─ Check balance: 2,000,000 IDR due
       └─ Prepare welcome

Day 0: Arrival
──────────────
Dec 20 [Guest arrives at 3:30 PM]
       ├─ Search reservation: ABC2025120042
       ├─ Assign Room 301
       ├─ Check-in: Room status = occupied
       └─ Display: Deposit held 500,000 IDR

Mid-stay: Payment
─────────────────
Dec 22 [Guest pays remaining balance]
       ├─ Payment recorded: 2,000,000 IDR
       ├─ Total paid: 2,500,000 IDR
       └─ Balance: 0 IDR (fully paid)

Day 5: Departure
──────────────────
Dec 25 [Guest checks out at 11 AM]
       ├─ Balance: 0 IDR
       ├─ Deposit settlement:
       │  ├─ Held: 500,000 IDR
       │  ├─ Applied: 0 IDR (paid in full)
       │  └─ Refund: 500,000 IDR ✓
       ├─ Room status: available
       └─ Receipt printed, guest leaves satisfied

End State:
──────────
✓ Reservation completed
✓ All charges paid
✓ Deposit refunded
✓ Room ready for next guest
✓ Guest history recorded
```

---

## Key Workflow Patterns

### Pattern 1: Booking Pipeline
```
Availability Check → Create Reservation → Record Deposit →
Await Guest → Check-In → Settlement → Check-Out → Refund
```

### Pattern 2: Payment Flow
```
Pre-payment (optional) → Downpayment → Balance Payment →
Full Settlement → Deposit Refund
```

### Pattern 3: Error Handling
```
Validation → Business Logic Check → Conflict Detection →
Clear Error Message → Suggest Alternative
```

### Pattern 4: Daily Operations
```
Morning: Check arrivals/departures →
Throughout day: Check-in, payments, maintenance →
Evening: Review dashboard, reconcile accounts
```

---

## Summary: What Happens Behind the Scenes

### When Guest Reserves
- ✓ Availability checked (prevents double-booking)
- ✓ Confirmation number generated
- ✓ Deposit amount recorded
- ✓ Status set to "confirmed"

### When Guest Arrives
- ✓ Room assigned
- ✓ Room status changed to "occupied"
- ✓ Status changed to "checked_in"
- ✓ Check-in time and receptionist recorded

### When Guest Pays
- ✓ Payment recorded with method and type
- ✓ Balance updated automatically
- ✓ Payment history maintained

### When Guest Leaves
- ✓ Deposit settlement calculated
- ✓ Deposit refund amount determined
- ✓ Room status changed to "available"
- ✓ Status set to "checked_out"
- ✓ Deposit timestamp recorded

---

**Complete End-to-End Hotel Management Workflow**

The system handles everything from advance bookings to final settlement, ensuring no double-bookings, clear payment tracking, and automatic deposit refunds.
