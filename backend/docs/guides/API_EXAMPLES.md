# Rooms & Reservations - API Examples

**Purpose**: Complete curl and JSON examples for all API endpoints

**Last Updated**: November 8, 2025

---

## Table of Contents

1. [Authentication](#authentication)
2. [Room Type Management](#room-type-management)
3. [Room Management](#room-management)
4. [Guest Management](#guest-management)
5. [Reservation Management](#reservation-management)
6. [Payment Management](#payment-management)
7. [Error Responses](#error-responses)

---

## Authentication

All endpoints require a Bearer token in the Authorization header.

### Login

```bash
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response** (200 OK):
```json
{
  "access_token": "rB3vD2nJ4kL5mP9qR8sT1vW4xY7zC6dE",
  "token_type": "Bearer",
  "user_id": 1,
  "username": "admin",
  "role": "admin"
}
```

### Using Token in Requests

```bash
export TOKEN="rB3vD2nJ4kL5mP9qR8sT1vW4xY7zC6dE"

curl -X GET "http://localhost:8001/api/rooms" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Room Type Management

### List Room Types

```bash
curl -X GET "http://localhost:8001/api/room-types" \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 1,
      "name": "Deluxe Double",
      "description": "Spacious room with queen bed",
      "capacity": 2,
      "base_rate": 500000,
      "amenities": ["WiFi", "AC", "TV", "Mini Bar"],
      "created_at": "2025-11-01T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Standard Single",
      "description": "Compact room with single bed",
      "capacity": 1,
      "base_rate": 300000,
      "amenities": ["WiFi", "AC"],
      "created_at": "2025-11-01T10:00:00Z"
    }
  ],
  "total": 2
}
```

### Create Room Type

```bash
curl -X POST "http://localhost:8001/api/room-types" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deluxe Suite",
    "description": "Premium suite with living area",
    "capacity": 4,
    "base_rate": 1200000,
    "amenities": ["WiFi", "AC", "TV", "Mini Bar", "Bathtub", "Balcony"]
  }'
```

**Response** (201 Created):
```json
{
  "id": 3,
  "name": "Deluxe Suite",
  "description": "Premium suite with living area",
  "capacity": 4,
  "base_rate": 1200000,
  "amenities": ["WiFi", "AC", "TV", "Mini Bar", "Bathtub", "Balcony"],
  "created_at": "2025-11-08T14:00:00Z"
}
```

### Get Room Type Details

```bash
curl -X GET "http://localhost:8001/api/room-types/1" \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Deluxe Double",
  "description": "Spacious room with queen bed",
  "capacity": 2,
  "base_rate": 500000,
  "amenities": ["WiFi", "AC", "TV", "Mini Bar"],
  "created_at": "2025-11-01T10:00:00Z",
  "room_count": 10,
  "available_count": 7
}
```

---

## Room Management

### List Rooms with Pagination

```bash
curl -X GET "http://localhost:8001/api/rooms?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 101,
      "room_number": "101",
      "room_type_id": 1,
      "room_type_name": "Deluxe Double",
      "status": "available",
      "custom_rate": null,
      "base_rate": 500000,
      "floor": 1,
      "notes": "Renovated 2025",
      "created_at": "2025-11-01T10:00:00Z"
    },
    {
      "id": 102,
      "room_number": "102",
      "room_type_id": 1,
      "room_type_name": "Deluxe Double",
      "status": "occupied",
      "custom_rate": null,
      "base_rate": 500000,
      "floor": 1,
      "notes": null,
      "created_at": "2025-11-01T10:00:00Z"
    }
  ],
  "total": 40,
  "page": 1,
  "page_size": 10
}
```

### Create Room

```bash
curl -X POST "http://localhost:8001/api/rooms" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "room_number": "401",
    "room_type_id": 1,
    "floor": 4,
    "status": "available",
    "custom_rate": 600000,
    "notes": "Corner room with extra space"
  }'
```

**Response** (201 Created):
```json
{
  "id": 201,
  "room_number": "401",
  "room_type_id": 1,
  "room_type_name": "Deluxe Double",
  "status": "available",
  "custom_rate": 600000,
  "base_rate": 500000,
  "floor": 4,
  "notes": "Corner room with extra space",
  "created_at": "2025-11-08T14:15:00Z"
}
```

### Get Room Details

```bash
curl -X GET "http://localhost:8001/api/rooms/101" \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "id": 101,
  "room_number": "101",
  "room_type_id": 1,
  "room_type_name": "Deluxe Double",
  "room_type_capacity": 2,
  "room_type_amenities": ["WiFi", "AC", "TV", "Mini Bar"],
  "status": "available",
  "custom_rate": null,
  "base_rate": 500000,
  "floor": 1,
  "notes": "Renovated 2025",
  "images": [
    {
      "id": 1,
      "room_id": 101,
      "image_url": "https://example.com/room101.jpg",
      "uploaded_at": "2025-11-01T10:00:00Z"
    }
  ],
  "created_at": "2025-11-01T10:00:00Z"
}
```

### Update Room

```bash
curl -X PUT "http://localhost:8001/api/rooms/101" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "out_of_order",
    "custom_rate": null,
    "notes": "Maintenance: AC repair in progress"
  }'
```

**Response** (200 OK):
```json
{
  "id": 101,
  "room_number": "101",
  "room_type_id": 1,
  "room_type_name": "Deluxe Double",
  "status": "out_of_order",
  "custom_rate": null,
  "base_rate": 500000,
  "floor": 1,
  "notes": "Maintenance: AC repair in progress",
  "updated_at": "2025-11-08T14:20:00Z"
}
```

### Delete Room

```bash
curl -X DELETE "http://localhost:8001/api/rooms/101" \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "message": "Room deleted successfully",
  "room_id": 101
}
```

**Error** - Cannot delete if active reservations (409 Conflict):
```json
{
  "detail": "Cannot delete room with active reservations",
  "error_code": "ROOM_IN_USE",
  "active_reservations": 1
}
```

---

## Guest Management

### Create Guest

```bash
curl -X POST "http://localhost:8001/api/guests" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "+62812345678",
    "country": "Indonesia",
    "id_type": "passport",
    "id_number": "A123456789",
    "address": "123 Main St"
  }'
```

**Response** (201 Created):
```json
{
  "id": 10,
  "name": "John Doe",
  "email": "john@example.com",
  "phone_number": "+62812345678",
  "country": "Indonesia",
  "id_type": "passport",
  "id_number": "A123456789",
  "address": "123 Main St",
  "created_at": "2025-11-08T14:30:00Z"
}
```

### List Guests with Filter

```bash
# Get all guests from specific country
curl -X GET "http://localhost:8001/api/guests?country=Indonesia&page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 1,
      "name": "Budi Santoso",
      "email": "budi@example.com",
      "phone_number": "+62812345678",
      "country": "Indonesia",
      "created_at": "2025-11-01T10:00:00Z"
    },
    {
      "id": 10,
      "name": "John Doe",
      "email": "john@example.com",
      "phone_number": "+62812345678",
      "country": "Indonesia",
      "created_at": "2025-11-08T14:30:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

### Get Guest Details

```bash
curl -X GET "http://localhost:8001/api/guests/10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "id": 10,
  "name": "John Doe",
  "email": "john@example.com",
  "phone_number": "+62812345678",
  "country": "Indonesia",
  "id_type": "passport",
  "id_number": "A123456789",
  "address": "123 Main St",
  "created_at": "2025-11-08T14:30:00Z",
  "reservation_count": 2,
  "total_spent": 1500000
}
```

---

## Reservation Management

### Check Availability

```bash
curl -X GET "http://localhost:8001/api/reservations/availability" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "room_type_id": 1,
    "check_in": "2025-11-15",
    "check_out": "2025-11-17"
  }'
```

**Response** (200 OK):
```json
{
  "room_type_id": 1,
  "check_in_date": "2025-11-15",
  "check_out_date": "2025-11-17",
  "available_rooms": 7,
  "total_rooms": 10,
  "is_available": true,
  "message": "7 rooms available for selected dates"
}
```

**Response** (No availability - 409):
```json
{
  "room_type_id": 1,
  "check_in_date": "2025-12-23",
  "check_out_date": "2025-12-25",
  "available_rooms": 0,
  "total_rooms": 10,
  "is_available": false,
  "message": "No rooms available for selected dates"
}
```

### Create Reservation

```bash
curl -X POST "http://localhost:8001/api/reservations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "guest_id": 10,
    "room_type_id": 1,
    "check_in_date": "2025-11-15",
    "check_out_date": "2025-11-17",
    "total_amount": 1000000,
    "deposit_amount": 500000,
    "notes": "2-night stay with breakfast included"
  }'
```

**Response** (201 Created):
```json
{
  "id": 42,
  "confirmation_number": "a1b2c3d4e5",
  "guest_id": 10,
  "guest_name": "John Doe",
  "room_type_id": 1,
  "room_type_name": "Deluxe Double",
  "check_in_date": "2025-11-15",
  "check_out_date": "2025-11-17",
  "total_amount": 1000000,
  "deposit_amount": 500000,
  "status": "confirmed",
  "room_id": null,
  "created_at": "2025-11-08T15:00:00Z",
  "notes": "2-night stay with breakfast included"
}
```

### List Reservations with Filters

```bash
# Get all confirmed reservations
curl -X GET "http://localhost:8001/api/reservations?status=confirmed&page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"

# Get reservations for specific guest
curl -X GET "http://localhost:8001/api/reservations?guest_id=10&page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"

# Get checked-in reservations
curl -X GET "http://localhost:8001/api/reservations?status=checked_in" \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 42,
      "confirmation_number": "a1b2c3d4e5",
      "guest_name": "John Doe",
      "room_type_name": "Deluxe Double",
      "check_in_date": "2025-11-15",
      "check_out_date": "2025-11-17",
      "total_amount": 1000000,
      "status": "confirmed",
      "created_at": "2025-11-08T15:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20
}
```

### Get Reservation Details

```bash
curl -X GET "http://localhost:8001/api/reservations/42" \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "id": 42,
  "confirmation_number": "a1b2c3d4e5",
  "guest_id": 10,
  "guest_name": "John Doe",
  "guest_email": "john@example.com",
  "room_type_id": 1,
  "room_type_name": "Deluxe Double",
  "room_id": null,
  "room_number": null,
  "check_in_date": "2025-11-15",
  "check_out_date": "2025-11-17",
  "total_amount": 1000000,
  "deposit_amount": 500000,
  "status": "confirmed",
  "checked_in_at": null,
  "checked_in_by": null,
  "checked_in_by_name": null,
  "checked_out_at": null,
  "deposit_returned_at": null,
  "created_at": "2025-11-08T15:00:00Z",
  "created_by": 1,
  "notes": "2-night stay with breakfast included",
  "payments": [
    {
      "id": 50,
      "amount": 500000,
      "payment_type": "card",
      "payment_date": "2025-11-08T15:05:00Z"
    }
  ],
  "total_paid": 500000,
  "balance": 500000
}
```

### Update Reservation

```bash
# Update dates (only before check-in)
curl -X PUT "http://localhost:8001/api/reservations/42" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "check_in_date": "2025-11-16",
    "check_out_date": "2025-11-18",
    "notes": "Updated to 2-night stay starting Nov 16"
  }'
```

**Response** (200 OK):
```json
{
  "id": 42,
  "confirmation_number": "a1b2c3d4e5",
  "guest_name": "John Doe",
  "check_in_date": "2025-11-16",
  "check_out_date": "2025-11-18",
  "status": "confirmed",
  "notes": "Updated to 2-night stay starting Nov 16",
  "updated_at": "2025-11-08T15:10:00Z"
}
```

### Check-in Reservation

```bash
curl -X POST "http://localhost:8001/api/reservations/42/check-in" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 105,
    "require_payment": false
  }'
