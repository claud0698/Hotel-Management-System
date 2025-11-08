# Hotel Management System - Quick Reference Guide

**Fast lookup for API endpoints, status codes, and common operations**

---

## API Endpoints at a Glance

### 🔐 Authentication
| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/auth/login` | POST | Login user | ✗ |
| `/api/users/me` | GET | Get current user | ✓ |
| `/api/users` | GET | List users | ✓ Admin |
| `/api/users` | POST | Create user | ✓ Admin |

### 🛏️ Room Management
| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/room-types` | GET | List room types | ✓ |
| `/api/room-types` | POST | Create room type | ✓ Admin |
| `/api/room-types/{id}` | GET | Get room type | ✓ |
| `/api/room-types/{id}` | PUT | Update room type | ✓ Admin |
| `/api/room-types/{id}` | DELETE | Delete room type | ✓ Admin |
| `/api/rooms` | GET | List rooms | ✓ |
| `/api/rooms` | POST | Create room | ✓ Admin |
| `/api/rooms/{id}` | GET | Get room | ✓ |
| `/api/rooms/{id}` | PUT | Update room | ✓ Admin |

### 👥 Guest Management
| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/guests` | GET | List/search guests | ✓ |
| `/api/guests` | POST | Create guest | ✓ |
| `/api/guests/{id}` | GET | Get guest | ✓ |
| `/api/guests/{id}` | PUT | Update guest | ✓ |
| `/api/guests/{id}` | DELETE | Delete guest | ✓ Admin |

### 📅 Reservations
| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/reservations` | GET | List reservations | ✓ |
| `/api/reservations` | POST | Create reservation | ✓ |
| `/api/reservations/{id}` | GET | Get reservation | ✓ |
| `/api/reservations/{id}` | PUT | Update reservation | ✓ |
| `/api/reservations/availability` | GET | Check availability | ✓ |
| `/api/reservations/{id}/balance` | GET | Check balance | ✓ |
| `/api/reservations/{id}/check-in` | POST | Check-in guest | ✓ |
| `/api/reservations/{id}/check-out` | POST | Check-out guest | ✓ |

### 💳 Payments
| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/payments` | GET | List payments | ✓ |
| `/api/payments` | POST | Record payment | ✓ |
| `/api/payments/{id}` | GET | Get payment | ✓ |

### 📊 Dashboard
| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/dashboard/today` | GET | Today's metrics | ✓ |
| `/api/dashboard/metrics` | GET | Period metrics | ✓ |
| `/api/dashboard/revenue` | GET | Revenue summary | ✓ |
| `/api/dashboard/summary` | GET | Quick stats | ✓ |

---

## HTTP Status Codes

### Success Codes
```
200 OK              - Successful GET/PUT
201 Created         - Successful POST (resource created)
204 No Content      - Successful DELETE
```

### Client Error Codes
```
400 Bad Request     - Invalid request format
401 Unauthorized    - Missing/invalid auth token
403 Forbidden       - Insufficient permissions
404 Not Found       - Resource doesn't exist
409 Conflict        - Double-booking or constraint violation
422 Validation      - Input validation failed
```

### Server Error Codes
```
500 Internal Error  - Unexpected server error
503 Unavailable     - Server temporarily unavailable
```

---

## Response Format

### Success Response
```json
{
  "id": 1,
  "name": "Standard Room",
  "status": "available",
  "created_at": "2025-11-08T10:30:00"
}
```

### Error Response
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "timestamp": "2025-11-08T10:30:00.123456",
    "details": {
      "field": "additional context"
    }
  }
}
```

---

## Common Operations

### 1️⃣ Check Room Availability
```bash
GET /api/reservations/availability?room_type_id=1&check_in_date=2025-12-20&check_out_date=2025-12-25
```

**Returns**: Available rooms count, total rooms, availability status

### 2️⃣ Create Reservation
```bash
POST /api/reservations
Content-Type: application/json

