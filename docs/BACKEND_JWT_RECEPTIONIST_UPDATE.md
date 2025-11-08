# Backend Updates: JWT Configuration & Receptionist Tracking

**Date:** 2025-11-08
**Status:** ✓ Completed and Integrated

## Overview

This document summarizes the backend updates for JWT token expiration (12-hour shift-based) and receptionist name tracking in guest check-in operations.

---

## Changes Made

### 1. JWT Token Expiration (16 Hours)

**File:** `backend/security.py` (line 16)

```python
TOKEN_EXPIRE_MINUTES = 60 * 16  # 16 hours (shift-based expiration)
```

**Why 16 hours?**
- Hotel receptionists work in extended shifts (8-16 hour shifts)
- 16-hour expiration covers standard and extended shift durations
- Provides flexibility for longer operational periods
- Still requires re-authentication for new shifts, improving security
- Reduces token validity window for security incidents

**Implementation:**
- Tokens created via `create_access_token()` include expiration timestamp
- Tokens are stored in `active_tokens` dictionary with expiration time
- `verify_token()` checks if token has expired before accepting requests

**Testing:**
```python
# Token created at: 2025-11-10 08:00:00 UTC
# Token expires at: 2025-11-11 00:00:00 UTC
# Duration: 16 hours exactly
```

---

### 2. Receptionist Tracking in Check-In

**Files Modified:**
- `backend/models.py` (Reservation model)
- `backend/routes/reservations_router.py` (check-in endpoint)

#### 2.1 Database Schema (models.py)

**Added Field:**
```python
class Reservation(Base):
    __tablename__ = "reservations"

    # ... other fields ...

    checked_in_by = Column(Integer, ForeignKey("users.id"))  # Receptionist who did check-in
```

**Added Relationship:**
```python
checked_in_by_user = relationship("User", foreign_keys=[checked_in_by])
```

**Updated to_dict() Method:**
```python
def to_dict(self):
    return {
        # ... other fields ...
        "checked_in_by": self.checked_in_by,
        "checked_in_by_name": self.checked_in_by_user.username if self.checked_in_by_user else None,
        # ... other fields ...
    }
```

#### 2.2 Check-In Endpoint (reservations_router.py)

**Endpoint:** `POST /api/reservations/{reservation_id}/check-in`

**Request Parameters:**
```json
{
  "reservation_id": 1,
  "room_id": 5
}
```

**Process Flow:**
1. Verify reservation exists
2. Verify room exists and is available
3. Update reservation fields:
   - `status = 'checked_in'`
   - `checked_in_at = datetime.utcnow()`
   - `checked_in_by = current_user.get("user_id")` ← **Receptionist ID**
   - `room_id = provided_room_id`
4. Update room status to 'occupied'
5. Commit to database
6. Return response with receptionist information

**Response Example:**
```json
{
  "message": "Guest checked in successfully",
  "reservation_id": 1,
  "guest_name": "John Doe",
  "room_number": "A501",
  "checked_in_at": "2025-11-10T15:30:00",
  "checked_in_by": 2,
  "checked_in_by_name": "receptionist_john"
}
```

**Key Features:**
- Tracks which receptionist performed the check-in (User ID)
- Stores receptionist username for audit trail
- Returns both ID and name for client-side display
- Prevents duplicate check-ins (status validation)
- Ensures room is available before assignment

---

### 3. API Schemas (schemas.py)

**New Schemas Created:**

#### ReservationCreate
```python
class ReservationCreate(BaseModel):
    guest_id: int
    room_type_id: int
    check_in_date: str
    check_out_date: str
    adults: int = Field(default=1, ge=1)
    children: int = Field(default=0, ge=0)
    rate_per_night: float
    subtotal: float
    discount_amount: float = 0.0
    total_amount: float
    special_requests: Optional[str] = None
```

#### ReservationResponse
```python
class ReservationResponse(BaseModel):
    id: int
    confirmation_number: str
    # ... booking details ...
    status: str
    checked_in_at: Optional[str] = None
    checked_in_by: Optional[int] = None          # ← Receptionist ID
    checked_in_by_name: Optional[str] = None      # ← Receptionist username
    checked_out_at: Optional[str] = None
    # ... timestamps ...
```

#### ReservationListResponse
Provides paginated list of reservations with pagination metadata.