```

**Response** (200 OK):
```json
{
  "id": 42,
  "confirmation_number": "a1b2c3d4e5",
  "guest_name": "John Doe",
  "room_id": 105,
  "room_number": "105",
  "room_type_name": "Deluxe Double",
  "status": "checked_in",
  "checked_in_at": "2025-11-15T14:30:00Z",
  "checked_in_by": 2,
  "checked_in_by_name": "Maria Garcia",
  "total_amount": 1000000,
  "total_paid": 500000,
  "balance": 500000,
  "deposit_held": 500000,
  "payment_status": "Partial: 500000/1000000 IDR paid",
  "notes": "2-night stay with breakfast included"
}
```

### Check-out Reservation

```bash
curl -X POST "http://localhost:8001/api/reservations/42/check-out" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount_paid": 500000,
    "payment_type": "cash",
    "notes": "Final payment: balance settled with deposit"
  }'
```

**Response** (200 OK):
```json
{
  "id": 42,
  "confirmation_number": "a1b2c3d4e5",
  "guest_name": "John Doe",
  "room_number": "105",
  "status": "checked_out",
  "check_in_date": "2025-11-15",
  "check_out_date": "2025-11-17",
  "total_amount": 1000000,
  "total_paid": 1000000,
  "deposit_held": 500000,
  "balance_owed": 0,
  "to_refund": 0,
  "settlement_note": "Full payment received. No deposit refund.",
  "checked_out_at": "2025-11-17T11:00:00Z",
  "deposit_returned_at": "2025-11-17T11:00:00Z"
}
```

### Cancel Reservation

```bash
curl -X DELETE "http://localhost:8001/api/reservations/42" \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "message": "Reservation cancelled successfully",
  "reservation_id": 42,
  "status": "cancelled",
  "cancelled_at": "2025-11-08T16:00:00Z"
}
```

**Error** - Cannot cancel after check-in (409):
```json
{
  "detail": "Cannot cancel reservation in status 'checked_in'",
  "error_code": "INVALID_STATE_TRANSITION"
}
```

---

## Payment Management

### Record Payment

```bash
curl -X POST "http://localhost:8001/api/payments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reservation_id": 42,
    "amount": 300000,
    "payment_type": "card",
    "notes": "Additional payment towards balance"
  }'
