-- Hotel Management System - Create Missing Core Tables
-- This file creates the core tables that were missing from migration 1

-- ============================================================================
-- TABLE: reservations (Booking System)
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
    deposit_amount DECIMAL(12,2) DEFAULT 0,
    special_requests TEXT,
    status VARCHAR(20) DEFAULT 'confirmed'
        CHECK(status IN ('confirmed', 'checked_in', 'checked_out', 'cancelled')),
    booking_source VARCHAR(50),
    booking_channel_id INTEGER,
    created_by INTEGER NOT NULL,
    checked_in_by INTEGER,
    checked_in_at TIMESTAMP,
    checked_out_at TIMESTAMP,
    deposit_returned_at TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE RESTRICT,
    FOREIGN KEY (room_type_id) REFERENCES room_types(id) ON DELETE RESTRICT,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (checked_in_by) REFERENCES users(id) ON DELETE SET NULL,
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
-- TABLE: payments (Payment Tracking)
-- ============================================================================
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    reservation_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL
        CHECK(payment_method IN ('cash', 'credit_card', 'debit_card',
              'bank_transfer', 'e_wallet', 'other')),
    payment_type VARCHAR(20) DEFAULT 'full'
        CHECK(payment_type IN ('full', 'downpayment', 'deposit', 'adjustment')),
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
-- TABLE: payment_attachments (Payment Proof Uploads)
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