{
  "guest_id": 1,
  "room_type_id": 1,
  "check_in_date": "2025-12-20",
  "check_out_date": "2025-12-25",
  "adults": 2,
  "children": 0,
  "rate_per_night": 500000,
  "subtotal": 2500000,
  "discount_amount": 0,
  "total_amount": 2500000,
  "deposit_amount": 500000
}
```

**Returns**: Confirmation number, reservation ID, status "confirmed"

### 3️⃣ Record Payment
```bash
POST /api/payments
Content-Type: application/json

{
  "reservation_id": 42,
  "amount": 500000,
  "payment_date": "2025-11-08",
  "payment_method": "bank_transfer",
  "payment_type": "downpayment"
}
```

**Payment Types**:
- `full` - Complete payment
- `downpayment` - Partial payment
- `deposit` - Security deposit
- `adjustment` - Corrections

### 4️⃣ Check Balance
```bash
GET /api/reservations/42/balance
Authorization: Bearer {token}
```

**Returns**: Total, paid, balance, deposit amount, final balance after deposit

### 5️⃣ Check-In Guest
```bash
POST /api/reservations/42/check-in
Content-Type: application/json

{
  "room_id": 5
}
```

**System Updates**:
- Assigns room to reservation
- Changes status to "checked_in"
- Records check-in time and receptionist
- Changes room status to "occupied"

### 6️⃣ Check-Out Guest
```bash
POST /api/reservations/42/check-out
Authorization: Bearer {token}
```

**Returns**: Settlement calculation, deposit refund amount, final balance

---

## Deposit System Quick Guide

### How Deposits Work

| Stage | Action | Deposit Status |
|-------|--------|----------------|
| Reservation | Deposit amount set | Held (refundable) |
| Check-in | Deposit held at check-in | Still refundable |
| Mid-stay | Partial payments applied | Not yet settled |
| Check-out | Deposit settled & refunded | Timestamp recorded |

### Deposit Settlement Scenarios

**Scenario A: Full Payment**
```
Total: 2,500,000 IDR
Paid: 2,500,000 IDR
Deposit: 500,000 IDR

Result: Deposit refunded = 500,000 IDR ✓
```

**Scenario B: Partial Payment**
```
Total: 2,500,000 IDR
Paid: 1,200,000 IDR
Balance: 1,300,000 IDR
Deposit: 500,000 IDR

Deposit applied: 500,000 IDR
Remaining owed: 800,000 IDR
Refund: 0 IDR
```

**Scenario C: Overpayment**
```
Total: 2,500,000 IDR
Paid: 3,000,000 IDR
Deposit: 500,000 IDR