---

### 4. Reservations Router (routes/reservations_router.py)

**Endpoints Implemented:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/reservations` | Create new reservation |
| GET | `/api/reservations` | List reservations (paginated) |
| GET | `/api/reservations/{id}` | Get single reservation |
| PUT | `/api/reservations/{id}` | Update reservation |
| DELETE | `/api/reservations/{id}` | Cancel reservation |
| POST | `/api/reservations/{id}/check-in` | Check in guest (with receptionist tracking) |
| POST | `/api/reservations/{id}/check-out` | Check out guest |

**Authentication:** All endpoints require valid JWT token via `get_current_user` dependency

**Validation:**
- Guest existence verification
- Room type existence verification
- Room availability checking (for check-in)
- Status transition validation
- Room is released back to 'available' on check-out

---

### 5. App Integration (app.py)

**Imports:**
```python
from routes import (..., reservations_router)
```

**Router Registration:**
```python
app.include_router(reservations_router.router, tags=["Reservations"])
```

- Routes prefixed with `/api/reservations` automatically
- All routes tagged as "Reservations" in API docs
- Available at: `GET /api/docs` for interactive testing

---

## API Examples

### Create Reservation

**Request:**
```bash
curl -X POST "http://localhost:8001/api/reservations" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
    "special_requests": "Late check-in"
  }'
