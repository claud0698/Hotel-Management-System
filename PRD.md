# Product Requirements Document (PRD)
## Kos Management Dashboard

**Version**: 1.0
**Last Updated**: October 24, 2025
**Status**: In Development

---

## 1. Executive Summary

The **Kos Management Dashboard** is a web-based application designed to help property managers and owners of shared room rental properties (Kos, Boarding Houses, Co-living spaces) in Indonesia streamline their operations. The system will enable managers to efficiently track tenants, rooms, payments, and finances through an intuitive dashboard.

### Business Problem
Property managers currently face challenges in:
- Tracking which rooms are occupied and which are available
- Managing tenant information and payment history
- Identifying overdue payments quickly
- Monitoring income and expenses manually
- Generating financial reports

### Solution Overview
A centralized digital platform that provides:
- Real-time room occupancy status visualization
- Tenant management with complete profiles
- Payment tracking with automatic overdue alerts
- Income and expense monitoring
- Financial reporting and analytics

---

## 2. Product Vision & Goals

### Vision Statement
"Make it simple for property managers to manage their room rental business with confidence and clarity."

### Business Goals
1. **Operational Efficiency**: Reduce time spent on administrative tasks by 70%
2. **Payment Tracking**: Achieve 95% on-time payment collection through better tracking
3. **Financial Visibility**: Provide clear monthly and yearly profit/loss visibility
4. **Data Centralization**: Keep all business data in one secure, accessible location

### Success Metrics
- User can view occupancy status in < 2 seconds
- User can record a payment in < 1 minute
- System uptime: 99.5%
- All data persists reliably with automatic backups
- Payment records are 100% accurate

---

## 3. Target Users

### Primary User
- **Property Owner/Manager** of a small to medium-sized Kos/Boarding House
- Age: 25-60 years old
- Tech-savviness: Basic to Intermediate
- Frequency of use: Daily
- Main pain point: Time-consuming manual management of tenants and finances

### User Characteristics
- May not have formal IT training
- Prefers simple, intuitive interfaces
- Primarily uses desktop/laptop for management
- Needs mobile accessibility for quick lookups
- Wants reliable data backup

### Secondary Users
- Accountant/Financial Administrator (view-only access for reporting)
- Family members helping with management (limited access)
- Note: v1.0 will only support single admin user

---

## 4. Core Features & Requirements

### 4.1 Authentication & User Management

#### Feature: Admin Login
- **Description**: Secure login system for property manager
- **Acceptance Criteria**:
  - User can register new account with username, email, password
  - User can login with username/password
  - Session persists for 30 days (auto-logout after inactivity)
  - Password is hashed and never stored in plain text
  - User can view their profile
  - Invalid login attempts show clear error messages

#### Feature: Password Management (Future)
- **Note**: Not in v1.0 - manual password reset only

---

### 4.2 Room Management

#### Feature: Room CRUD Operations
- **Description**: Create, view, edit, and delete room listings
- **Acceptance Criteria**:
  - User can add new room with: room number, floor, type, monthly rate, amenities
  - User can edit all room details
  - User can delete a room (warning if occupied)
  - Room numbers are unique across property
  - Monthly rate is displayed in IDR currency

#### Feature: Room Status Tracking
- **Description**: Track current status of each room
- **Status Types**:
  - `available`: Room is empty and ready for occupancy
  - `occupied`: Room has an active tenant
  - `maintenance`: Room is being repaired/cleaned
- **Acceptance Criteria**:
  - Status updates automatically when tenant moves in/out
  - User can manually change status if needed
  - Current status is always visible in room list

#### Feature: Room Occupancy Grid Visualization
- **Description**: Visual display of all rooms with color-coded status
- **Acceptance Criteria**:
  - Grid shows all rooms at a glance
  - Color coding: Green (available), Blue (occupied), Yellow (maintenance)
  - Clicking room shows full details
  - Room numbers are clearly visible
  - Grid is responsive on all screen sizes
  - Display occupancy percentage

