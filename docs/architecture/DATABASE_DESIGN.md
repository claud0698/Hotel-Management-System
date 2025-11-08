# Database Design - Hotel Management System
## Full Schema with v1.1+ Future Features

**Version**: 1.0 (MVP - Core tables)
**Last Updated**: November 8, 2025
**Status**: Ready for Implementation

---

## Table of Contents

1. [Overview](#overview)
2. [v1.0 Core Tables (10 tables)](#v10-core-tables)
3. [v1.1+ Future Tables (Prepared but unused)](#v11-future-tables-prepared-but-unused)
4. [Discounts & Promotions](#discounts--promotions)
5. [Booking Channel Integration](#booking-channel-integration)
6. [File Management for Payment Proofs](#file-management-for-payment-proofs)
7. [Admin Settings](#admin-settings)
8. [Full Schema with Relationships](#full-schema-with-relationships)
9. [Migration Strategy](#migration-strategy)

---

## Overview

### Philosophy
- **v1.0**: Implement and use core tables only (8 tables)
- **v1.1+**: Prepare future tables in schema, but don't implement business logic yet
- **Scalable**: Add features incrementally without major schema redesign
- **Future-Proof**: Design supports discounts, booking channels, housekeeping, maintenance, file uploads

### Table Categories

**V1.0 (Implement & Use)**:
- `users` - Authentication
- `room_types` - Room categories
- `rooms` - Individual rooms
- `room_images` - Room photo gallery (NEW)
- `room_type_images` - Room type showcases (NEW)
- `guests` - Guest profiles
- `reservations` - Bookings
- `payments` - Payment tracking
- `payment_attachments` - Payment proof uploads (invoices, receipts, transfer proofs)
- `settings` - Admin configuration (v1.0 for booking channels)

**V1.1+ (Prepare but don't use)**:
- `discounts` - Promotional pricing
- `booking_channels` - OTA integrations
- `housekeeping_tasks` - Cleaning workflow
- `maintenance_requests` - Maintenance tracking
- `room_history` - Audit trail
- `guest_documents` - ID scans, additional docs (future)

---

## V1.0 Core Tables

### 1. users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(10) NOT NULL CHECK(role IN ('admin', 'user')),
    status VARCHAR(10) DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

---

### 2. room_types
```sql
CREATE TABLE room_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    description TEXT,
    base_capacity_adults INTEGER DEFAULT 2,
    base_capacity_children INTEGER DEFAULT 1,
    bed_config VARCHAR(100),
    default_rate DECIMAL(12,2) NOT NULL,
    amenities TEXT,
    max_occupancy INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_room_types_code ON room_types(code);
CREATE INDEX idx_room_types_active ON room_types(is_active);
```

---

### 3. rooms
```sql
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    room_number VARCHAR(10) UNIQUE NOT NULL,
    floor INTEGER,
    room_type_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'available'
        CHECK(status IN ('available', 'occupied', 'out_of_order')),
    view_type VARCHAR(50),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_type_id) REFERENCES room_types(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_rooms_number ON rooms(room_number);
CREATE INDEX idx_rooms_status ON rooms(status);
CREATE INDEX idx_rooms_type ON rooms(room_type_id);
CREATE INDEX idx_rooms_active ON rooms(is_active);
```

---

### 3b. room_images (NEW - V1.0 for room photos)
```sql
CREATE TABLE room_images (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    image_name VARCHAR(255) NOT NULL,
    image_type VARCHAR(20) NOT NULL
        CHECK(image_type IN ('main_photo', 'bedroom', 'bathroom',
                             'living_area', 'amenities', 'other')),
    image_path VARCHAR(500) NOT NULL,
    storage_location VARCHAR(50) NOT NULL
        CHECK(storage_location IN ('local', 's3', 'gcs', 'azure')),
    file_size_bytes INTEGER,
    mime_type VARCHAR(100),
    original_filename VARCHAR(255),
    image_width INTEGER,
    image_height INTEGER,

    -- Metadata
    uploaded_by INTEGER,
    description TEXT,
    display_order INTEGER DEFAULT 0,  -- For ordering photos
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_room_images_room ON room_images(room_id);
CREATE INDEX idx_room_images_type ON room_images(image_type);
CREATE INDEX idx_room_images_order ON room_images(room_id, display_order);
CREATE INDEX idx_room_images_active ON room_images(is_active);
```

**Features**:
- Store multiple images per room (main photo + detailed shots)
- Categorized by type (bedroom, bathroom, living area, etc.)
- Display order for gallery
- Full audit trail (who uploaded)
- Support multiple storage backends

**Usage Example**:
```
Room 101 (Standard Double)
├── Image 1: main_photo.jpg (Display order: 1)
├── Image 2: bedroom_view.jpg (Display order: 2)
├── Image 3: bathroom.jpg (Display order: 3)
├── Image 4: living_area.jpg (Display order: 4)
└── Image 5: amenities.jpg (Display order: 5)
```

---

### 3c. room_type_images (NEW - V1.0 for room type showcases)
```sql
CREATE TABLE room_type_images (
    id SERIAL PRIMARY KEY,
    room_type_id INTEGER NOT NULL,
    image_name VARCHAR(255) NOT NULL,
    image_type VARCHAR(20) NOT NULL
        CHECK(image_type IN ('showcase', 'floorplan', 'amenities', 'other')),
    image_path VARCHAR(500) NOT NULL,
    storage_location VARCHAR(50) NOT NULL
        CHECK(storage_location IN ('local', 's3', 'gcs', 'azure')),
    file_size_bytes INTEGER,
    mime_type VARCHAR(100),
    original_filename VARCHAR(255),
    image_width INTEGER,
    image_height INTEGER,

    -- Metadata
    uploaded_by INTEGER,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_type_id) REFERENCES room_types(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_room_type_images_type ON room_type_images(room_type_id);
CREATE INDEX idx_room_type_images_order ON room_type_images(room_type_id, display_order);
CREATE INDEX idx_room_type_images_active ON room_type_images(is_active);
```

**Features**:
- Gallery for room type (showcase to guests)
- Floor plan display
- Amenities showcase
- Used in reservations and bookings

---

### 4. guests
```sql
CREATE TABLE guests (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    phone_country_code VARCHAR(5),
    id_type VARCHAR(50),
    id_number VARCHAR(50),
    nationality VARCHAR(50),
    birth_date DATE,
    notes TEXT,
    is_vip BOOLEAN DEFAULT FALSE,
    preferred_room_type_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (preferred_room_type_id) REFERENCES room_types(id)
        ON DELETE SET NULL
);

CREATE INDEX idx_guests_name ON guests(full_name);
CREATE INDEX idx_guests_email ON guests(email);
CREATE INDEX idx_guests_phone ON guests(phone);
```

---

### 5. reservations
```sql
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    confirmation_number VARCHAR(20) UNIQUE NOT NULL,
    guest_id INTEGER NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    room_type_id INTEGER NOT NULL,
    room_id INTEGER,
    adults INTEGER DEFAULT 1,
    children INTEGER DEFAULT 0,
    rate_per_night DECIMAL(12,2) NOT NULL,
    number_of_nights INTEGER GENERATED ALWAYS AS (check_out_date - check_in_date) STORED,
    subtotal DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    discount_id INTEGER,
    total_amount DECIMAL(12,2) NOT NULL,
    special_requests TEXT,
    status VARCHAR(20) DEFAULT 'confirmed'
        CHECK(status IN ('confirmed', 'checked_in', 'checked_out', 'cancelled')),
    booking_source VARCHAR(50),
    booking_channel_id INTEGER,
    created_by INTEGER NOT NULL,
    checked_in_at TIMESTAMP,
    checked_out_at TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE RESTRICT,
    FOREIGN KEY (room_type_id) REFERENCES room_types(id) ON DELETE RESTRICT,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (discount_id) REFERENCES discounts(id) ON DELETE SET NULL,
    FOREIGN KEY (booking_channel_id) REFERENCES booking_channels(id) ON DELETE SET NULL
);

CREATE INDEX idx_reservations_dates ON reservations(check_in_date, check_out_date);
CREATE INDEX idx_reservations_status ON reservations(status);
CREATE INDEX idx_reservations_guest ON reservations(guest_id);
CREATE INDEX idx_reservations_room ON reservations(room_id);
CREATE INDEX idx_reservations_confirmation ON reservations(confirmation_number);
CREATE INDEX idx_reservations_guest_dates ON reservations(guest_id, check_in_date, check_out_date);
```

---

### 6. payments
```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    reservation_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL
        CHECK(payment_method IN ('cash', 'credit_card', 'debit_card',
              'bank_transfer', 'e_wallet', 'other')),
    reference_number VARCHAR(100),
    transaction_id VARCHAR(100),
    notes TEXT,
    created_by INTEGER,
    is_refund BOOLEAN DEFAULT FALSE,
    refund_reason TEXT,
    is_voided BOOLEAN DEFAULT FALSE,
    has_proof BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_payments_reservation ON payments(reservation_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
CREATE INDEX idx_payments_method ON payments(payment_method);
CREATE INDEX idx_payments_transaction ON payments(transaction_id);
CREATE INDEX idx_payments_has_proof ON payments(has_proof);
```

**New Field for v1.0**:
- `has_proof` - Indicates if payment has attached proof files

---

### 7. payment_attachments ⭐ (NEW - V1.0 for file uploads)
```sql
CREATE TABLE payment_attachments (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL
        CHECK(file_type IN ('invoice', 'receipt', 'transfer_proof',
                            'credit_card_slip', 'other')),
    file_path VARCHAR(500) NOT NULL,
    storage_location VARCHAR(50) NOT NULL
        CHECK(storage_location IN ('local', 's3', 'gcs', 'azure')),
    file_size_bytes INTEGER,
    mime_type VARCHAR(100),
    original_filename VARCHAR(255),

    -- Metadata
    uploaded_by INTEGER,
    description TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by INTEGER,
    verified_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_payment_attachments_payment ON payment_attachments(payment_id);
CREATE INDEX idx_payment_attachments_type ON payment_attachments(file_type);
CREATE INDEX idx_payment_attachments_created ON payment_attachments(created_at);
CREATE INDEX idx_payment_attachments_verified ON payment_attachments(is_verified);
```

**Features**:
- Track multiple proof files per payment
- Support multiple storage backends (local/S3/GCS/Azure)
- Verification workflow (optional admin approval)
- Full audit trail (who uploaded, when verified by whom)

**Usage Example**:
```
Payment: $1,000 for Reservation ABC123
├── Attachment 1: bank_transfer_proof.jpg (Bank Transfer Screenshot)
├── Attachment 2: transaction_receipt.pdf (Bank Receipt)
└── Attachment 3: payment_slip.jpg (ATM/Mobile Banking Slip)
```

---

### 8. settings
```sql
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(20) DEFAULT 'string'
        CHECK(setting_type IN ('string', 'integer', 'boolean', 'json', 'decimal')),
    is_editable BOOLEAN DEFAULT TRUE,
    description TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_settings_key ON settings(setting_key);
CREATE INDEX idx_settings_category ON settings(category);
```

**File Storage Settings (for V1.0 use)**:
```json
{
  "file_storage_config": {
    "storage_backend": "local",  // local, s3, gcs, azure
    "local_path": "/data/uploads/payment_proofs",
    "max_file_size_mb": 10,
    "allowed_file_types": ["jpg", "jpeg", "png", "pdf"],
    "retention_days": 2555  // ~7 years for audit
  },
  "s3_config": {
    "enabled": false,
    "bucket": "hotel-payment-proofs",
    "region": "us-east-1",
    "access_key": "xxxxx",
    "secret_key": "xxxxx"
  }
}
```

---

## V1.1+ Future Tables (Prepared but unused)

### 9. discounts (V1.1+)
```sql
CREATE TABLE discounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE,
    description TEXT,
    discount_type VARCHAR(20) NOT NULL
        CHECK(discount_type IN ('percentage', 'fixed_amount')),
    discount_value DECIMAL(12,2) NOT NULL,
    max_discount_amount DECIMAL(12,2),

    -- Applicability
    applicable_room_types TEXT,  -- JSON array of room_type_ids
    applicable_guests TEXT,       -- JSON array of guest_ids (VIP only)

    -- Validity
    valid_from DATE,
    valid_until DATE,
    usage_limit INTEGER,
    usage_count INTEGER DEFAULT 0,

    -- Conditions
    min_stay_nights INTEGER,
    min_booking_amount DECIMAL(12,2),
    max_bookings_per_guest INTEGER,

    status VARCHAR(20) DEFAULT 'active'
        CHECK(status IN ('active', 'inactive', 'expired')),
    is_auto_applied BOOLEAN DEFAULT FALSE,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_discounts_code ON discounts(code);
CREATE INDEX idx_discounts_status ON discounts(status);
CREATE INDEX idx_discounts_dates ON discounts(valid_from, valid_until);
```

---

### 10. booking_channels (V1.1+)
```sql
CREATE TABLE booking_channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    channel_type VARCHAR(50) NOT NULL
        CHECK(channel_type IN ('ota', 'direct', 'corporate', 'api')),

    -- API Configuration
    api_url VARCHAR(255),
    api_key VARCHAR(255),
    api_secret VARCHAR(255),
    webhook_url VARCHAR(255),

    -- Settings
    is_enabled BOOLEAN DEFAULT TRUE,
    auto_confirm BOOLEAN DEFAULT FALSE,
    sync_enabled BOOLEAN DEFAULT FALSE,
    sync_interval_minutes INTEGER DEFAULT 60,

    -- Commission
    commission_percentage DECIMAL(5,2) DEFAULT 0,
    commission_fixed_amount DECIMAL(12,2) DEFAULT 0,

    -- Support
    support_contact VARCHAR(255),
    support_email VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_booking_channels_code ON booking_channels(code);
CREATE INDEX idx_booking_channels_enabled ON booking_channels(is_enabled);
```

**Predefined Channels**:
- `direct` - Walk-in, phone, email
- `tiket` - Tiket.com
- `traveloka` - Traveloka
- `booking` - Booking.com

---

### 11. housekeeping_tasks (V1.1+)
```sql
CREATE TABLE housekeeping_tasks (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    reservation_id INTEGER,
    task_type VARCHAR(50) NOT NULL
        CHECK(task_type IN ('turnover', 'deep_clean', 'maintenance_prep', 'post_checkout')),
    status VARCHAR(20) DEFAULT 'pending'
        CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled')),

    priority VARCHAR(20) DEFAULT 'normal'
        CHECK(priority IN ('urgent', 'high', 'normal', 'low')),

    assigned_to INTEGER,
    assigned_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    notes TEXT,
    checklist TEXT,  -- JSON array of checklist items

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_housekeeping_room ON housekeeping_tasks(room_id);
CREATE INDEX idx_housekeeping_status ON housekeeping_tasks(status);
CREATE INDEX idx_housekeeping_assigned ON housekeeping_tasks(assigned_to);
```

---

### 12. maintenance_requests (V1.1+)
```sql
CREATE TABLE maintenance_requests (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    issue_category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal'
        CHECK(priority IN ('urgent', 'high', 'normal', 'low')),

    status VARCHAR(20) DEFAULT 'open'
        CHECK(status IN ('open', 'assigned', 'in_progress', 'completed', 'cancelled')),

    reported_by INTEGER,
    assigned_to INTEGER,

    reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_date TIMESTAMP,
    completed_date TIMESTAMP,

    notes TEXT,
    estimated_cost DECIMAL(12,2),
    actual_cost DECIMAL(12,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE RESTRICT,
    FOREIGN KEY (reported_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_maintenance_room ON maintenance_requests(room_id);
CREATE INDEX idx_maintenance_status ON maintenance_requests(status);
CREATE INDEX idx_maintenance_priority ON maintenance_requests(priority);
```

---

### 13. room_history (V1.1+)
```sql
CREATE TABLE room_history (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL
        CHECK(event_type IN ('check_in', 'check_out', 'status_change',
                             'cleaning', 'maintenance')),

    reservation_id INTEGER,
    previous_status VARCHAR(20),
    new_status VARCHAR(20),

    notes TEXT,
    changed_by INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE SET NULL,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_room_history_room ON room_history(room_id);
CREATE INDEX idx_room_history_type ON room_history(event_type);
CREATE INDEX idx_room_history_date ON room_history(created_at);
```

---

### 14. guest_documents (V1.1+)
```sql
CREATE TABLE guest_documents (
    id SERIAL PRIMARY KEY,
    guest_id INTEGER NOT NULL,
    document_type VARCHAR(50) NOT NULL
        CHECK(document_type IN ('id_scan', 'passport_scan', 'visa_scan', 'other')),
    file_path VARCHAR(500) NOT NULL,
    storage_location VARCHAR(50) NOT NULL,
    uploaded_by INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_guest_documents_guest ON guest_documents(guest_id);
CREATE INDEX idx_guest_documents_type ON guest_documents(document_type);
```

---

## File Management for Payment Proofs

### Storage Architecture

**Purpose**: Store payment evidence (invoices, receipts, transfer proofs)

**Supported Storage Backends**:
1. **Local** (v1.0) - `/data/uploads/payment_proofs/{reservation_id}/{payment_id}/`
2. **AWS S3** (v1.1+) - `s3://bucket/payment-proofs/{reservation_id}/{payment_id}/`
3. **Google Cloud Storage** (v1.1+) - `gs://bucket/payment-proofs/{reservation_id}/{payment_id}/`
4. **Azure Blob** (v1.1+) - `https://account.blob.core.windows.net/container/...`

### File Organization

```
Local Storage Path Structure:
/data/uploads/
├── payment_proofs/
│   ├── RES-20251108-0001/
│   │   ├── PAY-001/
│   │   │   ├── bank_transfer_proof.jpg (1.2 MB)
│   │   │   ├── transaction_receipt.pdf (2.3 MB)
│   │   │   └── metadata.json
│   │   └── PAY-002/
│   │       └── credit_card_slip.png (890 KB)
│   └── RES-20251108-0002/
│       └── ...

Metadata Format:
{
  "payment_id": 123,
  "file_name": "bank_transfer_proof.jpg",
  "file_size": 1254321,
  "mime_type": "image/jpeg",
  "uploaded_by": 1,
  "uploaded_at": "2025-11-08T10:30:00Z",
  "is_verified": false
}
```

### File Upload API (V1.0)

```
POST /api/v1/payments/{id}/attachments
Headers:
  - Authorization: Bearer <token>
  - Content-Type: multipart/form-data

Parameters:
  - file: <binary file>
  - file_type: "invoice" | "receipt" | "transfer_proof" | "credit_card_slip" | "other"
  - description: "Optional description"

Response:
{
  "id": 456,
  "payment_id": 123,
  "file_name": "bank_transfer_proof.jpg",
  "file_path": "/data/uploads/payment_proofs/RES-001/PAY-001/...",
  "storage_location": "local",
  "file_size_bytes": 1254321,
  "mime_type": "image/jpeg",
  "uploaded_by": 1,
  "is_verified": false,
  "created_at": "2025-11-08T10:30:00Z"
}
```

### Retrieval API (V1.0)

```
GET /api/v1/payments/{id}/attachments
Response:
{
  "payment_id": 123,
  "attachments": [
    {
      "id": 456,
      "file_name": "bank_transfer_proof.jpg",
      "file_type": "transfer_proof",
      "file_size_bytes": 1254321,
      "uploaded_by": "John Doe",
      "uploaded_at": "2025-11-08T10:30:00Z",
      "is_verified": false,
      "download_url": "/api/v1/attachments/456/download"
    }
  ]
}
```

### Admin Features (V1.0)

**Payment Proof Management**:
- Upload/download proofs
- View all attachments per payment
- Verify proofs (mark as verified)
- Delete files (with audit trail)

---

## Discounts & Promotions (V1.1+)

### Database Design Ready
- Table created but no business logic
- Admin UI prepared for future

---

## Booking Channel Integration (V1.0)

### Admin Configuration
Admin can configure channels in Settings:
```json
{
  "enabled_channels": ["direct", "tiket", "traveloka", "booking"],
  "channels": {
    "tiket": {
      "enabled": true,
      "api_key": "xxxxx",
      "commission_percentage": 15
    },
    "traveloka": {
      "enabled": true,
      "api_key": "xxxxx",
      "commission_percentage": 18
    },
    "booking": {
      "enabled": true,
      "api_key": "xxxxx",
      "commission_percentage": 20
    }
  }
}
```

---

## Admin Settings Configuration (V1.0)

### Default Settings to Create

```python
DEFAULT_SETTINGS = [
    # Hotel Info
    ('hotel_name', 'My Hotel', 'string', 'Hotel information'),
    ('hotel_address', 'Address', 'string', 'Hotel information'),
    ('hotel_phone', '+62xxx', 'string', 'Hotel information'),

    # Booking Config
    ('check_in_time', '14:00', 'string', 'Booking'),
    ('check_out_time', '12:00', 'string', 'Booking'),

    # File Storage
    ('file_storage_config', '{"storage_backend": "local", ...}', 'json', 'File Storage'),

    # Localization
    ('timezone', 'Asia/Jakarta', 'string', 'Localization'),
    ('currency', 'IDR', 'string', 'Localization'),
    ('default_language', 'id', 'string', 'Localization'),

    # OTA Channels
    ('booking_channels_config', '{"enabled_channels": [...]}', 'json', 'OTA'),
]
```

---

## Full Schema with Relationships

### Entity Relationship Diagram

```
users (id) ──┐
             ├──< (N) reservations (created_by)
             ├──< (N) payments (created_by)
             ├──< (N) payment_attachments (uploaded_by, verified_by)
             └──< (N) maintenance_requests (reported_by, assigned_to)

room_types (id) ──┐
                  ├──< (N) rooms
                  ├──< (N) reservations
                  └──< (N) guests (preferred_room_type)

rooms (id) ──┐
             ├──< (N) reservations
             ├──< (N) housekeeping_tasks
             ├──< (N) maintenance_requests
             └──< (N) room_history

guests (id) ──┐
              ├──< (N) reservations
              └──< (N) guest_documents

reservations (id) ──┐
                    ├──< (N) payments
                    ├──< (N) payment_attachments (via payments)
                    ├──< (N) housekeeping_tasks
                    └──< room_history (one-to-many)

payments (id) ──< (N) payment_attachments

discounts (id) ──< (N) reservations

booking_channels (id) ──< (N) reservations
```

---

## Migration Strategy

### Phase 1: V1.0 Implementation
```sql
-- Create all v1.0 core tables
CREATE TABLE users (...);
CREATE TABLE room_types (...);
CREATE TABLE rooms (...);
CREATE TABLE room_images (...);  -- NEW for room photos
CREATE TABLE room_type_images (...);  -- NEW for room type showcases
CREATE TABLE guests (...);
CREATE TABLE reservations (...);
CREATE TABLE payments (...);
CREATE TABLE payment_attachments (...);  -- NEW for payment proofs
CREATE TABLE settings (...);
CREATE TABLE discounts (...);  -- Created but not used
CREATE TABLE booking_channels (...);  -- Created but not used
```

**Status**: ✅ Implement and use first 10 tables, create last 2 but don't use

---

### Phase 2: V1.1 Enhancement
```sql
-- Create and use v1.1 tables
CREATE TABLE housekeeping_tasks (...);
CREATE TABLE maintenance_requests (...);
CREATE TABLE room_history (...);
CREATE TABLE guest_documents (...);

-- Activate discount logic
-- Activate booking channel sync
```

---

## Constraints & Validations

### V1.0 Rules

**Payments with Attachments**:
- Up to 5 files per payment
- Max 10MB per file
- Allowed types: JPG, PNG, PDF
- Retention: 7 years (audit requirement)

**Payment Amounts**:
- `amount > 0`
- Sum of payments ≤ reservation total_amount
- File required for transfers (optional for cash)

---

## Summary Table

| Component | V1.0 | V1.1+ | Status |
|-----------|------|-------|--------|
| Room Images | ✅ | - | Multi-photo gallery with order |
| Room Type Images | ✅ | - | Showcase/floorplan support |
| Payment Proofs | ✅ | - | Multi-file upload with verification |
| Discounts | - | ✅ | Schema only |
| Booking Channels | Config | Sync | Config in v1.0 |
| Housekeeping | - | ✅ | Schema only |
| Maintenance | - | ✅ | Schema only |
| Room History | - | ✅ | Schema only |
| Guest Documents | - | ✅ | Schema only |

---

**Status**: ✅ **Database Design Complete and Ready for Implementation**

This design allows you to:
1. ✅ Store payment proofs with full audit trail
2. ✅ Support multiple file types and storage backends
3. ✅ Configure booking channels without implementation
4. ✅ Prepare discounts table for future use
5. ✅ Scale without schema redesign
