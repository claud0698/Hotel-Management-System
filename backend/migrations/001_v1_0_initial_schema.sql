-- Hotel Management System v1.0 - Initial Database Schema
-- Supabase PostgreSQL Migration
-- Created: November 8, 2025
-- Status: Ready for Implementation

-- ============================================================================
-- TABLE 1: users (Authentication & User Management)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
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

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- ============================================================================
-- TABLE 2: room_types (Room Categories)
-- ============================================================================
CREATE TABLE IF NOT EXISTS room_types (
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

CREATE INDEX IF NOT EXISTS idx_room_types_code ON room_types(code);
CREATE INDEX IF NOT EXISTS idx_room_types_active ON room_types(is_active);

-- ============================================================================
-- TABLE 3: rooms (Individual Rooms)
-- ============================================================================
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    room_number VARCHAR(10) UNIQUE NOT NULL,
    floor INTEGER,
    room_type_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'available'
        CHECK(status IN ('available', 'occupied', 'out_of_order')),
    view_type VARCHAR(50),
    notes TEXT,
    custom_rate DECIMAL(12,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_type_id) REFERENCES room_types(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rooms_number ON rooms(room_number);
CREATE INDEX IF NOT EXISTS idx_rooms_status ON rooms(status);
CREATE INDEX IF NOT EXISTS idx_rooms_type ON rooms(room_type_id);
CREATE INDEX IF NOT EXISTS idx_rooms_active ON rooms(is_active);

-- ============================================================================
-- TABLE 3b: room_images (Room Photo Gallery)
-- ============================================================================
CREATE TABLE IF NOT EXISTS room_images (
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
    uploaded_by INTEGER,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_room_images_room ON room_images(room_id);
CREATE INDEX IF NOT EXISTS idx_room_images_type ON room_images(image_type);
CREATE INDEX IF NOT EXISTS idx_room_images_order ON room_images(room_id, display_order);
CREATE INDEX IF NOT EXISTS idx_room_images_active ON room_images(is_active);

-- ============================================================================
-- TABLE 3c: room_type_images (Room Type Showcase Gallery)
-- ============================================================================
CREATE TABLE IF NOT EXISTS room_type_images (
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
    uploaded_by INTEGER,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_type_id) REFERENCES room_types(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_room_type_images_type ON room_type_images(room_type_id);
CREATE INDEX IF NOT EXISTS idx_room_type_images_order ON room_type_images(room_type_id, display_order);
CREATE INDEX IF NOT EXISTS idx_room_type_images_active ON room_type_images(is_active);

-- ============================================================================
-- TABLE 4: guests (Guest Profiles)
-- ============================================================================
CREATE TABLE IF NOT EXISTS guests (
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

CREATE INDEX IF NOT EXISTS idx_guests_name ON guests(full_name);
CREATE INDEX IF NOT EXISTS idx_guests_email ON guests(email);
CREATE INDEX IF NOT EXISTS idx_guests_phone ON guests(phone);

-- ============================================================================
-- TABLE 5: reservations (Booking System)
-- ============================================================================
CREATE TABLE IF NOT EXISTS reservations (
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

CREATE INDEX IF NOT EXISTS idx_reservations_dates ON reservations(check_in_date, check_out_date);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);
CREATE INDEX IF NOT EXISTS idx_reservations_guest ON reservations(guest_id);
CREATE INDEX IF NOT EXISTS idx_reservations_room ON reservations(room_id);
CREATE INDEX IF NOT EXISTS idx_reservations_confirmation ON reservations(confirmation_number);
CREATE INDEX IF NOT EXISTS idx_reservations_guest_dates ON reservations(guest_id, check_in_date, check_out_date);

-- ============================================================================
-- TABLE 6: payments (Payment Tracking)
-- ============================================================================
CREATE TABLE IF NOT EXISTS payments (
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

CREATE INDEX IF NOT EXISTS idx_payments_reservation ON payments(reservation_id);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_payments_method ON payments(payment_method);
CREATE INDEX IF NOT EXISTS idx_payments_transaction ON payments(transaction_id);
CREATE INDEX IF NOT EXISTS idx_payments_has_proof ON payments(has_proof);

-- ============================================================================
-- TABLE 7: payment_attachments (Payment Proof Uploads)
-- ============================================================================
CREATE TABLE IF NOT EXISTS payment_attachments (
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

CREATE INDEX IF NOT EXISTS idx_payment_attachments_payment ON payment_attachments(payment_id);
CREATE INDEX IF NOT EXISTS idx_payment_attachments_type ON payment_attachments(file_type);
CREATE INDEX IF NOT EXISTS idx_payment_attachments_created ON payment_attachments(created_at);
CREATE INDEX IF NOT EXISTS idx_payment_attachments_verified ON payment_attachments(is_verified);

-- ============================================================================
-- TABLE 8: settings (Admin Configuration)
-- ============================================================================
CREATE TABLE IF NOT EXISTS settings (
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

CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(setting_key);
CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category);

-- ============================================================================
-- TABLE 9: discounts (V1.1+ - Created but not used in v1.0)
-- ============================================================================
CREATE TABLE IF NOT EXISTS discounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE,
    description TEXT,
    discount_type VARCHAR(20) NOT NULL
        CHECK(discount_type IN ('percentage', 'fixed_amount')),
    discount_value DECIMAL(12,2) NOT NULL,
    max_discount_amount DECIMAL(12,2),
    applicable_room_types TEXT,
    applicable_guests TEXT,
    valid_from DATE,
    valid_until DATE,
    usage_limit INTEGER,
    usage_count INTEGER DEFAULT 0,
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

CREATE INDEX IF NOT EXISTS idx_discounts_code ON discounts(code);
CREATE INDEX IF NOT EXISTS idx_discounts_status ON discounts(status);
CREATE INDEX IF NOT EXISTS idx_discounts_dates ON discounts(valid_from, valid_until);

-- ============================================================================
-- TABLE 10: booking_channels (V1.1+ - Simplified for V1.0)
-- ============================================================================
CREATE TABLE IF NOT EXISTS booking_channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    channel_type VARCHAR(50) NOT NULL
        CHECK(channel_type IN ('ota', 'direct', 'corporate', 'api')),
    api_url VARCHAR(255),
    api_key VARCHAR(255),
    api_secret VARCHAR(255),
    webhook_url VARCHAR(255),
    is_enabled BOOLEAN DEFAULT TRUE,
    auto_confirm BOOLEAN DEFAULT FALSE,
    sync_enabled BOOLEAN DEFAULT FALSE,
    sync_interval_minutes INTEGER DEFAULT 60,
    commission_percentage DECIMAL(5,2) DEFAULT 0,
    commission_fixed_amount DECIMAL(12,2) DEFAULT 0,
    support_contact VARCHAR(255),
    support_email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_booking_channels_code ON booking_channels(code);
CREATE INDEX IF NOT EXISTS idx_booking_channels_enabled ON booking_channels(is_enabled);

-- ============================================================================
-- INITIAL DATA: Booking Channels (V1.0)
-- ============================================================================
INSERT INTO booking_channels (name, code, description, channel_type, is_enabled)
VALUES
    ('Direct Booking', 'direct', 'Walk-in, phone, email, website', 'direct', TRUE),
    ('Tiket.com', 'tiket', 'Tiket OTA integration', 'ota', TRUE),
    ('Traveloka', 'traveloka', 'Traveloka OTA integration', 'ota', TRUE),
    ('Booking.com', 'booking', 'Booking.com OTA integration', 'ota', TRUE),
    ('Other', 'other', 'Other booking sources', 'direct', TRUE)
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- INITIAL DATA: Default Settings (V1.0)
-- ============================================================================
INSERT INTO settings (setting_key, setting_value, setting_type, is_editable, description, category)
VALUES
    ('hotel_name', 'My Hotel', 'string', TRUE, 'Hotel name', 'Hotel Information'),
    ('hotel_address', 'Hotel Address', 'string', TRUE, 'Hotel physical address', 'Hotel Information'),
    ('hotel_phone', '+62xxx', 'string', TRUE, 'Hotel contact phone', 'Hotel Information'),
    ('check_in_time', '14:00', 'string', TRUE, 'Standard check-in time', 'Booking Configuration'),
    ('check_out_time', '12:00', 'string', TRUE, 'Standard check-out time', 'Booking Configuration'),
    ('timezone', 'Asia/Jakarta', 'string', TRUE, 'Hotel timezone', 'Localization'),
    ('currency', 'IDR', 'string', TRUE, 'Hotel currency code', 'Localization'),
    ('default_language', 'id', 'string', TRUE, 'Default language (en/id)', 'Localization'),
    ('file_storage_config', '{"storage_backend": "gcs", "max_file_size_mb": 10, "allowed_file_types": ["jpg", "jpeg", "png", "pdf"], "retention_days": 2555}', 'json', TRUE, 'File storage configuration', 'File Storage'),
    ('booking_channels_config', '{"enabled_channels": ["direct", "tiket", "traveloka", "booking", "other"], "channels": {"direct": {"name": "Direct Booking", "enabled": true, "commission_percentage": 0}, "tiket": {"name": "Tiket.com", "enabled": true, "commission_percentage": 15}, "traveloka": {"name": "Traveloka", "enabled": true, "commission_percentage": 18}, "booking": {"name": "Booking.com", "enabled": true, "commission_percentage": 20}, "other": {"name": "Other", "enabled": true, "commission_percentage": 0}}}', 'json', TRUE, 'Booking channels configuration', 'Booking Channels')
ON CONFLICT (setting_key) DO NOTHING;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- All v1.0 tables created successfully
-- Database is ready for backend API implementation
-- Use SQLAlchemy models in backend/models/ directory