#### Feature: Room History
- **Description**: Track which tenants lived in each room and when
- **Acceptance Criteria**:
  - View complete history for each room
  - Shows move-in and move-out dates
  - Accessible from room detail view

---

### 4.3 Tenant Management

#### Feature: Tenant Profile Creation
- **Description**: Create and maintain tenant information
- **Data Collected**:
  - Full name (required)
  - Phone number
  - Email address
  - ID number (KTP, passport, etc.)
  - Move-in date
  - Status (active, inactive, moved out)
  - Additional notes
- **Acceptance Criteria**:
  - All tenant information is saved and retrievable
  - Tenant can be assigned to a room
  - Multiple tenants cannot be assigned to same room simultaneously
  - Tenant status reflects whether they're active or not

#### Feature: Tenant List View
- **Description**: View all tenants with search and filter options
- **Acceptance Criteria**:
  - List shows all tenants with key information
  - Search by name
  - Filter by status (active, inactive, moved out)
  - Filter by room
  - Sort by name or move-in date
  - Quick actions: view profile, mark for payment, edit, delete

#### Feature: Tenant-Room Assignment
- **Description**: Assign and reassign tenants to rooms
- **Acceptance Criteria**:
  - Assign tenant to room with move-in date
  - Cannot assign multiple tenants to same room
  - Changing tenant room updates both room and tenant records
  - Moving tenant out marks room as available
  - Previous occupancy is recorded in room history
  - Tenant status updates when room assignment changes

#### Feature: Tenant Deletion
- **Description**: Remove tenant from system
- **Acceptance Criteria**:
  - Cannot delete tenant with unpaid balances (future phase)
  - Shows warning if tenant has payment records
  - Confirms deletion action

---

### 4.4 Payment Tracking

#### Feature: Payment Recording
- **Description**: Record monthly rent payments from tenants
- **Payment Fields**:
  - Tenant (who paid)
  - Amount
  - Due date
  - Paid date (when actually paid)
  - Status (pending, paid, overdue)
  - Payment method (cash, transfer, check, etc.)
  - Receipt number (optional)
  - Notes (optional)
- **Acceptance Criteria**:
  - User can record new payment
  - Payment amount defaults to room's monthly rate
  - User can mark existing pending payment as paid
  - Paid date automatically set to current date when marking paid
  - All payment details are editable until confirmed

#### Feature: Payment Status Management
- **Description**: Automated status calculation for payments
- **Status Logic**:
  - `pending`: Not yet paid, due date not passed
  - `overdue`: Not yet paid, due date has passed
  - `paid`: Successfully paid
- **Acceptance Criteria**:
  - Status calculated automatically based on current date
  - Overdue status triggers visual alert
  - Easy to mark overdue payments as paid

#### Feature: Payment History Per Tenant
- **Description**: View complete payment history for each tenant
- **Acceptance Criteria**:
  - List all payments (paid and pending) for tenant
  - Show payment status progression
  - Display payment dates and amounts
  - Accessible from tenant profile

#### Feature: Payment List with Filters
- **Description**: View all payments with filtering options
- **Acceptance Criteria**:
  - View all payments across all tenants
  - Filter by status (pending, paid, overdue)
  - Filter by tenant
  - Filter by date range
  - Sort by due date or paid date
  - See total amounts for pending and overdue

#### Feature: Overdue Alert System
- **Description**: Highlight tenants with overdue payments
- **Acceptance Criteria**:
  - Dashboard shows count of overdue payments
  - Overdue list shows tenant and amount owed
  - Overdue items highlighted in red/orange
  - Quick action to mark as paid from overdue list

---

### 4.5 Income & Expense Tracking

#### Feature: Expense Recording
- **Description**: Log business expenses
- **Expense Fields**:
  - Date
  - Category (utilities, maintenance, supplies, cleaning, other)
  - Amount
  - Description
  - Receipt attachment (optional)
- **Acceptance Criteria**:
  - User can add new expense
  - All expense categories predefined but customizable
  - Expense date can be any date (not just today)
  - Expenses are editable and deletable
  - Amount stored in IDR

