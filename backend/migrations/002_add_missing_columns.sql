-- Hotel Management System v1.0 - Add Missing Columns
-- Supabase PostgreSQL Migration
-- Created: November 8, 2025
-- Status: Fixes schema mismatches between models.py and database

-- ============================================================================
-- Add missing column to payments table: payment_type
-- ============================================================================
ALTER TABLE IF EXISTS payments
ADD COLUMN IF NOT EXISTS payment_type VARCHAR(20) DEFAULT 'full'
    CHECK(payment_type IN ('full', 'downpayment', 'deposit', 'adjustment'));

-- ============================================================================
-- Add missing columns to reservations table
-- ============================================================================
ALTER TABLE IF EXISTS reservations
ADD COLUMN IF NOT EXISTS deposit_amount DECIMAL(12,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS checked_in_by INTEGER,
ADD COLUMN IF NOT EXISTS deposit_returned_at TIMESTAMP;

-- Add foreign key for checked_in_by if not already present
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'reservations' AND constraint_name = 'fk_reservations_checked_in_by'
    ) THEN
        ALTER TABLE reservations
        ADD CONSTRAINT fk_reservations_checked_in_by
        FOREIGN KEY (checked_in_by) REFERENCES users(id) ON DELETE SET NULL;
    END IF;
END $$;

-- ============================================================================
-- Create guest_images table if it doesn't exist
-- ============================================================================
CREATE TABLE IF NOT EXISTS guest_images (
    id SERIAL PRIMARY KEY,
    guest_id INTEGER NOT NULL,
    image_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_by_user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_guest_images_guest ON guest_images(guest_id);
CREATE INDEX IF NOT EXISTS idx_guest_images_type ON guest_images(image_type);

-- ============================================================================
-- Create expenses table
-- ============================================================================
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    category VARCHAR(50) NOT NULL
        CHECK(category IN ('utilities', 'maintenance', 'cleaning', 'supplies', 'repairs', 'insurance', 'taxes', 'other')),
    amount DECIMAL(12,2) NOT NULL,
    description TEXT,
    receipt_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- All missing columns and tables have been added
-- Database schema is now aligned with models.py
