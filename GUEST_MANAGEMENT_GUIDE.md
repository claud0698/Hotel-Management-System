# Guest Management System - Complete Guide

**Status:** ✅ Database Ready | **Endpoints:** ⏳ Phase 1 Implementation

---

## 📋 Guest Database Schema

### Guest Table Structure

The `guests` table stores all guest information with the following fields:

```python
class Guest(Base):
    __tablename__ = "guests"

    # Identifiers
    id                      Integer, Primary Key
    full_name              String(100), NOT NULL, Indexed
    email                  String(100), Indexed
    phone                  String(20), Indexed
    phone_country_code     String(5)

    # Identification
    id_type                String(50)          # passport, driver_license, national_id, etc.
    id_number              String(50)

    # Personal Info
    nationality            String(50)
    birth_date             Date

    # Hotel Specific
    is_vip                 Boolean, Default=False
    preferred_room_type_id Integer, Foreign Key → room_types.id
    notes                  Text

    # Audit Trail
    created_at             DateTime, Default=utcnow()
    updated_at             DateTime, Default=utcnow()
```

### Database Relationships

```
Guest ─────→ RoomType (preferred_room_type)
  │
  └─────→ Reservation (multiple reservations per guest)
            │
            └─────→ Room
            └─────→ Payment
```

---

## 🔑 Key Features

### 1. **Comprehensive Guest Profile**
- Full contact information (name, email, phone with country code)
- Identification tracking (ID type and number for check-in requirements)
- Personal details (nationality, birth date for demographic analysis)
- VIP flag for special handling

### 2. **Preferences Tracking**
- Preferred room type stored for personalized recommendations
- Notes field for special requests and preferences
- History accessible through reservations relationship

### 3. **Audit Trail**
- Created timestamp for guest acquisition tracking
- Updated timestamp for profile modification tracking
- Essential for compliance and guest history

### 4. **Data Integrity**
- Email and phone indexed for quick lookups
- Full_name indexed for guest searches
- Foreign key relationship to room_types
- Not null constraint on full_name (required field)

---

## 📊 Guest Data Model (to_dict Output)

When a guest is serialized to JSON:

```json
{
    "id": 1,
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "phone_country_code": "+1",
    "id_type": "passport",
    "id_number": "A12345678",
    "nationality": "USA",
    "birth_date": "1990-05-15",
    "notes": "Prefers high floor, non-smoking room",
    "is_vip": true,
    "preferred_room_type_id": 2,
    "created_at": "2025-11-08T10:30:00",
    "updated_at": "2025-11-08T10:30:00"
}
```

---

## 🔄 Guest Lifecycle

### 1. **Guest Creation**
```
User creates guest profile
→ Validate required fields (full_name)
→ Check for duplicate email (optional)
→ Store in guests table
→ Generate guest ID
```

**Required Fields:**
- `full_name` ✅ (mandatory)

**Optional Fields:**
- email, phone, nationality, birth_date
- ID info, VIP status, preferences, notes

### 2. **Guest Update**
```
User modifies guest information
→ Update any profile field
→ Update modified timestamp
→ Maintain audit trail
```

### 3. **Guest Association with Reservation**
```
Guest → Reservation → Room
        Reservation → Payment
```

When creating a reservation:
1. Specify guest_id
2. System associates guest with room, dates, rates
3. Payment linked to reservation (and guest indirectly)
4. Guest history tracked through reservations

### 4. **Guest History Retrieval**
```
GET /api/guests/{id}/reservations
→ All reservations for guest
→ Check-in/check-out history
→ Payment records
→ Room preferences used
```

---

## 🛠️ Phase 1 - Guest Management Endpoints (To Be Implemented)

### Guest CRUD Operations

#### Create Guest
```
POST /api/guests
Content-Type: application/json

{
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "phone_country_code": "+1",
    "id_type": "passport",
    "id_number": "A12345678",
    "nationality": "USA",
    "birth_date": "1990-05-15",
    "is_vip": false,
    "preferred_room_type_id": 2,
    "notes": "Regular guest, prefers king beds"
}

Response: 201 Created
{
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    ...
}
```