#### Feature: Expense Categories
- **Description**: Organize expenses by type
- **Default Categories**:
  - `utilities`: Electricity, water, internet
  - `maintenance`: Repairs, cleaning, upkeep
  - `supplies`: Office, household supplies
  - `cleaning`: Cleaning services
  - `other`: Miscellaneous

#### Feature: Income Calculation
- **Description**: Automatically calculate business income
- **Logic**:
  - Income = Sum of all paid payments in period
  - Counts only successfully paid rent
  - Excludes partial payments initially
- **Acceptance Criteria**:
  - Total income accurately reflects paid payments
  - Income can be filtered by date range
  - Income shows as IDR currency

#### Feature: Financial Summary
- **Description**: View income vs expenses comparison
- **Shows**:
  - Total income for period
  - Total expenses for period
  - Net profit (income - expenses)
  - Breakdown of expenses by category
  - Occupancy-based analysis
- **Acceptance Criteria**:
  - Accurate calculations
  - Monthly and yearly summaries available
  - Date range filtering works correctly
  - All values in IDR currency

---

### 4.6 Dashboard & Reporting

#### Feature: Dashboard Overview
- **Description**: Landing page showing key business metrics
- **Dashboard Sections**:

##### 4.6.1 Key Metrics Cards
- **Occupancy Rate**: percentage of occupied rooms
  - Shows: "8/10 rooms occupied (80%)"
  - Color changes based on occupancy (red <50%, yellow 50-80%, green >80%)
- **Monthly Revenue**: income for current month
  - Shows: Total paid rent in IDR
  - Link to payment details
- **Monthly Expenses**: expenses for current month
  - Shows: Total expenses in IDR by category breakdown
  - Link to expense details
- **Net Profit**: Monthly revenue - expenses
  - Shows: IDR amount
  - Color: Green if positive, Red if negative

##### 4.6.2 Room Status Summary
- Available rooms count
- Occupied rooms count
- Maintenance rooms count
- Visual occupancy grid

##### 4.6.3 Payment Status Alert
- Count of pending payments
- Count of overdue payments
- Total overdue amount
- Quick link to overdue list

##### 4.6.4 Recent Activity
- Latest 5 payments recorded
- Latest 5 expenses recorded
- Recent tenant sign-ups

#### Feature: Financial Reports
- **Description**: Detailed financial analysis
- **Report Types**:
  - Monthly income/expense summary
  - Yearly profit/loss statement
  - Expense breakdown by category (pie chart)
  - Income trend (line chart showing monthly revenue)
  - Room occupancy trend over time

#### Feature: Date Range Filtering
- **Description**: View metrics for custom time periods
- **Options**:
  - Current month (default)
  - Last 3 months
  - Last 6 months
  - Last 12 months
  - Custom date range

#### Feature: Data Export
- **Description**: Export data for accounting/analysis
- **Export Formats**:
  - CSV (payments, expenses, tenants)
  - PDF (financial report)
- **Acceptance Criteria**:
  - Exports include all selected data
  - File naming includes date
  - Exports are downloadable

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Dashboard loads in < 2 seconds
- API responses within 200ms for normal queries
- Support up to 100 rooms and 200 tenants initially
- Smooth UI interactions without lag

### 5.2 Security
- All passwords hashed with bcrypt
- JWT tokens for session management
- HTTPS encryption in production
- Data validation on all inputs (prevent SQL injection)
- No sensitive data in logs
- Regular data backups

### 5.3 Reliability
- 99.5% uptime target
- Automatic daily backups
- Data recovery procedures documented
- No loss of data from system crashes

### 5.4 Usability
- Intuitive interface requiring minimal training
- Clear error messages
- Mobile-responsive design
- Keyboard navigation support
- Loading states for all async operations

### 5.5 Maintainability
- Clean, well-documented code
- Modular architecture
- Easy database migrations
- Clear API documentation

### 5.6 Scalability (Future)
- Database designed to support multiple properties
- API can handle 1000+ concurrent users
- Can migrate to managed database (PostgreSQL)

