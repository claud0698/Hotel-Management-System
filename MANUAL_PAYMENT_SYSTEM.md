# Manual Payment System Documentation

## Overview

The manual payment system allows administrators to easily record tenant payments by specifying the period/duration (in months) instead of manually calculating amounts and due dates. The system automatically:

- Calculates the total payment amount based on the room's monthly rate
- Sets the due date (current date + number of months)
- Stores the period information for tracking
- Supports both pending and paid status

## Features Implemented

### 1. Database Schema Updates

#### Payment Model (`models.py`)
- Added `period_months` column (Integer, default=1)
- Tracks how many months each payment covers
- Updated `to_dict()` method to include `period_months` in responses

### 2. New Schema

#### ManualPaymentCreate (`schemas.py`)
```python
{
    "tenant_id": int,              # Required: tenant ID
    "period_months": int,          # Required: 1-12 months
    "status": str,                 # Optional: "pending" or "paid" (default: "pending")
    "payment_method": str,         # Optional: "cash", "transfer", etc.
    "receipt_number": str,         # Optional: receipt/reference number
    "notes": str                   # Optional: payment notes
}
```

### 3. API Endpoint

#### POST `/api/payments/manual/create`

**Request:**
```json
{
    "tenant_id": 1,
    "period_months": 2,
    "status": "pending",
    "payment_method": "cash",
    "notes": "First payment"
}
```

**Response (201 Created):**
```json
{
    "message": "Manual payment created for 2 month(s)",
    "payment": {
        "id": 5,
        "tenant_id": 1,
        "amount": 1000000.0,
        "due_date": "2025-12-24T16:52:20.583898",
        "paid_date": null,
        "status": "pending",
        "period_months": 2,
        "payment_method": "cash",
        "receipt_number": null,
        "notes": "Payment for 2 month(s)",
        "created_at": "2025-10-24T16:52:20.584416",
        "updated_at": "2025-10-24T16:52:20.584417"
    },
    "details": {
        "tenant_name": "John Doe",
        "room_number": "A1",
        "monthly_rate": 500000.0,
        "period_months": 2,
        "total_amount": 1000000.0,
        "due_date": "2025-12-24T16:52:20.583898+00:00"
    }
}
```

**Error Responses:**

```json
// Tenant not found (404)
{
    "detail": "Tenant with ID {id} not found"
}

// Tenant not in a room (400)
{
    "detail": "Tenant {name} has no room assigned"
}

// Room not found (400)
{
    "detail": "Room not found for tenant"
}

// Invalid period (422)
{
    "detail": [
        {
            "loc": ["body", "period_months"],
            "msg": "ensure this value is greater than or equal to 1",
            "type": "value_error.number.not_ge"
        }
    ]
}
```

## Payment Calculation Logic

### Amount Calculation
```
Total Amount = Room Monthly Rate × Period Months
```

Example: Room A1 (500,000 IDR/month) × 2 months = 1,000,000 IDR

### Due Date Calculation
```
Due Date = Today + Period Months
```

Using `python-dateutil.relativedelta` for accurate month addition.

### Status Handling
- If status is set to "pending": `paid_date` remains null
- If status is set to "paid": `paid_date` is automatically set to current timestamp

## Room Seeding

### Room Configuration (A1-A12, B1-B12)

**Location:** `backend/seed_rooms_simple.py`

**Command:**
```bash
python seed_rooms_simple.py
```

**Generated Rooms:**
- Floor A: A1 to A12 (12 rooms)
- Floor B: B1 to B12 (12 rooms)
- Total: 24 rooms
- Monthly Rate: 500,000 IDR per room
- Room Type: Single room
- Amenities: WiFi, AC, Bed, Table
- Status: All available (until assigned to tenants)

## Server Configuration

### Port
- Default: 8001
- Set via environment variable: `PORT=8001`
- Modified in `app.py` line 139

### CORS Configuration
- Testing Mode: All origins allowed (`*`)
- Can be restricted via `CORS_ORIGINS` environment variable
- Format: comma-separated list of URLs (e.g., `http://localhost:3000,http://localhost:5173`)

## Dependencies

### New Dependency Added
```
python-dateutil==2.8.2
```

Added to `requirements.txt` for handling month calculations.

## Testing

### Test Script
**Location:** `/tmp/test_simple.sh`