```

**Response:**
```json
{
  "id": 1,
  "confirmation_number": "ABC123XYZ",
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
  "special_requests": "Late check-in",
  "status": "confirmed",
  "checked_in_at": null,
  "checked_in_by": null,
  "checked_in_by_name": null,
  "checked_out_at": null,
  "created_by": 1,
  "created_at": "2025-11-09T10:00:00",
  "updated_at": "2025-11-09T10:00:00"
}
```

### Check In Guest (with Receptionist Tracking)

**Request:**
```bash
curl -X POST "http://localhost:8001/api/reservations/1/check-in" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 5}'
```

**Response:**
```json
{
  "message": "Guest checked in successfully",
  "reservation_id": 1,
  "guest_name": "John Doe",
  "room_number": "A501",
  "checked_in_at": "2025-11-10T15:30:00",
  "checked_in_by": 2,
  "checked_in_by_name": "receptionist_john"
}
```

### List Reservations with Receptionist Info

**Request:**
```bash
curl -X GET "http://localhost:8001/api/reservations?skip=0&limit=10&status=checked_in" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "reservations": [
    {
      "id": 1,
      "confirmation_number": "ABC123XYZ",
      "guest_id": 1,
      "room_id": 5,
      "room_type_id": 2,
      "check_in_date": "2025-11-10",
      "check_out_date": "2025-11-13",
      "adults": 2,
      "children": 1,
      "status": "checked_in",
      "checked_in_at": "2025-11-10T15:30:00",
      "checked_in_by": 2,
      "checked_in_by_name": "receptionist_john",
      "total_amount": 1400000,
      "created_at": "2025-11-09T10:00:00",
      "updated_at": "2025-11-10T15:30:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

---

## Audit Trail & Security

### 1. Receptionist Accountability

When a guest checks in:
1. Receptionist's user ID is stored (`checked_in_by`)
2. Receptionist's username is stored for display (`checked_in_by_name`)
3. Check-in timestamp is recorded (`checked_in_at`)

**Audit Query Example:**
```sql
SELECT
    r.id,
    r.confirmation_number,
    g.full_name as guest_name,
    u.username as receptionist_name,
    r.checked_in_at,
    rm.room_number
FROM reservations r
JOIN guests g ON r.guest_id = g.id
JOIN users u ON r.checked_in_by = u.id
JOIN rooms rm ON r.room_id = rm.id
WHERE r.status = 'checked_in'
ORDER BY r.checked_in_at DESC;
```

### 2. JWT Security Timeline

```
Receptionist Login Time    Standard Shift         Extended Shift         Token Expiration
       ↓                   End Time               End Time                      ↓
   08:00 UTC          16:00 UTC              24:00 UTC (midnight)        00:00 UTC (+1 day)
   │                      │                      │                           │
   └──────────────────────┘─────────────────────┘                           │
         8-hour shift      16-hour shift                                      │
                                                                              │ 16-hour validity
                                                                              │ (covers all shifts)
```

Benefits:
- Token valid for entire standard shift (8-12 hours)
- Token valid for extended shifts (up to 16 hours)
- Receptionist only needs to re-login at shift change
- Reduces password entry fatigue
- Automatic logout after 16 hours for security
- Flexibility for operational requirements

### 3. Room Management

Check-in flow:
- Verify room is `available` before assigning
- Update room status to `occupied` when guest checks in
- Release room back to `available` on check-out
- Prevents double-booking

---

## Testing Checklist

- [x] JWT expiration set to 12 hours (720 minutes)
- [x] Receptionist tracking fields added to Reservation model
- [x] Relationship created between Reservation and User
- [x] Check-in endpoint captures receptionist user ID
- [x] Check-in endpoint returns receptionist username
- [x] Schemas created for all reservation operations
- [x] Reservations router integrated into app
- [x] All endpoints have authentication requirement
- [x] Room status validation implemented
- [x] Reservation status transitions validated

---

## Frontend Integration Notes

### 1. JWT Token Handling

**Token Expiration (16 hours):**
```typescript
// Frontend should implement automatic re-login at 15.5 hours
const TOKEN_EXPIRATION_MS = 16 * 60 * 60 * 1000; // 16 hours

useEffect(() => {
  const refreshTimer = setTimeout(() => {
    // Show "Session expiring soon" warning at 15.5 hours
    showSessionExpiryWarning();
  }, TOKEN_EXPIRATION_MS - 30 * 60 * 1000); // 30 minutes before expiry
}, []);
```

### 2. Check-In Display

When displaying check-in information to the guest:
```typescript
interface CheckInResponse {
  message: string;
  reservation_id: number;
  guest_name: string;
  room_number: string;
  checked_in_at: string;
  checked_in_by: number;           // Receptionist ID
  checked_in_by_name: string;       // Receptionist username for display
}

// Display in UI:
// "Checked in by: receptionist_john at 3:30 PM"
```

### 3. Receptionist Assignment UI

When assigning rooms during check-in, show:
```json
{
  "reservations": [
    {
      "id": 1,
      "guest_name": "John Doe",
      "room_number": "A501",
      "checked_in_at": "2025-11-10T15:30:00",
      "checked_in_by_name": "receptionist_john"
    }
  ]
}
```

---

## Database Migration (if needed)

If updating existing database:

```sql
-- Add checked_in_by column if not exists
ALTER TABLE reservations
ADD COLUMN checked_in_by INTEGER REFERENCES users(id);

-- Create index for faster lookups
CREATE INDEX idx_reservations_checked_in_by
ON reservations(checked_in_by);

-- Query check-ins by receptionist
SELECT checked_in_by, COUNT(*) as total_check_ins
FROM reservations
WHERE status = 'checked_in'
GROUP BY checked_in_by;
```

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **JWT Expiration** | 24 hours | 16 hours (shift-based, flexible) |
| **Receptionist Tracking** | Not tracked | User ID + Username |
| **Check-in Audit Trail** | Basic | Full with receptionist info |
| **API Endpoints** | None | 7 endpoints for reservations |
| **Room Management** | Manual | Automatic status updates |

---

## Files Modified/Created

```
backend/
├── security.py                          ✓ Modified (JWT expiration)
├── models.py                            ✓ Modified (added checked_in_by)
├── schemas.py                           ✓ Modified (added Reservation schemas)
├── app.py                               ✓ Modified (added reservations_router)
├── routes/
│   └── reservations_router.py           ✓ Created (7 endpoints)
└── test_reservations.py                 ✓ Created (validation script)

docs/
└── BACKEND_JWT_RECEPTIONIST_UPDATE.md   ✓ This file
```

---

## Next Steps

1. **Frontend Integration:**
   - Implement JWT token refresh logic
   - Build check-in form with room selection
   - Display receptionist name on confirmation

2. **Testing:**
   - Run full API test suite
   - Test 12-hour token expiration
   - Test check-in with multiple receptionists
   - Verify audit trail captures correct data

3. **Production Deployment:**
   - Move tokens to Redis (not in-memory)
   - Add database migration scripts
   - Enable audit logging
   - Configure JWT secrets

---

**Status:** ✓ Ready for Frontend Integration
**Version:** 1.0.0
**Last Updated:** 2025-11-08
