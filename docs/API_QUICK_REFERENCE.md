# Hotel Management System - API Endpoints Quick Reference

## Quick Navigation

### Authentication
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user

### Guests
- `POST /api/guests` - Create guest
- `GET /api/guests` - List guests
- `GET /api/guests/{id}` - Get guest
- `PUT /api/guests/{id}` - Update guest
- `DELETE /api/guests/{id}` - Delete guest

### Reservations
- `GET /api/reservations/availability` - Check availability
- `POST /api/reservations` - Create reservation
- `GET /api/reservations` - List reservations
- `GET /api/reservations/{id}` - Get reservation
- `GET /api/reservations/{id}/balance` - Get balance
- `PUT /api/reservations/{id}` - Update reservation
- `DELETE /api/reservations/{id}` - Cancel reservation
- `POST /api/reservations/{id}/check-in` - Check in guest
- `POST /api/reservations/{id}/check-out` - Check out guest

### Payments
- `POST /api/payments` - Create payment
- `GET /api/payments` - List payments
- `GET /api/payments/{id}` - Get payment
- `PUT /api/payments/{id}` - Update payment
- `DELETE /api/payments/{id}` - Delete payment

### Rooms
- `GET /api/rooms` - List rooms
- `GET /api/rooms/{id}` - Get room

### Dashboard
- `GET /api/dashboard/today` - Today's metrics
- `GET /api/dashboard/metrics` - Period metrics

### System
- `GET /health` - Health check
- `GET /api` - API info

---

## Authentication Header
All requests (except /health and /api) require:
```
Authorization: Bearer {access_token}
```

---

## Common Request/Response Examples

### 1. Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin"
  }
}
```

### 2. Create Guest
```bash
POST /api/guests
Authorization: Bearer {token}

{
  "full_name": "John Doe",
  "id_type": "passport",
  "id_number": "A12345678"
}

Response: 201 Created
{
  "id": 1,
  "full_name": "John Doe",
  "id_type": "passport",
  "id_number": "A12345678"
}
```

### 3. Check Availability
```bash
GET /api/reservations/availability?room_type_id=2&check_in_date=2025-11-10&check_out_date=2025-11-13
Authorization: Bearer {token}

Response:
{
  "available_rooms": 5,
  "total_rooms": 10,
  "is_available": true
}
```

### 4. Create Reservation
```bash
POST /api/reservations
Authorization: Bearer {token}

{
  "guest_id": 1,
  "room_type_id": 2,
  "check_in_date": "2025-11-10",
  "check_out_date": "2025-11-13",
  "adults": 1,
  "children": 0,
  "rate_per_night": 500000,
  "subtotal": 1500000,
  "discount_amount": 0,
  "total_amount": 1500000,
  "deposit_amount": 500000
}

Response: 201 Created
{
  "id": 1,
  "confirmation_number": "ABC123XYZ",
  "status": "confirmed",
  "total_amount": 1500000,
  "balance": 1500000
}
```

### 5. Record Payment
```bash
POST /api/payments
Authorization: Bearer {token}

{
  "reservation_id": 1,
  "amount": 500000,
  "payment_date": "2025-11-08",
  "payment_method": "bank_transfer",
  "payment_type": "downpayment"
}

Response: 201 Created
{
  "message": "Payment recorded successfully",
  "payment": {
    "id": 1,
    "amount": 500000,
    "payment_method": "bank_transfer"
  }
}
```

### 6. Check-In Guest
```bash
POST /api/reservations/1/check-in?room_id=101
Authorization: Bearer {token}

Response:
{
  "message": "Guest checked in successfully",
  "confirmation_number": "ABC123XYZ",
  "room_number": "101",
  "checked_in_by_name": "receptionist_john",
  "total_paid": 500000,
  "balance": 1000000
}
```

### 7. Check-Out Guest
```bash
POST /api/reservations/1/check-out
Authorization: Bearer {token}

Response:
{
  "message": "Guest checked out successfully",
  "deposit_settlement": {
    "deposit_held": 500000,
    "balance_owed": 0,
    "to_refund": 500000
  }
}
```

### 8. Get Balance
```bash
GET /api/reservations/1/balance
Authorization: Bearer {token}

Response:
{
  "total_amount": 1500000,
  "total_paid": 1500000,
  "balance": 0,
  "deposit_amount": 500000,
  "final_balance_after_deposit": 0,
  "payment_status": "fully_paid"
}
```

---

## Query Parameters

### Pagination (all list endpoints)
- `skip=0` - Records to skip
- `limit=10` - Records to return

### Filters
- Reservations: `status=confirmed`, `guest_id=1`
- Payments: `reservation_id=1`, `status=paid`
- Rooms: None currently

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 402 | Payment Required |
| 404 | Not Found |
| 409 | Conflict |
| 500 | Server Error |

---

## Important Notes

### Date Format
All dates: `YYYY-MM-DD`
All times: `YYYY-MM-DDTHH:MM:SS`

### Monetary Values
All amounts are numeric with 2 decimal places
Handle as: `amount: 1500000` (in local currency)

### Reservation Status Flow
`confirmed` → `checked_in` → `checked_out` (or `cancelled`)

### Payment Types
- `full` - Full payment
- `downpayment` - Partial advance payment
- `deposit` - Security deposit
- `adjustment` - Payment correction

### Payment Methods
- `cash`
- `credit_card`
- `debit_card`
- `bank_transfer`
- `e_wallet`
- `other`

### Room Status
- `available` - Ready for occupancy
- `occupied` - Guest checked in
- `out_of_order` - Maintenance needed

---

## Error Examples

### Validation Error (400)
```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD"
}
```

### Unauthorized (401)
```json
{
  "detail": "Invalid or expired token"
}
```

### Not Found (404)
```json
{
  "detail": "Guest with ID 999 not found"
}
```

### Conflict (409)
```json
{
  "detail": "No available rooms of type 'Double Room' for the selected dates"
}
```

---

## Testing with curl

```bash
# Login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'

# Get current user
curl -X GET http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer {token}"

# List guests
curl -X GET "http://localhost:8001/api/guests?skip=0&limit=10" \
  -H "Authorization: Bearer {token}"

# Check availability
curl -X GET "http://localhost:8001/api/reservations/availability?room_type_id=2&check_in_date=2025-11-10&check_out_date=2025-11-13" \
  -H "Authorization: Bearer {token}"

# Create payment
curl -X POST http://localhost:8001/api/payments \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "reservation_id": 1,
    "amount": 500000,
    "payment_date": "2025-11-08",
    "payment_method": "bank_transfer"
  }'
```

---

## Frontend Integration Tips

1. **Store token in localStorage or sessionStorage**
   ```javascript
   localStorage.setItem('access_token', response.access_token);
   ```

2. **Add token to all requests**
   ```javascript
   headers: {
     'Authorization': `Bearer ${localStorage.getItem('access_token')}`
   }
   ```

3. **Handle token expiration (16 hours)**
   - Implement token refresh or redirect to login
   - Store login time and warn user

4. **Use confirmation numbers for guest communication**
   - Display on booking confirmation
   - Use for check-in lookup

5. **Format currency values**
   ```javascript
   new Intl.NumberFormat('id-ID', {
     style: 'currency',
     currency: 'IDR'
   }).format(1500000);
   ```

---

## Swagger/OpenAPI Documentation

Access interactive API documentation:
- Swagger UI: `http://localhost:8001/api/docs`
- OpenAPI JSON: `http://localhost:8001/api/openapi.json`

All endpoints, request/response schemas, and status codes documented there.