**What it does:**
1. Kills existing servers
2. Starts fresh server on port 8001
3. Creates test tenant in room A1
4. Tests manual payment creation for 2 months
5. Shows full response

**Run:**
```bash
bash /tmp/test_simple.sh
```

### Example Test Result

```
Testing manual payment endpoint for 2 months...
{
    "message": "Manual payment created for 2 month(s)",
    "payment": {
        "id": 5,
        "tenant_id": 3,
        "amount": 1000000.0,
        "due_date": "2025-12-24T16:52:20.583898",
        "paid_date": null,
        "status": "pending",
        "period_months": 2,
        "payment_method": "cash",
        "receipt_number": null,
        "notes": "Payment for 2 month(s)",
        "created_at": "2025-10-24T16:52:20.584416",
        "updated_at": "2025-10-24T16:52:20.584417"
    },
    "details": {
        "tenant_name": "John Doe",
        "room_number": "A1",
        "monthly_rate": 500000.0,
        "period_months": 2,
        "total_amount": 1000000.0,
        "due_date": "2025-12-24T16:52:20.583898+00:00"
    }
}
```

## Usage Examples

### Example 1: Simple 1-month payment (pending)
```bash
curl -X POST http://localhost:8001/api/payments/manual/create \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": 1,
    "period_months": 1,
    "status": "pending",
    "payment_method": "cash"
  }'
```

### Example 2: 3-month payment (already paid with receipt)
```bash
curl -X POST http://localhost:8001/api/payments/manual/create \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": 2,
    "period_months": 3,
    "status": "paid",
    "payment_method": "transfer",
    "receipt_number": "TRF001",
    "notes": "Advanced payment for 3 months"
  }'
```

### Example 3: Maximum 12-month payment (full year)
```bash
curl -X POST http://localhost:8001/api/payments/manual/create \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": 3,
    "period_months": 12,
    "status": "pending",
    "payment_method": "transfer"
  }'
```

## Database

### Reset Database (if needed)
```bash
# Delete existing database
rm kos.db

# Recreate and seed
python -c "from app import Base, engine; Base.metadata.create_all(bind=engine)"
python seed_rooms_simple.py
```

### Verify Rooms
```bash
curl http://localhost:8001/api/rooms | python3 -m json.tool | head -50
```

## Files Modified/Created

### Modified Files
1. `backend/models.py` - Added `period_months` column to Payment model
2. `backend/schemas.py` - Added `ManualPaymentCreate` schema, updated `PaymentResponse`
3. `backend/routes/payments_router.py` - Added manual payment creation endpoint
4. `backend/requirements.txt` - Added `python-dateutil==2.8.2`
5. `backend/app.py` - Changed default port from 5000 to 8001, disabled CORS for testing

### Created Files
1. `backend/seed_rooms_simple.py` - Room seeding script for A1-A12 and B1-B12
2. `/tmp/test_simple.sh` - Test script for manual payment system

## Future Enhancements

1. **Bulk Payment Creation** - Create payments for multiple months at once
2. **Payment Plans** - Auto-generate recurring payments
3. **Payment Reminders** - Email notifications before due date
4. **Payment History** - Track payment updates and status changes
5. **Reports** - Generate payment reports by tenant/period/status
6. **Advanced Filtering** - Filter payments by date range, amount, etc.

## Support & Troubleshooting

### Issue: "Tenant has no room assigned"
**Solution:** Assign a room to the tenant before creating a payment
```bash
curl -X PUT http://localhost:8001/api/tenants/1 \
  -H "Content-Type: application/json" \
  -d '{"current_room_id": 1}'
```

### Issue: "Room not found for tenant"
**Cause:** The tenant's `current_room_id` doesn't exist in the rooms table
**Solution:** Create the room first or ensure room IDs match

### Issue: Port 8001 already in use
**Solution:** Kill existing processes and restart
```bash
lsof -i :8001 -t | xargs kill -9
python app.py
```

### Issue: Missing `dateutil` module
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

## Summary

The manual payment system successfully simplifies admin payment recording by:
- Requiring only period (months) instead of exact calculations
- Automatically calculating amounts based on room rates
- Automatically setting due dates
- Supporting both pending and paid status
- Providing detailed payment information and tracking

All features tested and working on port 8001 with 24 pre-seeded rooms (A1-A12, B1-B12).