Result: Deposit refunded + excess = 1,000,000 IDR ✓
```

---

## Validation Rules

### Dates
- ✓ Format: YYYY-MM-DD (ISO 8601)
- ✓ Check-in: Cannot be in the past
- ✓ Check-out: Must be after check-in
- ✓ Duration: Maximum 365 days

### Occupancy
- ✓ Adults: 1-10 (required, minimum 1)
- ✓ Children: 0-10 (optional, maximum 10)
- ✓ Total: Adults + Children ≤ 10

### Pricing
- ✓ Total = Subtotal - Discount
- ✓ Discount ≤ Subtotal
- ✓ Deposit ≤ Total Amount
- ✓ All amounts > 0 (positive)

### Payments
- ✓ Full, downpayment, deposit: amount > 0
- ✓ Adjustment: amount can be negative
- ✓ Payment method: required
- ✓ Payment date: ISO format (YYYY-MM-DD)

### Strings
- ✓ Username: 3-80 chars, letters/numbers/underscore/dash
- ✓ Password: 6-200 chars (any characters)
- ✓ Full name: 2-200 chars, letters/spaces/hyphens/apostrophes
- ✓ Phone: 9-20 chars, valid phone format
- ✓ Email: Valid email format

---

## Error Codes

### Validation Errors (422)
```
VALIDATION_ERROR
├─ check_in_date: "Check-in date cannot be in the past"
├─ rate_per_night: "Must be greater than 0"
└─ total_amount: "Total must equal subtotal - discount"
```

### Resource Errors (404)
```
RESOURCE_NOT_FOUND
├─ Reservation with ID 99999 not found
├─ Guest with ID 123 not found
└─ Room with ID 5 not found
```

### Conflict Errors (409)
```
CONFLICT
├─ No available rooms for selected dates
├─ Duplicate room number
└─ Database constraint violation
```

### Authentication Errors (401)
```
UNAUTHORIZED
├─ Missing or invalid token
├─ Token expired
└─ Invalid credentials
```

### Permission Errors (403)
```
FORBIDDEN
├─ Only admins can delete users
├─ Insufficient permissions
└─ Cannot delete own user
```

---

## Payment Methods

| Method | Code | Example |
|--------|------|---------|
| Cash | `cash` | Manual transaction |
| Credit Card | `credit_card` | Card payment |
| Debit Card | `debit_card` | Bank debit |
| Bank Transfer | `bank_transfer` | Wire transfer |
| E-Wallet | `e_wallet` | Mobile payment |
| Check | `check` | Physical check |
| Other | `other` | Other method |

---

## Room Statuses

| Status | Meaning | Can Book |
|--------|---------|----------|
| `available` | Ready for guests | ✓ Yes |
| `occupied` | Guest currently in | ✗ No |
| `maintenance` | Under repair | ✗ No |
| `reserved` | Booked, not checked in | ✗ No |
| `blocked` | Blocked from booking | ✗ No |

---

## Reservation Statuses

| Status | Stage | Can Check In | Can Check Out |
|--------|-------|-------------|--------------|
| `confirmed` | Booked, not arrived | ✓ Yes | ✗ No |
| `checked_in` | Guest in room | ✗ No | ✓ Yes |
| `checked_out` | Guest left | ✗ No | ✗ No |
| `cancelled` | Cancelled | ✗ No | ✗ No |

---

## Payment Statuses

| Status | Meaning |
|--------|---------|
| `pending` | Awaiting payment |
| `partial_paid` | Some payment received |
| `paid_in_full` | All charges paid |
| `overpaid` | Paid more than due |

---

## Authentication

### Login
```bash
POST /api/auth/login
{
  "username": "admin",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

### Token Lifetime
- **Duration**: 16 hours (shift-based)
- **Type**: Bearer token
- **Include in requests**: `Authorization: Bearer {token}`

### User Roles
- **admin**: Full access (create, update, delete all resources)
- **user**: Limited access (create/read/update, no delete)

---

## Common Workflows

### Quick Check-In
```
1. Search reservation by confirmation #
2. Select available room
3. POST /api/reservations/{id}/check-in with room_id
4. Display receipt
```

### Record Payment
```
1. Select reservation
2. POST /api/payments with amount and method
3. Check updated balance
4. Confirm payment recorded
```

### Generate Receipt
```
1. GET /api/reservations/{id}/balance
2. GET /api/reservations/{id} (for details)
3. Format and print receipt
```

---

## Troubleshooting

### "Room not available"
- Check availability endpoint
- Verify dates don't overlap with existing bookings
- Try different room type or dates

### "Validation failed"
- Check date format: YYYY-MM-DD
- Verify all required fields
- Check field lengths and types
- Ensure occupancy is valid (adults + children ≤ 10)

### "Insufficient permissions"
- Verify user role (admin vs user)
- Check if action requires admin
- Confirm token is valid

### "Deposit amount exceeded"
- Deposit cannot be > total amount
- Reduce deposit or increase total
- Leave as 0 for no deposit

---

## Quick Tips

💡 **Always check availability before creating reservation**
- Prevents "room not available" errors
- Shows exact number of available rooms

💡 **Deposits default to 0**
- Only set deposit if needed
- Can override per reservation
- Always refundable

💡 **Record payments immediately**
- Keep balance tracking accurate
- Helps with checkout settlement
- Maintains payment history

💡 **Use confirmation numbers for lookup**
- Faster than reservation ID
- Guest-friendly format
- Unique per booking

💡 **Check balance before checkout**
- Verify all payments recorded
- Calculate deposit refund amount
- Ensure no outstanding balance

---

**Last Updated**: November 8, 2025
**Version**: 1.0 (Phase 8 Complete)