---

## 6. Technical Architecture

### 6.1 Technology Stack
- **Backend**: Python Flask with SQLAlchemy ORM
- **Frontend**: React with TypeScript and Tailwind CSS
- **Database**: SQLite (development) → PostgreSQL (production)
- **Authentication**: JWT tokens
- **API**: RESTful API with JSON
- **Hosting**: Cloud-based (TBD - could be Vercel, Heroku, or self-hosted)

### 6.2 Database Schema Overview
```
Users
├── id, username, password_hash, email

Rooms
├── id, room_number, floor, room_type
├── monthly_rate, status, amenities

Tenants
├── id, name, phone, email, id_number
├── move_in_date, move_out_date, current_room_id, status

Payments
├── id, tenant_id, amount, due_date, paid_date
├── status, payment_method, receipt_number

Expenses
├── id, date, category, amount, description

RoomHistory
├── id, room_id, tenant_id, move_in_date, move_out_date
```

### 6.3 API Endpoints
- `POST /api/auth/register` - Create admin account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Current user info
- `GET/POST/PUT/DELETE /api/rooms` - Room management
- `GET/POST/PUT/DELETE /api/tenants` - Tenant management
- `GET/POST/PUT/DELETE /api/payments` - Payment management
- `GET/POST/PUT/DELETE /api/expenses` - Expense management
- `GET /api/dashboard/metrics` - Dashboard metrics
- `GET /api/dashboard/summary` - Dashboard summary data

---

## 7. User Flows

### 7.1 First-Time Setup Flow
1. User registers account (username, email, password)
2. User logs in
3. User creates first room(s)
4. User adds first tenant(s)
5. System auto-generates first payment records for current month
6. Dashboard displays occupancy and metrics

### 7.2 Daily Management Flow
1. User logs in to dashboard
2. Views key metrics (occupancy, revenue, overdue payments)
3. Records new expenses if any
4. Checks overdue payment list
5. Marks received payments as paid
6. (Optional) Reviews financial summary

### 7.3 Tenant Move-In Flow
1. User creates new tenant profile
2. Assigns tenant to available room
3. System creates payment record for next month
4. Room status changes to occupied
5. Occupancy metrics update automatically

### 7.4 Tenant Move-Out Flow
1. User updates tenant status to "moved out"
2. Removes tenant from room (or change room)
3. System records move-out date
4. Room status changes to available
5. Occupancy metrics update
6. Payment records freeze for that tenant

### 7.5 Payment Recording Flow
1. Tenant makes payment
2. User finds tenant in payment list
3. Clicks "Mark as Paid" on pending payment
4. Enters payment method and receipt number
5. System marks payment as paid with current date
6. Payment appears in paid list
7. Dashboard revenue updates

---

## 8. Constraints & Assumptions

### Constraints
- Single property management only (v1.0)
- Single admin user (v1.0)
- Manual payment entry (no automatic payment gateway integration v1.0)
- Maximum 500 rooms, 1000 tenants (v1.0 limit)
- Data stored in single location (no multi-region backup initially)

### Assumptions
- Monthly rental cycle (due dates per month)
- IDR currency (Indonesia)
- Users have stable internet connection
- Users prefer web access over mobile app initially
- Data entry is manual (no bulk import initially)

---

## 9. Out of Scope (Future Versions)

### Phase 2 Features
- **Dashboard Report Export** (Priority: High)
  - Export financial reports (PDF/Excel) for custom time periods
  - Monthly, quarterly, yearly pre-set export options
  - User-selected date range export capability
  - Includes: Income summary, Expense breakdown, Net profit, Occupancy metrics
  - Export formats: PDF (formatted report), Excel (detailed data), CSV (data only)
  - Report customization: Select which sections to include
  - Scheduled email reports (monthly/quarterly)
  - Report templates for accounting
