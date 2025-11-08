-- Hotel Management System - Mock Data for Local Testing
-- Created: November 8, 2025

-- ============================================================================
-- INSERT: Users (Admin and staff)
-- ============================================================================
INSERT INTO users (username, password_hash, email, full_name, phone, role, status) VALUES
('admin', '$2b$12$EIx3F/ClUlxm6/O5gx6EAO.K.j3BYqr9E5yR3aBLOQP1K6TDJ3uEK', 'admin@hotel.local', 'Admin User', '+62-821-1111-1111', 'admin', 'active'),
('manager', '$2b$12$P2qczQhHF8nQH5lPr0sLJOnO.z/pDR5B9qyDr8MvVGEiU9bwKxcZK', 'manager@hotel.local', 'Hotel Manager', '+62-821-2222-2222', 'user', 'active'),
('receptionist', '$2b$12$Z5VRY9K6bP4tqKxC2v8V4eFJgUqGJ/HXL3J2pNh5RmVxDzDJLZxXC', 'receptionist@hotel.local', 'Receptionist', '+62-821-3333-3333', 'user', 'active')
ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- INSERT: Room Types (8 room types as per hotel specification)
-- ============================================================================
INSERT INTO room_types (name, code, description, base_capacity_adults, base_capacity_children, bed_config, default_rate, amenities, is_active) VALUES
('Standard Room', 'STD', 'Kamar yang sangat terjangkau dan nyaman untuk beristirahat dengan fasilitas memadai. Dilengkapi kasur double. Ukuran: 4,82m x 3,46m. Amenities: AC, TV, Shower (tanpa water heater), Kettle, Mineral Water', 2, 0, '1 Double Bed', 300000, 'AC, TV, Shower (tanpa water heater), Kettle, Mineral Water', TRUE),
('Standard Twin Room', 'STT', 'Kamar terjangkau dan nyaman dengan dua kasur tipe single. Ukuran: 4,82m x 3,46m. Amenities: AC, TV, Shower (tanpa water heater), Kettle, Mineral Water', 2, 0, '2 Single Beds', 300000, 'AC, TV, Shower (tanpa water heater), Kettle, Mineral Water', TRUE),
('Superior Room', 'SUP', 'Kamar nyaman yang menjadi pilihan utama tamu pekerja dinas. Dilengkapi kasur queen. Ukuran: 4,82m x 3,46m. Amenities: AC, TV, Shower (dengan water heater), Kettle, Mineral Water', 2, 0, '1 Queen Bed', 400000, 'AC, TV, Shower (dengan water heater), Kettle, Mineral Water', TRUE),
('Superior Twin Room', 'SUT', 'Kamar nyaman untuk pekerja dinas. Dilengkapi dua kasur single. Ukuran: 4,82m x 3,46m. Amenities: AC, TV, Shower (dengan water heater), Kettle, Mineral Water', 2, 0, '2 Single Beds', 400000, 'AC, TV, Shower (dengan water heater), Kettle, Mineral Water', TRUE),
('Deluxe Room', 'DEL', 'Kamar luas dan tenang dengan balkon dan view laut. Dilengkapi kasur king. Cocok untuk pasangan/keluarga. Ukuran: 4,72m x 4,60m. Amenities: AC, TV, Shower (dengan water heater), Mini Fridge, Kettle, Mineral Water', 2, 0, '1 King Bed', 500000, 'AC, TV, Shower (dengan water heater), Mini Fridge, Kettle, Mineral Water', TRUE),
('Junior Suite Room', 'JUS', 'Terletak dekat laut dengan interior modern dan tenang. Dilengkapi dua kasur single. Ukuran: 6,47m x 3,60m. Amenities: AC, TV, Shower (dengan water heater), Mini Fridge, Kettle, Mineral Water', 2, 0, '2 Single Beds', 550000, 'AC, TV, Shower (dengan water heater), Mini Fridge, Kettle, Mineral Water', TRUE),
('Suite Room', 'SUI', 'Kamar luas dan tenang dengan view laut, kasur king. Cocok untuk pasangan/keluarga. Ukuran: 5,96m x 4,42m. Amenities: AC, TV, Shower (dengan water heater), Mini Fridge, Kettle, Mineral Water', 2, 0, '1 King Bed', 600000, 'AC, TV, Shower (dengan water heater), Mini Fridge, Kettle, Mineral Water', TRUE),
('Suite Room with Ocean View', 'SUO', 'Kamar luas dan tenang dengan balkon dan view laut. Dilengkapi kasur king. Ukuran: 5,96m x 4,42m. Amenities: AC, TV, Shower (dengan water heater), Mini Fridge, Kettle, Mineral Water', 2, 0, '1 King Bed', 650000, 'AC, TV, Shower (dengan water heater), Mini Fridge, Kettle, Mineral Water', TRUE)
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- INSERT: Rooms (22 rooms total distributed across 8 room types)
-- ============================================================================
INSERT INTO rooms (room_number, floor, room_type_id, status, is_active) VALUES
('101', 1, 1, 'available', TRUE),
('102', 1, 1, 'available', TRUE),
('103', 1, 1, 'available', TRUE),
('104', 1, 1, 'available', TRUE),
('105', 1, 1, 'available', TRUE),
('201', 2, 2, 'available', TRUE),
('202', 2, 2, 'available', TRUE),
('203', 2, 3, 'available', TRUE),
('204', 2, 3, 'available', TRUE),
('205', 2, 3, 'available', TRUE),
('206', 2, 3, 'available', TRUE),
('207', 2, 3, 'available', TRUE),
('208', 2, 4, 'available', TRUE),
('209', 2, 4, 'available', TRUE),
('301', 3, 5, 'available', TRUE),
('302', 3, 5, 'available', TRUE),
('303', 3, 5, 'available', TRUE),
('304', 3, 6, 'available', TRUE),
('305', 3, 6, 'available', TRUE),
('306', 3, 6, 'available', TRUE),
('307', 3, 6, 'available', TRUE),
('308', 3, 6, 'available', TRUE),
('401', 4, 7, 'available', TRUE),
('402', 4, 7, 'available', TRUE),
('403', 4, 8, 'available', TRUE),
('404', 4, 8, 'available', TRUE)
ON CONFLICT (room_number) DO NOTHING;