#### Get Guest
```
GET /api/guests/{id}

Response: 200 OK
{
    "id": 1,
    "full_name": "John Doe",
    ...
}
```

#### List Guests
```
GET /api/guests?skip=0&limit=10&is_vip=false&search=john

Query Parameters:
- skip: Pagination offset
- limit: Number of results
- is_vip: Filter by VIP status
- search: Search by name or email

Response: 200 OK
{
    "guests": [...],
    "total": 150,
    "skip": 0,
    "limit": 10
}
```

#### Update Guest
```
PUT /api/guests/{id}

{
    "full_name": "John Doe",
    "is_vip": true,
    "preferred_room_type_id": 3,
    "notes": "VIP guest, prefers suites"
}

Response: 200 OK
{
    "id": 1,
    "full_name": "John Doe",
    "is_vip": true,
    ...
}
```

#### Delete Guest
```
DELETE /api/guests/{id}

Response: 200 OK or 204 No Content
{
    "message": "Guest deleted successfully"
}

Note: Consider soft delete to maintain reservation history
```

---

## 📊 Guest Query Examples

### Find Guest by Email
```sql
SELECT * FROM guests WHERE email = 'john@example.com';
```

### List VIP Guests
```sql
SELECT * FROM guests WHERE is_vip = true ORDER BY created_at DESC;
```

### Guest Reservation Count
```sql
SELECT g.id, g.full_name, COUNT(r.id) as reservation_count
FROM guests g
LEFT JOIN reservations r ON g.id = r.guest_id
GROUP BY g.id
ORDER BY reservation_count DESC;
```

### Recent Guests
```sql
SELECT * FROM guests ORDER BY created_at DESC LIMIT 10;
```

### Guests with Preferences
```sql
SELECT g.*, rt.name as preferred_room
FROM guests g
LEFT JOIN room_types rt ON g.preferred_room_type_id = rt.id
WHERE g.preferred_room_type_id IS NOT NULL;
```

---

## 🔐 Guest Privacy & Security

### Data Protection Considerations
- ✅ Encrypted transmission (HTTPS in production)
- ✅ Sensitive fields: email, phone, ID number
- ⏳ GDPR compliance (right to be forgotten - soft delete recommended)
- ⏳ PII handling - audit access to guest data
- ⏳ Data retention policy - when to purge old guest records

### Access Control
```python
# Only admin can view all guests
@router.get("/api/guests")
async def list_guests(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    # ...

# Users can view their own guest profiles (future: user-guest mapping)
@router.get("/api/guests/{id}")
async def get_guest(
    id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify ownership or admin role
    # ...
```

---

## 📈 Guest Analytics & Reporting

### Metrics to Track
- **Total Guests:** Count of guests in system
- **VIP Guests:** High-value customer tracking
- **Return Guests:** Frequency of repeat bookings
- **Guest Satisfaction:** Average rating/review
- **Booking Patterns:** Preferences by room type

### Reports to Generate
```
1. Guest Summary Report
   - Total guests
   - VIP percentage
   - New guests (this month)
   - Average stay duration

2. Guest Activity Report
   - Recent guests
   - Upcoming check-ins
   - Past guests statistics

3. Guest Preferences Report
   - Popular room types
   - Special requests
   - Dietary requirements (if added)
```

---

## 🔄 Guest-Reservation Flow

### Typical Workflow

```
1. Create Guest Profile
   ↓
2. Create Reservation for Guest
   ├─ Specify guest_id
   ├─ Specify room_type_id
   ├─ Specify check-in/check-out dates
   ├─ System calculates rates
   └─ Generate confirmation number
   ↓
3. Process Payments
   ├─ Link payment to reservation
   ├─ Track payment status
   └─ Generate invoice
   ↓
4. Check-in
   ├─ Verify guest identity (use id_number)
   ├─ Assign specific room
   ├─ Register key
   └─ Activate room access
   ↓
5. Check-out
   ├─ Settle any outstanding charges
   ├─ Collect feedback
   ├─ Process refunds if applicable
   └─ Update guest status
   ↓
6. Post-Stay
   ├─ Request review/feedback
   ├─ Update guest preferences
   ├─ Track for marketing
   └─ Offer loyalty rewards
```

