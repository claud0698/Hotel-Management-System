# Guest API - Quick Reference Card

## Guest Field Requirements at a Glance

### REQUIRED Fields (Must Provide)
```
✅ full_name (String, 2-100 chars) - Guest's legal name
```

### OPTIONAL Fields (Nice to Have)

#### Contact Information
```
📧 email (String, unique email) - Guest's email address
📱 phone (String, max 20 chars) - Phone number
🌐 phone_country_code (String, max 5 chars) - Country code (e.g., "+1", "+44")
```

#### Identification
```
🪪 id_type (String, max 50 chars) - Document type: passport, driver_license, national_id, visa, etc.
🆔 id_number (String, max 50 chars) - Document number
```

#### Personal Information
```
🌍 nationality (String, max 50 chars) - Country of origin
🎂 birth_date (String, YYYY-MM-DD format) - Date of birth
```

#### Hotel-Specific
```
⭐ is_vip (Boolean, default: false) - VIP guest flag
🏨 preferred_room_type_id (Integer) - Preferred room type ID
📝 notes (Text, unlimited) - Special requests, preferences, allergies, etc.
```

#### Auto-Generated (Read-Only)
```
🔑 id (Integer) - Unique guest ID (generated on creation)
⏰ created_at (DateTime) - When profile was created
🔄 updated_at (DateTime) - When profile was last updated
```

---

## 6 Core Endpoints

### 1️⃣ CREATE
```bash
POST /api/guests
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "John Doe"              # REQUIRED
  "email": "john@example.com",         # optional, unique
  "phone": "+1-555-0123",              # optional
  "phone_country_code": "+1",          # optional
  "id_type": "passport",               # optional
  "id_number": "ABC123",               # optional
  "nationality": "USA",                # optional
  "birth_date": "1990-05-15",          # optional, YYYY-MM-DD
  "is_vip": false,                     # optional, default: false
  "preferred_room_type_id": 2,         # optional
  "notes": "High floor preferred"      # optional
}

Response: 201 Created with full guest object
```

### 2️⃣ READ (Get One)
```bash
GET /api/guests/{id}
Authorization: Bearer {token}

Response: 200 OK with guest object
```

### 3️⃣ READ (List All)
```bash
GET /api/guests?skip=0&limit=10&is_vip=false&search=john
Authorization: Bearer {token}

Query Parameters:
- skip: (int) How many to skip (pagination)
- limit: (int) How many to return (max: 100)
- is_vip: (bool) Filter by VIP status
- search: (string) Search name/email

Response: 200 OK with guest array + metadata
{
  "guests": [...],
  "total": 150,
  "skip": 0,
  "limit": 10
}
```

### 4️⃣ UPDATE
```bash
PUT /api/guests/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "is_vip": true,          # only update what you need
  "notes": "VIP status"
}

Response: 200 OK with updated guest object
```

### 5️⃣ DELETE
```bash
DELETE /api/guests/{id}
Authorization: Bearer {token}

Response: 200 OK with success message
Error: 400 if guest has reservations
```

### 6️⃣ BONUS - Get Reservations
```bash
GET /api/guests/{id}/reservations?skip=0&limit=10
Authorization: Bearer {token}

Response: 200 OK with reservation array
{
  "guest_id": 1,
  "guest_name": "John Doe",
  "reservations": [...],
  "total": 5,
  "skip": 0,
  "limit": 10
}
```

---

## Response Format

All guest responses follow this structure:

```json
{
  "id": 1,                           // Auto-generated
  "full_name": "John Doe",           // REQUIRED
  "email": "john@example.com",       // Optional (unique)
  "phone": "+1-555-0123",            // Optional
  "phone_country_code": "+1",        // Optional
  "id_type": "passport",             // Optional
  "id_number": "ABC123",             // Optional
  "nationality": "USA",              // Optional
  "birth_date": "1990-05-15",        // Optional (YYYY-MM-DD)
  "is_vip": false,                   // Optional (default: false)
  "preferred_room_type_id": 2,       // Optional (room type ID)
  "notes": "Special requests...",    // Optional (unlimited text)
  "created_at": "2025-11-08T...",    // Auto-generated (ISO datetime)
  "updated_at": "2025-11-08T..."     // Auto-updated (ISO datetime)
}
```

---

## Quick Examples

### Minimal Guest (Full Name Only)
```json
{
  "full_name": "Jane Smith"
}
```

### Guest with Contact Info
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0123",
  "phone_country_code": "+1"
}
```

### Complete Guest Profile
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-0123",
  "phone_country_code": "+1",
  "id_type": "passport",
  "id_number": "A12345678",
  "nationality": "USA",
  "birth_date": "1990-05-15",
  "is_vip": false,
  "preferred_room_type_id": 2,
  "notes": "Prefers high floor, non-smoking, allergic to nuts"
}
```

### VIP Guest Update
```json
{
  "is_vip": true,
  "preferred_room_type_id": 3,
  "notes": "Premium member - provide suite upgrade"
}
```

---

## Error Codes & Messages

| Code | Scenario | Message |
|------|----------|---------|
| 201 | Success | Guest created |
| 200 | Success | Guest retrieved/updated/deleted |
| 400 | Bad Request | Duplicate email, validation error |
| 404 | Not Found | Guest not found, room type not found |
| 422 | Validation | Invalid data type or format |

---

## Filtering & Searching

### Filter by VIP Status
```bash
GET /api/guests?is_vip=true      # Only VIP guests
GET /api/guests?is_vip=false     # Only non-VIP guests
```

### Search by Name or Email
```bash
GET /api/guests?search=john      # Finds "John Doe", "Johnny Smith"
GET /api/guests?search=example   # Finds "user@example.com"
```

### Pagination
```bash
GET /api/guests?skip=0&limit=10    # First 10 guests
GET /api/guests?skip=10&limit=10   # Next 10 guests (11-20)
GET /api/guests?skip=20&limit=5    # 5 guests starting at position 21
```

### Combined Filters
```bash
GET /api/guests?is_vip=true&search=john&skip=0&limit=20
# VIP guests named "john", first 20 results
```

---

## Test Commands

```bash
# Login first to get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Create guest
curl -X POST http://localhost:8001/api/guests \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"John Doe"}'

# List guests
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/guests

# Get specific guest
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/guests/1

# Update guest
curl -X PUT http://localhost:8001/api/guests/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_vip":true}'

# Delete guest
curl -X DELETE http://localhost:8001/api/guests/1 \
  -H "Authorization: Bearer $TOKEN"

# Get guest's reservations
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/guests/1/reservations
```

---

## Status: ✅ PRODUCTION READY

- All endpoints implemented
- All endpoints tested
- Full validation in place
- Error handling included
- Documentation complete

**Ready for:** Frontend integration, Reservation system, Payment integration

---

*Last Updated: 2025-11-08*
*Version: 1.0.0*
*Implementation: Complete ✅*