```

**Response** (201 Created):
```json
{
  "id": 51,
  "reservation_id": 42,
  "amount": 300000,
  "payment_type": "card",
  "payment_date": "2025-11-10T10:30:00Z",
  "notes": "Additional payment towards balance"
}
```

### List Payments for Reservation

```bash
curl -X GET "http://localhost:8001/api/payments?reservation_id=42" \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 50,
      "reservation_id": 42,
      "amount": 500000,
      "payment_type": "card",
      "payment_date": "2025-11-08T15:05:00Z",
      "notes": "Initial deposit"
    },
    {
      "id": 51,
      "reservation_id": 42,
      "amount": 300000,
      "payment_type": "card",
      "payment_date": "2025-11-10T10:30:00Z",
      "notes": "Additional payment towards balance"
    }
  ],
  "total": 2,
  "total_amount": 800000
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid request format",
  "error_code": "BAD_REQUEST"
}
```

### 401 Unauthorized

```json
{
  "detail": "Invalid or expired token",
  "error_code": "UNAUTHORIZED"
}
```

### 404 Not Found

```json
{
  "detail": "Reservation not found",
  "error_code": "NOT_FOUND",
  "resource": "reservation",
  "id": 999
}
```

### 409 Conflict

```json
{
  "detail": "Room type mismatch. Reservation requires room type 'Deluxe Double' but room 201 is 'Standard Single'",
  "error_code": "VALIDATION_ERROR"
}
```

### 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "loc": ["body", "total_amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "request_id": "req_12345"
}
```

---

## Batch Operations

### Create Multiple Payments

```bash
# Script to record multiple payments
curl -X POST "http://localhost:8001/api/payments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reservation_id": 42,
    "amount": 200000,
    "payment_type": "cash"
  }'

curl -X POST "http://localhost:8001/api/payments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reservation_id": 42,
    "amount": 100000,
    "payment_type": "card"
  }'
```

### Export Reservations for Date Range

```bash
# Query reservations checked out in November
curl -X GET "http://localhost:8001/api/reservations?status=checked_out&page=1&page_size=100" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.items[] | {confirmation_number, guest_name, check_out_date, total_amount}'
```

---

**Last Updated**: November 8, 2025
**Status**: Complete with all endpoints documented