---

## 💾 Database Statistics (Current)

```
guests table:
- Records: 0 (ready for data)
- Columns: 14
- Indexes: 3 (id, full_name, email, phone)
- Relationships: 2 (room_types, reservations)
- Storage: ~100 bytes per record (estimated)
```

---

## 🚀 Implementation Roadmap

### Phase 1 (Week 2-3)
- [ ] Implement POST /api/guests (create guest)
- [ ] Implement GET /api/guests/{id} (get guest)
- [ ] Implement PUT /api/guests/{id} (update guest)
- [ ] Implement GET /api/guests (list guests with filters)
- [ ] Implement DELETE /api/guests/{id} (delete guest)

### Phase 1.5 (Future)
- [ ] Guest search and filtering
- [ ] Guest preferences analysis
- [ ] Loyalty program integration
- [ ] Guest feedback/reviews
- [ ] Automated guest communication

### Phase 2+ (Long-term)
- [ ] Guest app for self-service
- [ ] Guest history analytics
- [ ] Personalized marketing
- [ ] Guest relationship management (CRM)
- [ ] Advanced segmentation

---

## 📝 API Request/Response Examples

### Create Guest Request
```bash
curl -X POST http://localhost:8001/api/guests \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Smith",
    "email": "jane.smith@example.com",
    "phone": "+44-20-7946-0958",
    "phone_country_code": "+44",
    "id_type": "passport",
    "id_number": "GB1234567",
    "nationality": "UK",
    "birth_date": "1985-03-20",
    "is_vip": false,
    "notes": "Frequent traveler, prefers near elevator"
  }'
```

### Get Guest Reservations
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8001/api/guests/1/reservations

# Returns all reservations for guest 1
```

### List VIP Guests
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8001/api/guests?is_vip=true"

# Returns only VIP guests with pagination
```

---

## 🎯 Best Practices

### Data Entry
✅ Always validate full_name (required)
✅ Normalize phone numbers with country code
✅ Store ID information for check-in verification
✅ Track preferences for personalization
✅ Update notes with special requests

### Privacy
✅ Encrypt sensitive data (PII) in transit
✅ Limit guest data access to authorized staff
✅ Implement soft delete for compliance
✅ Regular security audits
✅ GDPR-compliant data handling

### Performance
✅ Index email and phone for quick lookups
✅ Cache frequently accessed guest profiles
✅ Batch guest operations when possible
✅ Archive old guest records
✅ Monitor guest table growth

---

## ✅ Checklist for Phase 1

- [ ] Create Pydantic schemas for guest (GuestCreate, GuestUpdate, GuestResponse)
- [ ] Implement guest router with all CRUD operations
- [ ] Add guest search and filtering
- [ ] Add validation (email format, phone format)
- [ ] Add permission checks (only admin can list all guests)
- [ ] Write unit tests for guest endpoints
- [ ] Document in Swagger UI
- [ ] Test all scenarios (create, update, delete, list)

---

## 📚 Related Documentation

- [Database Design](./docs/architecture/PROJECT_OVERVIEW.md)
- [Models](./backend/models.py)
- [Phase 1 Roadmap](./PHASE_1_ROADMAP.md)
- [Quick Reference](./QUICK_REFERENCE.md)

---

**Guest Management System Status:** ✅ Database Ready | ⏳ Endpoints Coming Phase 1 Week 2-3

**Key Takeaway:** The guest table is fully designed with comprehensive fields for guest profile management, preferences, and audit trail. Phase 1 Week 2-3 will implement the REST API endpoints to manage guest records.
