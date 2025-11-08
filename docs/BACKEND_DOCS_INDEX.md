# Backend Documentation Index

## Overview
Complete backend architecture documentation for the Hotel Management System. All files have been generated from a thorough analysis of the FastAPI backend codebase.

## Generated Documentation Files

### 1. BACKEND_EXPLORATION_SUMMARY.md
**Purpose:** Executive summary of backend exploration
**Length:** 11 KB
**Contents:**
- Overview and key findings
- Technology stack details
- Database architecture (12 models)
- API structure (11 routers, 40+ endpoints)
- Data model relationships
- Security features
- Frontend development recommendations
- File organization
- Performance considerations

**Best for:** Quick overview, planning, understanding the big picture

---

### 2. BACKEND_ARCHITECTURE_SUMMARY.md (COMPREHENSIVE)
**Purpose:** Complete technical reference documentation
**Length:** 26 KB
**Contents:**
- Project overview and tech stack
- Detailed database models (1-12):
  - User, RoomType, Room, RoomImage, RoomTypeImage
  - Guest, GuestImage
  - Reservation, Payment, PaymentAttachment
  - Setting, Discount, BookingChannel
  - Each with fields, relationships, methods
- Complete API endpoints documentation:
  - Authentication (2 endpoints)
  - Guests (5 endpoints)
  - Reservations (9 endpoints)
  - Payments (5 endpoints)
  - Rooms (2 endpoints)
  - Users (3 endpoints)
  - Dashboard (3 endpoints)
  - System (2 endpoints)
- All endpoints include:
  - HTTP method and path
  - Request body examples
  - Response examples (200, 201, error codes)
  - Query parameters
  - Status codes
- Authentication & authorization details
- Error handling guide
- Data validation rules
- Business logic explanations
- Database connection configuration
- Frontend development guide
- Configuration & environment variables

**Best for:** Developers building features, understanding data models, API reference

---

### 3. API_QUICK_REFERENCE.md
**Purpose:** Quick lookup guide for common operations
**Length:** 7.4 KB
**Contents:**
- Quick navigation links to all endpoints
- Authentication header format
- Common request/response examples:
  - Login
  - Create guest
  - Check availability
  - Create reservation
  - Record payment
  - Check-in guest
  - Check-out guest
  - Get balance
- Query parameters
- Status codes reference table
- Important notes (dates, amounts, status flows)
- Error examples
- curl testing examples
- Frontend integration tips
- Swagger documentation links

**Best for:** Quick lookups while coding, testing, copy-paste examples

---

### 4. BACKEND_JWT_RECEPTIONIST_UPDATE.md (Existing)
**Purpose:** JWT authentication and receptionist tracking details
**Contents:** Authentication implementation details specific to receptionist workflows

---

## Quick Navigation

### For Frontend Developers
1. Start with: **BACKEND_EXPLORATION_SUMMARY.md**
   - Understand what the system does
   - Learn about core features
   - See data model relationships
   
2. Reference: **BACKEND_ARCHITECTURE_SUMMARY.md**
   - When building specific features
   - To understand request/response formats
   - For validation rules
   
3. Lookup: **API_QUICK_REFERENCE.md**
   - Quick endpoint lists
   - Common examples
   - Testing with curl

### For Backend Developers
1. Start with: **BACKEND_ARCHITECTURE_SUMMARY.md**
   - Complete technical reference
   - All models documented
   - All endpoints documented

2. Reference: **BACKEND_JWT_RECEPTIONIST_UPDATE.md**
   - Authentication specifics
   - Token implementation details

### For Product/Project Managers
1. Read: **BACKEND_EXPLORATION_SUMMARY.md**
   - Feature overview
   - Workflow descriptions
   - Development roadmap

## Key Information Summary

### Database Models (12 total)
1. User - Authentication
2. RoomType - Room categories
3. Room - Individual rooms
4. RoomImage - Room photos
5. RoomTypeImage - Category photos
6. Guest - Guest profiles
7. GuestImage - Guest ID photos
8. Reservation - Bookings
9. Payment - Transactions
10. PaymentAttachment - Payment proofs
11. Setting - Configuration
12. Discount - Promotional codes
13. BookingChannel - OTA integrations

### API Routers (11 total)
- auth_router (authentication)
- guests_router (guest management)
- reservations_router (booking operations)
- payments_router (payment processing)
- rooms_router (room inventory)
- users_router (user management)
- dashboard_router (analytics)
- expenses_router (planned)
- tenants_router (planned)
- Plus health check and API info

### Total API Endpoints: 40+

### Key Features
- Reservation workflow (confirmed → checked_in → checked_out)
- Flexible payment system (multiple types and methods)
- Deposit management with settlement logic
- Receptionist check-in tracking
- Dashboard analytics
- Guest ID document tracking
- Room availability checking
- Balance tracking across payments

### Tech Stack
- FastAPI 0.104.1
- PostgreSQL / SQLite
- SQLAlchemy 2.0.44
- Pydantic v2
- Bcrypt security
- Bearer token authentication

### Authentication
- Token-based (16-hour expiration)
- Bcrypt password hashing
- All endpoints protected except /health and /api

## How to Use This Documentation

