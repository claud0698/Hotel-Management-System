# Hotel Management System - TODO List

## High Priority Features

### 1. Settings Management Page
- **Status**: Not Started
- **Description**: Create a Settings page where admins can configure:
  - **Booking Sources (OTA Platforms)**
    - Allow admin to add/edit/delete booking sources
    - Currently hardcoded: Direct, Tiket.com, Traveloka
    - Should be stored in database and fetched dynamically
    - Used in ReservationsPage booking source dropdown
  - **Hotel Information**
    - Hotel name
    - Hotel address
    - Contact information
    - Tax ID
  - **Rate Management**
    - Default nightly rates by room type
    - Seasonal pricing (if applicable)
  - **Payment Settings**
    - Accepted payment methods
    - Deposit requirements
    - Cancellation policies
- **Related Files**:
  - Frontend: Create `frontend/src/pages/SettingsPage.tsx`
  - Backend: Create settings API endpoints
  - Database: Create settings table

### 2. Dashboard Improvements
- **Status**: Pending
- **Description**:
  - Add more analytics and metrics
  - Show booking sources breakdown
  - Revenue trends
  - Occupancy forecasting

### 3. Reservations Features
- **Status**: In Progress
- **Current**: Basic CRUD, check-in/out, delete functionality
- **TODO**:
  - Add notes/comments on reservations
  - Export reservation data (PDF, CSV)
  - Reservation templates for recurring bookings
  - Group booking support

### 4. User Roles & Permissions
- **Status**: Not Started
- **Description**:
  - Admin: Full access
  - Manager: Can manage all operations except settings
  - Receptionist: Can only check-in/out and view reservations
  - Staff: View-only access
- **Current State**: Basic user roles exist but no permission enforcement

### 5. Payment Processing
- **Status**: Partial
- **Current**: Manual payment recording
- **TODO**:
  - Payment gateway integration (Stripe, PayPal, etc.)
  - Automated payment reminders
  - Payment history and reconciliation
  - Refund management

### 6. Reporting
- **Status**: Not Started
- **Description**:
  - Daily/Monthly revenue reports
  - Occupancy reports
  - Guest reports
  - Expense reports
  - Export to Excel/PDF

## Medium Priority Features

### 1. Guest Management Enhancements
- Store guest preferences (room type, floor, amenities)
- Guest loyalty program tracking
- VIP guest management
- Guest communication preferences

### 2. Room Management Improvements
- Room availability calendar view
- Bulk room operations
- Room condition/maintenance tracking
- Room image gallery

### 3. Expense Tracking
- Expense categories customization
- Budget tracking
- Expense reports by category

### 4. Email Notifications
- Reservation confirmations
- Check-in reminders
- Payment reminders
- Expense alerts

## Low Priority / Nice to Have

### 1. Multi-language Support
- **Status**: In Progress
- Currently supporting: English, Bahasa Indonesia
- Could add: Chinese, Japanese, etc.

### 2. Mobile App
- React Native app for mobile check-ins
- On-the-go management

### 3. Integration with Third-party Services
- Calendar sync (Google Calendar, iCal)
- Accounting software integration
- PMS (Property Management System) integration

### 4. Advanced Analytics
- Machine learning for pricing optimization
- Demand forecasting
- Guest segmentation

## Bug Fixes / Technical Debt

- [ ] Fix TypeScript errors in various components
- [ ] Complete missing API endpoints
- [ ] Add proper error handling across the app
- [ ] Add input validation on all forms
- [ ] Improve loading states and skeleton screens
- [ ] Add unit tests
- [ ] Add integration tests

## Recently Completed

✅ Mobile-friendly responsive design with collapsible sidebar
✅ Comprehensive i18n (English & Indonesian) support
✅ Delete confirmation modal for reservations
✅ Nightly rate auto-population in reservation form
✅ Discount percentage calculation (frontend-only)
✅ Booking source tracking (Direct, Tiket.com, Traveloka)
✅ Check-in/Check-out functionality
✅ Payment recording

## Current Architecture

### Frontend Stack
- React 19.1.1
- TypeScript 5.9.3
- Vite 7.1.7
- Tailwind CSS 3.4.1
- Zustand (state management)
- React Router 7.0.0
- i18next (internationalization)

### Backend Stack
- FastAPI (Python)
- SQLAlchemy ORM
- PostgreSQL (production) / SQLite (development)
- Bcrypt (password hashing)

## Notes

- Settings page is the next major feature to implement
- Booking sources should be moved from hardcoded list to database
- Consider implementing role-based access control before adding more features
- Payment processing will require security audit