-- ============================================================================
-- INSERT: Guests
-- ============================================================================
INSERT INTO guests (full_name, email, phone, phone_country_code, id_type, id_number, nationality, is_vip, notes) VALUES
('John Doe', 'john@example.com', '+1-555-0123', '+1', 'passport', 'A12345678', 'USA', FALSE, 'First-time guest'),
('Jane Smith', 'jane@example.com', '+62-821-4444-4444', '+62', 'national_id', '1234567890123456', 'Indonesia', TRUE, 'VIP member'),
('Robert Johnson', 'robert@example.com', '+44-201-1111-111', '+44', 'driver_license', 'GB123456', 'UK', FALSE, ''),
('Maria Garcia', 'maria@example.com', '+34-911-111-111', '+34', 'passport', 'ES9876543', 'Spain', FALSE, 'Travelling with family'),
('Chen Wei', 'chen@example.com', '+86-10-1111-1111', '+86', 'national_id', '110101199003011234', 'China', TRUE, 'Corporate booking')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- INSERT: Reservations
-- ============================================================================
INSERT INTO reservations (confirmation_number, guest_id, check_in_date, check_out_date, room_type_id, room_id, adults, children, rate_per_night, subtotal, discount_amount, total_amount, deposit_amount, special_requests, status, created_by) VALUES
('CONF-001', 1, CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days', 1, 1, 1, 0, 500000, 1000000, 0, 1000000, 250000, 'Late check-in preferred', 'confirmed', 1),
('CONF-002', 2, CURRENT_DATE + INTERVAL '1 day', CURRENT_DATE + INTERVAL '4 days', 2, 2, 2, 1, 750000, 2250000, 150000, 2100000, 500000, 'Birthday celebration', 'confirmed', 2),
('CONF-003', 3, CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE + INTERVAL '1 day', 3, 3, 2, 0, 1200000, 2400000, 0, 2400000, 500000, '', 'checked_in', 1),
('CONF-004', 4, CURRENT_DATE + INTERVAL '5 days', CURRENT_DATE + INTERVAL '7 days', 2, NULL, 2, 2, 750000, 1500000, 100000, 1400000, 0, 'Family trip', 'confirmed', 3),
('CONF-005', 5, CURRENT_DATE + INTERVAL '10 days', CURRENT_DATE + INTERVAL '14 days', 1, NULL, 1, 0, 500000, 2000000, 200000, 1800000, 450000, 'Corporate stay', 'confirmed', 2)
ON CONFLICT (confirmation_number) DO NOTHING;

-- ============================================================================
-- INSERT: Payments
-- ============================================================================
INSERT INTO payments (reservation_id, payment_date, amount, payment_method, payment_type, reference_number, transaction_id, notes, created_by, is_refund) VALUES
(1, CURRENT_DATE, 250000, 'bank_transfer', 'deposit', 'TRF-001', 'TXN-001', 'Deposit payment', 1, FALSE),
(1, CURRENT_DATE, 750000, 'credit_card', 'full', 'CC-001', 'TXN-002', 'Final payment', 1, FALSE),
(2, CURRENT_DATE - INTERVAL '1 day', 500000, 'bank_transfer', 'downpayment', 'TRF-002', 'TXN-003', '50% downpayment', 2, FALSE),
(3, CURRENT_DATE - INTERVAL '1 day', 1200000, 'credit_card', 'full', 'CC-002', 'TXN-004', '', 1, FALSE),
(4, CURRENT_DATE + INTERVAL '5 days', 700000, 'cash', 'downpayment', 'CASH-001', '', 'Walk-in payment', 3, FALSE)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- INSERT: Expenses
-- ============================================================================
INSERT INTO expenses (date, category, amount, description, receipt_url) VALUES
(CURRENT_DATE - INTERVAL '2 days', 'utilities', 500000, 'Monthly electricity bill', 'https://example.com/receipts/util-001'),
(CURRENT_DATE - INTERVAL '1 day', 'maintenance', 1500000, 'AC unit repair for room 301', 'https://example.com/receipts/maint-001'),
(CURRENT_DATE, 'cleaning', 300000, 'Professional cleaning supplies', 'https://example.com/receipts/clean-001'),
(CURRENT_DATE, 'supplies', 200000, 'Bathroom amenities and linens', 'https://example.com/receipts/supp-001'),
(CURRENT_DATE + INTERVAL '1 day', 'insurance', 5000000, 'Monthly property insurance', 'https://example.com/receipts/ins-001')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Verify Data
-- ============================================================================
SELECT '✓ Users' as Status, COUNT(*) as Count FROM users
UNION ALL
SELECT '✓ Room Types', COUNT(*) FROM room_types
UNION ALL
SELECT '✓ Rooms', COUNT(*) FROM rooms
UNION ALL
SELECT '✓ Guests', COUNT(*) FROM guests
UNION ALL
SELECT '✓ Reservations', COUNT(*) FROM reservations
UNION ALL
SELECT '✓ Payments', COUNT(*) FROM payments
UNION ALL
SELECT '✓ Expenses', COUNT(*) FROM expenses;