### Scenario 1: Building Guest Management Feature
1. Read: BACKEND_EXPLORATION_SUMMARY.md (Guest section)
2. Reference: BACKEND_ARCHITECTURE_SUMMARY.md (Guest models and endpoints)
3. Lookup: API_QUICK_REFERENCE.md (Guest examples)
4. Access: Swagger UI at /api/docs for interactive testing

### Scenario 2: Implementing Reservation Booking
1. Read: BACKEND_ARCHITECTURE_SUMMARY.md (Reservation model, workflow)
2. Reference endpoints:
   - GET /api/reservations/availability
   - POST /api/reservations
   - POST /api/payments
   - POST /api/reservations/{id}/check-in
3. Example: API_QUICK_REFERENCE.md

### Scenario 3: Understanding Payment System
1. Read: BACKEND_ARCHITECTURE_SUMMARY.md (Payment and Deposit sections)
2. Reference: Payment and PaymentAttachment models
3. Workflow: Payment Types, Methods, Balance Calculation
4. Examples: API_QUICK_REFERENCE.md

### Scenario 4: Setting Up Frontend Project
1. Start with: BACKEND_EXPLORATION_SUMMARY.md
2. Create API service layer based on architecture
3. Use models as TypeScript interfaces (from BACKEND_ARCHITECTURE_SUMMARY.md)
4. Implement authentication first
5. Reference examples for testing

## Document Locations

All files in `/docs/` folder:
- BACKEND_EXPLORATION_SUMMARY.md
- BACKEND_ARCHITECTURE_SUMMARY.md
- API_QUICK_REFERENCE.md
- BACKEND_JWT_RECEPTIONIST_UPDATE.md (existing)

Source code in `/backend/` folder:
- app.py (main application)
- models.py (12 data models)
- schemas.py (Pydantic validation)
- database.py (database configuration)
- security.py (authentication)
- routes/ (API endpoints)

## API Documentation Tools

### Interactive API Documentation
- Swagger UI: `http://localhost:8001/api/docs`
- OpenAPI JSON: `http://localhost:8001/api/openapi.json`
- ReDoc: (if configured)

### Health Check
- Endpoint: `GET /health`
- Returns: System status, database connectivity, table counts

### API Info
- Endpoint: `GET /api`
- Returns: API version, documentation links

## Important Business Rules

1. **Guest Creation Required Fields:**
   - full_name
   - id_type (passport, driver_license, national_id, etc.)
   - id_number (ID document number)

2. **Reservation Workflow:**
   - Check availability first
   - Cannot book if no rooms available
   - Generates unique confirmation number
   - Status: confirmed → checked_in → checked_out

3. **Payment System:**
   - Supports multiple payment types (full, downpayment, deposit, adjustment)
   - Supports multiple methods (cash, card, transfer, e-wallet, other)
   - Tracks balance: total_amount - total_paid
   - Can have partial/multiple payments per reservation

4. **Deposit Handling:**
   - Refundable security deposit collected at booking
   - At check-out:
     - If balance unpaid: Use deposit to cover
     - If balance paid: Return full deposit
     - If overpaid: Calculate and process refund

5. **Check-In Tracking:**
   - Records which staff member (receptionist) did check-in
   - Records timestamp of check-in
   - Can optionally require payment before allowing check-in

## Development Roadmap

### Phase 1 (Core Features) - Backend Complete
- Authentication system ✓
- Guest management ✓
- Reservation booking ✓
- Payment processing ✓
- Check-in/check-out ✓
- Room management ✓
- Basic dashboard ✓

### Phase 2 (Advanced) - Needs Frontend
- Image uploads (guest IDs, room photos)
- Payment proof attachments
- Advanced dashboard with reports
- Expense tracking
- Long-term tenant management
- OTA integrations
- Discount codes

### Phase 3 (Future)
- Revenue management
- Housekeeping management
- Maintenance tracking
- Guest communication
- Integration with payment gateways
- Mobile app

## Troubleshooting & Support

### Common Issues

**401 Unauthorized**
- Check token validity (16-hour expiration)
- Verify Authorization header format: `Bearer {token}`
- Re-authenticate if token expired

**404 Not Found**
- Verify endpoint path and method
- Check resource ID exists
- Review error detail for exact issue

**400 Bad Request**
- Check request body format
- Verify date format: YYYY-MM-DD
- Ensure required fields provided
- Check enum values (status, payment_method, etc.)

**409 Conflict**
- Usually availability issues
- Check room type has rooms
- Verify date range
- Check reservation status flow

### Documentation Inconsistencies
If you find documentation that doesn't match actual API behavior:
1. Check Swagger UI at /api/docs (source of truth)
2. Review latest code in /backend/ folder
3. Run health check to verify system status

## File Statistics

| Document | Size | Words | Focus |
|----------|------|-------|-------|
| BACKEND_EXPLORATION_SUMMARY.md | 11 KB | 3,200 | Overview & recommendations |
| BACKEND_ARCHITECTURE_SUMMARY.md | 26 KB | 7,500 | Comprehensive reference |
| API_QUICK_REFERENCE.md | 7.4 KB | 2,100 | Quick lookup & examples |
| **Total** | **44.4 KB** | **12,800** | Complete backend docs |

---

**Generated:** November 8, 2025
**Status:** Complete - Ready for frontend development
**Next Step:** Start frontend implementation using this documentation as blueprint