- Multi-user support with role-based access
- Automated payment reminders via SMS/Email
- Payment gateway integration (Midtrans, Xendit)
- Mobile app
- Utility bill tracking per room
- Lease contract management
- Maintenance request system
- Tenant application/screening
- Multiple property management

### Phase 3+ Features
- Advanced reporting and analytics
- Custom reports builder
- API for third-party integrations
- Accounting software integration (Xero, SAP)
- Tenant communication portal
- Auto-payment reconciliation

---

## 10. Success Criteria & Metrics

### Launch Success
- [ ] Zero critical bugs in production
- [ ] All core features working as specified
- [ ] Documentation complete
- [ ] User can complete full workflow in < 10 minutes
- [ ] Dashboard loads in < 2 seconds
- [ ] All data persists reliably

### Post-Launch Success
- [ ] User adoption: At least 2-3 property managers using daily
- [ ] Feature adoption: All core features used within first month
- [ ] Data accuracy: 100% accuracy in financial calculations
- [ ] Reliability: 99%+ uptime maintained
- [ ] User satisfaction: Positive feedback on ease of use

---

## 11. Glossary

| Term | Definition |
|------|-----------|
| **Kos** | Indonesian term for boarding house or shared room rental |
| **Tenant** | Person renting/living in a room |
| **Room Status** | Current state of room (available, occupied, maintenance) |
| **Occupancy Rate** | Percentage of rooms with active tenants |
| **Overdue** | Payment that passed due date but not yet paid |
| **Move-in Date** | Date tenant starts living in room |
| **Move-out Date** | Date tenant vacates room |
| **Monthly Rate** | Regular rent amount per month in IDR |

---

## 12. Acceptance Testing Checklist

### Authentication
- [ ] New user can register with valid credentials
- [ ] User cannot register with duplicate username/email
- [ ] User can login with correct credentials
- [ ] User cannot login with incorrect password
- [ ] Session persists after refresh
- [ ] User can logout
- [ ] Logged out user cannot access protected routes

### Room Management
- [ ] User can create room with all fields
- [ ] Room number must be unique
- [ ] User can edit room details
- [ ] User can delete unoccupied room
- [ ] Occupancy grid displays all rooms
- [ ] Room status updates when tenant assigned/removed
- [ ] Occupancy percentage calculates correctly

### Tenant Management
- [ ] User can add new tenant with required fields
- [ ] User can assign tenant to available room
- [ ] Multiple tenants cannot be in same room
- [ ] User can view tenant profile
- [ ] User can edit tenant information
- [ ] Moving tenant out releases room
- [ ] Tenant list searchable and filterable

### Payment Tracking
- [ ] User can record payment for tenant
- [ ] Payment status shows correctly (pending/overdue/paid)
- [ ] Overdue payments calculated correctly
- [ ] User can mark pending payment as paid
- [ ] Payment history shows per tenant
- [ ] Payment list filterable by status, tenant, date

### Income & Expenses
- [ ] User can record expense with category
- [ ] Expenses appear in list and summary
- [ ] Income calculated from paid payments
- [ ] Monthly income/expense summary accurate
- [ ] Financial calculations correct (no rounding errors)

### Dashboard
- [ ] Dashboard loads without errors
- [ ] Key metrics display correctly
- [ ] Occupancy rate accurate
- [ ] Revenue amount correct
- [ ] Expense amount correct
- [ ] Net profit calculated correctly
- [ ] Overdue count accurate
- [ ] Date range filtering works
- [ ] Charts display proper data

### Data & Security
- [ ] Passwords are hashed (cannot see plaintext)
- [ ] Logout clears session
- [ ] Unprivileged user cannot access other data
- [ ] Data persists after refresh
- [ ] Data can be exported to CSV
- [ ] Backup process works

---

## Appendix A: Wireframes & Screenshots

*To be added with UI designs*

---

## Appendix B: API Documentation

*Full API documentation in separate file: `API_DOCS.md`*

---

**Document Approval**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | Claudio | — | — |
| Developer | — | — | — |
| QA Lead | — | — | — |

---

**Change Log**

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-24 | Initial PRD creation |

