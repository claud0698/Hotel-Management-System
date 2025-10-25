# Implementation Tasks Breakdown
## Kos Management Dashboard

**Estimated Total Duration**: 3-4 weeks (working 4 hours/day)
**Tech Stack**: Flask (Backend), React TypeScript (Frontend), SQLite → PostgreSQL

---

## Phase 1: Project Setup & Database (Week 1)

### Task 1.1: Backend Project Structure
**Effort**: 2 hours | **Priority**: P0 | **Complexity**: Low

**Description**: Initialize Flask project with proper structure and dependencies

**Acceptance Criteria**:
- [ ] Flask app initializes and runs on localhost:5000
- [ ] CORS enabled for frontend requests
- [ ] .env file configured with database and JWT secrets
- [ ] requirements.txt has all dependencies
- [ ] Project follows Flask best practices (blueprints, separation of concerns)

**Steps**:
1. Create virtual environment
2. Install dependencies (Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS, python-dotenv)
3. Create app.py with basic Flask setup
4. Create .env for configuration
5. Create basic health check endpoint
6. Test that Flask app starts without errors

**Deliverables**:
- working Flask app
- requirements.txt
- .env template

---

### Task 1.2: Database Models & ORM Setup
**Effort**: 3 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Create SQLAlchemy models for all database tables

**Acceptance Criteria**:
- [ ] All 6 models created (User, Room, Tenant, Payment, Expense, RoomHistory)
- [ ] Relationships properly defined between models
- [ ] All fields have correct types and constraints
- [ ] to_dict() methods return proper JSON serialization
- [ ] Models follow single responsibility principle

**Models to Create**:
1. User (id, username, password_hash, email, created_at)
2. Room (id, room_number, floor, room_type, monthly_rate, status, amenities)
3. Tenant (id, name, phone, email, id_number, move_in_date, move_out_date, current_room_id, status, notes)
4. Payment (id, tenant_id, amount, due_date, paid_date, status, payment_method, receipt_number, notes)
5. Expense (id, date, category, amount, description, receipt_url)
6. RoomHistory (id, room_id, tenant_id, move_in_date, move_out_date)

**Relationships**:
- User ← (many Rooms, Tenants, Payments, Expenses)
- Room ← (many Tenants, RoomHistory)
- Tenant ← (many Payments, RoomHistory)

**Steps**:
1. Create models.py with SQLAlchemy models
2. Define all relationships with proper foreign keys
3. Add constraints (unique room_number, nullable fields, defaults)
4. Create to_dict() methods for JSON serialization
5. Test model creation with test data

**Deliverables**:
- models.py with all ORM definitions
- Database schema documentation

---

### Task 1.3: Database Initialization & Migration
**Effort**: 1.5 hours | **Priority**: P0 | **Complexity**: Low

**Description**: Set up database creation and seed data

**Acceptance Criteria**:
- [ ] Database creates automatically on first app run
- [ ] Seed data can be inserted for testing
- [ ] Database file (kos.db) generated in backend folder
- [ ] Can reset database with one command

**Steps**:
1. Create database initialization in app.py (db.create_all())
2. Create seed.py script with sample data
3. Add CLI commands for seeding/resetting database
4. Test that database is created properly

**Deliverables**:
- seed.py with sample data
- Database setup documentation

---

### Task 1.4: Authentication Routes (Backend)
**Effort**: 2.5 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Implement user registration and login APIs

**Endpoints**:
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me` (protected)

**Acceptance Criteria**:
- [ ] User can register with username, email, password
- [ ] Password is hashed with Werkzeug
- [ ] Duplicate username/email validation
- [ ] User can login and receive JWT token
- [ ] Token valid for 30 days
- [ ] /me endpoint returns current user info
- [ ] Invalid credentials return 401
- [ ] JWT properly validates protected routes

**Request/Response Examples**:

**Register**:
```json
POST /api/auth/register
{
  "username": "claudio",
  "email": "claudio@example.com",
  "password": "secure123"
}

Response 201:
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "username": "claudio",
    "email": "claudio@example.com"
  }
}
```

**Login**:
```json
POST /api/auth/login
{
  "username": "claudio",
  "password": "secure123"
}

Response 200:
{
  "access_token": "eyJ0eXAiOiJKV1...",
  "user": {
    "id": 1,
    "username": "claudio",
    "email": "claudio@example.com"
  }
}
```

**Steps**:
1. Create auth_bp blueprint
2. Implement register endpoint with validation
3. Implement login endpoint with JWT token generation
4. Implement /me endpoint with @jwt_required decorator
5. Add proper error handling
6. Test all endpoints with curl/Postman

**Deliverables**:
- routes.py with auth endpoints
- API documentation for auth
- Test results showing all endpoints working

---

## Phase 2: Room Management (Week 1-2)

### Task 2.1: Room CRUD API Routes
**Effort**: 2 hours | **Priority**: P0 | **Complexity**: Low

**Description**: Implement Room management endpoints

**Endpoints**:
- `GET /api/rooms` - Get all rooms
- `GET /api/rooms/<id>` - Get single room
- `POST /api/rooms` - Create room
- `PUT /api/rooms/<id>` - Update room
- `DELETE /api/rooms/<id>` - Delete room

**Acceptance Criteria**:
- [ ] All CRUD endpoints implemented
- [ ] Room number uniqueness enforced
- [ ] All fields properly validated
- [ ] JWT authentication on all endpoints
- [ ] Proper HTTP status codes (200, 201, 404, 409)
- [ ] Room status defaults to 'available'

**Request Examples**:
```json
POST /api/rooms
{
  "room_number": "101",
  "floor": 1,
  "room_type": "single",
  "monthly_rate": 1500000,
  "amenities": "WiFi, AC, Bathroom"
}
```

**Steps**:
1. Create rooms_bp blueprint
2. Implement GET all rooms
3. Implement GET single room
4. Implement POST with validation
5. Implement PUT with update logic
6. Implement DELETE with safety checks
7. Test all endpoints

**Deliverables**:
- rooms_bp routes in routes.py
- API documentation for rooms

---

### Task 2.2: Room Frontend Components
**Effort**: 4 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Create React components for room management UI

**Components**:
- RoomList.tsx - List all rooms
- RoomCard.tsx - Single room display
- RoomForm.tsx - Create/Edit room form
- RoomModal.tsx - Modal for room details

**Acceptance Criteria**:
- [ ] Rooms list displays all rooms
- [ ] Add room button opens form
- [ ] Form validates inputs
- [ ] Can edit existing room
- [ ] Can delete room with confirmation
- [ ] Form clears after submission
- [ ] Loading states show during requests
- [ ] Error messages display properly
- [ ] Responsive on mobile

**UI Requirements**:
- Room cards show: number, floor, type, rate, status
- Room list has search/filter by status
- Form has all room fields
- Delete confirmation modal
- Success/error toast notifications

**Steps**:
1. Set up React project with Vite
2. Install dependencies (axios, zustand, react-router-dom)
3. Create API client (services/api.ts)
4. Create auth store (stores/authStore.ts)
5. Create room store (stores/roomStore.ts)
6. Create RoomList component
7. Create RoomForm component
8. Create RoomCard component
9. Wire up API calls
10. Test all functionality

**Deliverables**:
- src/components/rooms/ with all components
- src/services/api.ts with API client
- src/stores/ with Zustand stores
- Working room management UI

---

### Task 2.3: Room Occupancy Grid Visualization
**Effort**: 3 hours | **Priority**: P1 | **Complexity**: Medium

**Description**: Create visual grid showing room occupancy status

**Component**:
- RoomOccupancyGrid.tsx

**Acceptance Criteria**:
- [ ] Grid displays all rooms
- [ ] Color-coded by status (green available, blue occupied, yellow maintenance)
- [ ] Room numbers visible
- [ ] Clicking room shows details
- [ ] Occupancy percentage displayed
- [ ] Responsive grid layout (4-6 columns on desktop, 2-3 on mobile)
- [ ] Hover tooltip shows room info

**Features**:
- Click to view room details
- Double-click to edit
- Filter by status
- Zoom/responsive sizing

**Steps**:
1. Create RoomOccupancyGrid component
2. Create RoomGridCell component
3. Add color mapping for status
4. Add occupancy calculation
5. Wire to room store
6. Add click handlers
7. Add responsive styling with Tailwind
8. Test grid layout on different screen sizes

**Deliverables**:
- RoomOccupancyGrid component
- RoomGridCell component
- Responsive styling

---

## Phase 3: Tenant Management (Week 2)

### Task 3.1: Tenant CRUD API Routes
**Effort**: 2.5 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Implement Tenant management endpoints with room assignment logic

**Endpoints**:
- `GET /api/tenants` - Get all tenants
- `GET /api/tenants/<id>` - Get single tenant
- `POST /api/tenants` - Create tenant
- `PUT /api/tenants/<id>` - Update tenant
- `DELETE /api/tenants/<id>` - Delete tenant

**Acceptance Criteria**:
- [ ] All CRUD endpoints implemented
- [ ] Tenant can be assigned to room
- [ ] Cannot assign 2 tenants to same room
- [ ] Moving tenant updates room status
- [ ] Room history tracked
- [ ] Tenant status defaults to 'active'
- [ ] Move-in date required when assigning room
- [ ] Proper cascading when tenant deleted

**Key Logic**:
- When tenant assigned to room: room status → occupied, create RoomHistory
- When tenant unassigned: room status → available, close RoomHistory
- When tenant deleted: room released, room status → available

**Steps**:
1. Create tenants_bp blueprint
2. Implement GET all tenants
3. Implement GET single tenant with room info
4. Implement POST with room assignment logic
5. Implement PUT with room change handling
6. Implement DELETE with room cleanup
7. Handle RoomHistory creation/updates
8. Test all endpoints

**Deliverables**:
- tenants_bp routes in routes.py
- Room assignment logic
- API documentation

---

### Task 3.2: Tenant Frontend Components
**Effort**: 4 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Create React components for tenant management

**Components**:
- TenantList.tsx - List all tenants
- TenantCard.tsx - Tenant summary card
- TenantForm.tsx - Create/Edit tenant form
- TenantProfile.tsx - Detailed tenant view
- RoomAssignmentModal.tsx - Assign tenant to room

**Acceptance Criteria**:
- [ ] Tenant list with search/filter
- [ ] Add tenant opens form
- [ ] Form validates required fields
- [ ] Can assign room when creating/editing
- [ ] Room dropdown only shows available rooms
- [ ] Can change tenant room
- [ ] Can mark tenant as moved out
- [ ] Tenant payment history visible
- [ ] Delete with confirmation
- [ ] Mobile responsive

**UI Features**:
- Tenant list shows: name, room, status, move-in date
- Filter by status (active, inactive, moved out)
- Search by name
- Quick actions (view, edit, delete, assign room)
- Tenant profile shows full info + payment history

**Steps**:
1. Create tenant store (stores/tenantStore.ts)
2. Create TenantList component
3. Create TenantForm component
4. Create TenantCard component
5. Create RoomAssignmentModal
6. Create TenantProfile component
7. Wire API calls
8. Add form validation
9. Test all functionality

**Deliverables**:
- src/components/tenants/ with all components
- src/stores/tenantStore.ts
- Tenant management UI

---

### Task 3.3: Tenant-Room Relationship UI
**Effort**: 2 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Create UI for managing tenant-room assignments

**Component**:
- TenantRoomSelector.tsx

**Features**:
- Show current room assignment
- Dropdown to select available rooms
- Button to change room
- Confirmation for room change
- Shows available rooms only

**Acceptance Criteria**:
- [ ] Only available rooms in dropdown
- [ ] Cannot assign multiple tenants to same room
- [ ] Room status updates when assignment changes
- [ ] Move-out date appears when unassigning
- [ ] Previous room becomes available

**Steps**:
1. Create TenantRoomSelector component
2. Fetch available rooms from API
3. Add select dropdown
4. Add change handler
5. Show confirmation modal
6. Update on backend
7. Refresh room and tenant state

**Deliverables**:
- TenantRoomSelector component
- Room assignment UI logic

---

## Phase 4: Payment Tracking (Week 2-3)

### Task 4.1: Payment CRUD API Routes
**Effort**: 3 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Implement Payment management endpoints

**Endpoints**:
- `GET /api/payments` - Get all payments with filters
- `GET /api/payments/<id>` - Get single payment
- `POST /api/payments` - Create payment
- `PUT /api/payments/<id>` - Update payment
- `POST /api/payments/<id>/mark-paid` - Mark payment as paid
- `DELETE /api/payments/<id>` - Delete payment

**Query Parameters**:
- `tenant_id` - Filter by tenant
- `status` - Filter by status (pending, paid, overdue)

**Acceptance Criteria**:
- [ ] All endpoints implemented
- [ ] Payment status calculated (pending, paid, overdue)
- [ ] Overdue determined by due_date < today and status != paid
- [ ] Mark paid endpoint updates paid_date and status
- [ ] Payment method and receipt number optional
- [ ] Amount cannot be negative
- [ ] Proper validation and error handling

**Request Examples**:
```json
POST /api/payments
{
  "tenant_id": 1,
  "amount": 1500000,
  "due_date": "2025-11-01T00:00:00",
  "payment_method": "transfer",
  "receipt_number": "TRF123"
}

POST /api/payments/1/mark-paid
{
  "payment_method": "transfer",
  "receipt_number": "TRF456"
}
```

**Steps**:
1. Create payments_bp blueprint
2. Implement GET with filtering logic
3. Implement status calculation
4. Implement POST with validation
5. Implement PUT with update logic
6. Implement mark-paid endpoint
7. Implement DELETE
8. Test all endpoints

**Deliverables**:
- payments_bp routes in routes.py
- Payment status logic
- API documentation

---

### Task 4.2: Payment Frontend Components
**Effort**: 4 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Create React components for payment management

**Components**:
- PaymentList.tsx - List all payments
- PaymentCard.tsx - Payment summary
- PaymentForm.tsx - Create/Edit payment
- PaymentHistoryModal.tsx - Tenant payment history
- OverduePaymentsList.tsx - Highlight overdue

**Acceptance Criteria**:
- [ ] Payment list with search/filter
- [ ] Filter by status, tenant, date range
- [ ] Create new payment form
- [ ] Mark payment as paid (quick action)
- [ ] Edit payment details
- [ ] Delete payment with confirmation
- [ ] Overdue payments highlighted in red
- [ ] Payment history per tenant
- [ ] Mobile responsive

**UI Features**:
- Payment list shows: tenant, amount, due date, status
- Color-coded status (green paid, orange overdue, gray pending)
- Filter by status, tenant, date range
- Quick action: "Mark as Paid" button
- "Mark Paid" modal shows payment method and receipt number
- Overdue section shows total overdue amount

**Steps**:
1. Create payment store (stores/paymentStore.ts)
2. Create PaymentList component
3. Create PaymentCard component
4. Create PaymentForm component
5. Create OverduePaymentsList component
6. Create "Mark as Paid" modal
7. Wire API calls
8. Add date range filtering
9. Test functionality

**Deliverables**:
- src/components/payments/ with all components
- src/stores/paymentStore.ts
- Payment management UI

---

### Task 4.3: Auto-Generate Monthly Payments (Backend)
**Effort**: 2.5 hours | **Priority**: P1 | **Complexity**: Medium

**Description**: Create utility to auto-generate monthly payment records

**Features**:
- Auto-create payment for each tenant at start of month
- Due date set to 1st of month (or configurable)
- Amount = room's monthly_rate
- Status = pending

**Acceptance Criteria**:
- [ ] Script runs on app startup or scheduled task
- [ ] Only creates for active tenants
- [ ] Only creates if payment for month doesn't exist
- [ ] Due date correctly calculated
- [ ] Amount matches current room rate
- [ ] No duplicates created

**Implementation Options**:
1. Manual trigger endpoint: `POST /api/payments/generate-monthly`
2. Scheduled task with APScheduler (future)
3. Manual trigger in admin UI

**Steps**:
1. Create payment_utils.py with auto-generate logic
2. Create API endpoint to trigger generation
3. Add checks to prevent duplicates
4. Test payment generation

**Deliverables**:
- payment_utils.py with auto-generation logic
- Manual trigger endpoint

---

### Task 4.4: Payment Status Dashboard Widget
**Effort**: 2 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Create payment summary card for dashboard

**Component**:
- PaymentStatusWidget.tsx

**Shows**:
- Total pending payments count
- Total overdue payments count
- Total overdue amount
- Quick link to overdue list

**Steps**:
1. Create PaymentStatusWidget component
2. Fetch payment counts from API
3. Display counts with visual emphasis on overdue
4. Add link to detailed payment view
5. Auto-refresh every 60 seconds

**Deliverables**:
- PaymentStatusWidget component

---

## Phase 5: Income & Expense Tracking (Week 3)

### Task 5.1: Expense CRUD API Routes
**Effort**: 2 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Implement Expense management endpoints

**Endpoints**:
- `GET /api/expenses` - Get all expenses with filters
- `GET /api/expenses/<id>` - Get single expense
- `POST /api/expenses` - Create expense
- `PUT /api/expenses/<id>` - Update expense
- `DELETE /api/expenses/<id>` - Delete expense

**Query Parameters**:
- `category` - Filter by category
- `start_date` - Filter by date range
- `end_date` - Filter by date range

**Acceptance Criteria**:
- [ ] All CRUD endpoints working
- [ ] Date filtering works correctly
- [ ] Category filtering works
- [ ] Amount cannot be negative
- [ ] Receipt URL optional
- [ ] Proper validation

**Request Example**:
```json
POST /api/expenses
{
  "date": "2025-10-20T00:00:00",
  "category": "maintenance",
  "amount": 500000,
  "description": "Fixed broken AC in room 101",
  "receipt_url": "https://..."
}
```

**Steps**:
1. Create expenses_bp blueprint
2. Implement all CRUD endpoints
3. Add date range filtering
4. Add category filtering
5. Validate amounts
6. Test endpoints

**Deliverables**:
- expenses_bp routes in routes.py
- API documentation

---

### Task 5.2: Expense Frontend Components
**Effort**: 3.5 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Create React components for expense management

**Components**:
- ExpenseList.tsx - List all expenses
- ExpenseCard.tsx - Expense summary
- ExpenseForm.tsx - Create/Edit expense
- ExpenseCategoryBadge.tsx - Category display

**Acceptance Criteria**:
- [ ] List all expenses
- [ ] Filter by category and date range
- [ ] Create new expense
- [ ] Edit existing expense
- [ ] Delete expense
- [ ] Category color-coded
- [ ] Amount formatting (IDR)
- [ ] Mobile responsive

**UI Features**:
- Expense list shows: date, category, amount, description
- Color-coded categories
- Filter dropdowns
- Add expense button
- Edit/delete quick actions

**Steps**:
1. Create expense store
2. Create ExpenseList component
3. Create ExpenseForm component
4. Create ExpenseCard component
5. Add category badges
6. Wire API calls
7. Add filtering
8. Test functionality

**Deliverables**:
- src/components/expenses/ with all components
- Expense management UI

---

### Task 5.3: Financial Summary API Endpoint
**Effort**: 2.5 hours | **Priority**: P1 | **Complexity**: Medium

**Description**: Create backend endpoint for financial calculations

**Endpoint**:
- `GET /api/dashboard/metrics?start_date=...&end_date=...`

**Returns**:
```json
{
  "total_income": 4500000,
  "total_expenses": 800000,
  "net_profit": 3700000,
  "occupancy_rate": 80.0,
  "occupied_rooms": 8,
  "available_rooms": 2,
  "overdue_count": 2,
  "overdue_amount": 3000000,
  "pending_count": 5
}
```

**Acceptance Criteria**:
- [ ] Calculates total income from paid payments only
- [ ] Calculates total expenses in period
- [ ] Calculates net profit (income - expenses)
- [ ] Occupancy rate accurate
- [ ] Overdue count and amount correct
- [ ] Date filtering works
- [ ] Defaults to current month if no dates

**Steps**:
1. Update dashboard_bp
2. Implement metrics endpoint
3. Add income calculation from paid payments
4. Add expense sum
5. Add occupancy calculation
6. Add overdue detection
7. Test calculations with sample data

**Deliverables**:
- dashboard metrics endpoint
- Calculations tested

---

### Task 5.4: Financial Summary Dashboard Cards
**Effort**: 2.5 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Create dashboard cards showing financial metrics

**Components**:
- RevenueCard.tsx - Monthly income
- ExpenseCard.tsx - Monthly expenses
- ProfitCard.tsx - Net profit/loss
- OccupancyCard.tsx - Occupancy rate

**Features**:
- Show current month by default
- Show IDR currency formatting
- Color coding (green positive, red negative)
- Comparison to previous month (future)
- Date range selector

**Steps**:
1. Create dashboard metric components
2. Fetch metrics from API
3. Format currency (IDR)
4. Color code based on values
5. Add date range selector
6. Wire to dashboard page

**Deliverables**:
- Dashboard metric components
- Currency formatting utility

---

## Phase 6: Dashboard & Visualization (Week 3-4)

### Task 6.1: Dashboard Layout & Structure
**Effort**: 2 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Create main dashboard page layout

**Components**:
- Dashboard.tsx - Main page
- DashboardLayout.tsx - Layout structure

**Layout Sections**:
1. Header with user info and logout
2. Sidebar navigation
3. Main content area
4. Metric cards (occupancy, revenue, expenses, profit)
5. Room occupancy grid
6. Payment status summary
7. Recent activity

**Acceptance Criteria**:
- [ ] All sections display
- [ ] Responsive layout
- [ ] Navigation works
- [ ] User menu works
- [ ] Logout works
- [ ] Mobile friendly

**Steps**:
1. Create Dashboard.tsx page
2. Create DashboardLayout component
3. Create navigation sidebar
4. Create header with user menu
5. Layout all metric cards
6. Add room grid
7. Add activity section
8. Style with Tailwind
9. Make responsive

**Deliverables**:
- Dashboard page layout
- Navigation components

---

### Task 6.2: Dashboard Charts & Visualizations
**Effort**: 3.5 hours | **Priority**: P1 | **Complexity**: Medium

**Description**: Add charts to dashboard

**Charts**:
1. Revenue Trend (Line chart - last 6 months)
2. Expense Breakdown (Pie chart - by category)
3. Occupancy Trend (Bar chart - last 3 months)

**Library**: Recharts

**Acceptance Criteria**:
- [ ] Revenue line chart shows monthly trend
- [ ] Expense pie chart shows category breakdown
- [ ] Occupancy bar chart shows trend
- [ ] Charts are interactive (hover for details)
- [ ] Charts responsive on mobile
- [ ] Labels and legends clear

**Steps**:
1. Install Recharts
2. Create RevenueChart component
3. Create ExpenseBreakdownChart component
4. Create OccupancyChart component
5. Fetch data from API
6. Format data for charts
7. Add chart responsiveness
8. Test on mobile

**Deliverables**:
- Chart components with Recharts
- Chart data endpoints
- Responsive chart styling

---

### Task 6.3: Recent Activity Panel
**Effort**: 1.5 hours | **Priority**: P2 | **Complexity**: Low

**Description**: Show recent transactions and activity

**Component**:
- RecentActivityPanel.tsx

**Shows**:
- Last 5 payments recorded
- Last 5 expenses recorded
- Latest tenant additions

**Acceptance Criteria**:
- [ ] Displays recent items
- [ ] Timestamps shown
- [ ] Links to details
- [ ] Auto-refreshes
- [ ] Mobile friendly

**Steps**:
1. Create RecentActivityPanel component
2. Fetch recent data from API
3. Format timestamps
4. Add links to details
5. Auto-refresh every 60 seconds
6. Test display

**Deliverables**:
- RecentActivityPanel component

---

### Task 6.4: Dashboard Date Range Filtering
**Effort**: 2 hours | **Priority**: P2 | **Complexity**: Low

**Description**: Add date filtering to dashboard metrics

**Component**:
- DateRangeSelector.tsx

**Options**:
- Current month (default)
- Last 3 months
- Last 6 months
- Last 12 months
- Custom date range

**Acceptance Criteria**:
- [ ] Selector updates all metrics
- [ ] Charts update with date range
- [ ] Custom date picker works
- [ ] Defaults to current month

**Steps**:
1. Create DateRangeSelector component
2. Add date input fields
3. Wire to metric API calls
4. Update all charts and cards
5. Add preset buttons

**Deliverables**:
- DateRangeSelector component

---

## Phase 7: Frontend Setup & Integration (Week 1-2)

### Task 7.1: React Project Setup with Vite
**Effort**: 2 hours | **Priority**: P0 | **Complexity**: Low

**Description**: Initialize React TypeScript project with all dependencies

**Acceptance Criteria**:
- [ ] Vite React TypeScript project created
- [ ] All dependencies installed
- [ ] Tailwind CSS configured
- [ ] React Router configured
- [ ] Axios client set up
- [ ] Zustand store configured
- [ ] Project runs without errors
- [ ] Build process works

**Dependencies**:
- react, react-dom
- react-router-dom
- axios
- zustand
- recharts
- tailwindcss, postcss, autoprefixer
- typescript
- vite

**Steps**:
1. Create Vite React TS project
2. Install all dependencies
3. Configure Tailwind CSS
4. Configure React Router
5. Create folder structure (components, pages, services, stores)
6. Create API client (services/api.ts)
7. Test that app runs

**Deliverables**:
- Working React app
- Proper folder structure
- Configured tooling

---

### Task 7.2: API Client & Axios Setup
**Effort**: 1 hour | **Priority**: P0 | **Complexity**: Low

**Description**: Create axios client for backend API calls

**File**: `src/services/api.ts`

**Features**:
- Centralized API calls
- Automatic JWT token in headers
- Error handling
- Request/response interceptors
- Base URL from environment

**Acceptance Criteria**:
- [ ] API client exports typed functions
- [ ] JWT token automatically added to requests
- [ ] Errors handled properly
- [ ] Works with all endpoints

**Steps**:
1. Create api.ts with axios instance
2. Add JWT token interceptor
3. Add error handling
4. Create typed API functions
5. Export all functions

**Deliverables**:
- src/services/api.ts with all API functions

---

### Task 7.3: Authentication Store & Context
**Effort**: 2 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Create Zustand store for auth state

**File**: `src/stores/authStore.ts`

**Store State**:
- user (User | null)
- token (string | null)
- isLoading (boolean)
- error (string | null)

**Store Actions**:
- register(username, email, password)
- login(username, password)
- logout()
- getCurrentUser()
- setToken(token)
- clearError()

**Acceptance Criteria**:
- [ ] Store persists token to localStorage
- [ ] Token read from localStorage on app load
- [ ] Login/register set user and token
- [ ] Logout clears user and token
- [ ] Error states managed
- [ ] Loading states managed

**Steps**:
1. Create authStore.ts with Zustand
2. Add state properties
3. Add actions
4. Add localStorage persistence
5. Export hook for components
6. Test store

**Deliverables**:
- src/stores/authStore.ts
- useAuth hook for components

---

### Task 7.4: Login Page
**Effort**: 2 hours | **Priority**: P0 | **Complexity**: Low

**Description**: Create login and register pages

**Components**:
- LoginPage.tsx
- RegisterPage.tsx
- AuthForm.tsx (reusable)

**Features**:
- Email/username input
- Password input
- Remember me checkbox (future)
- Error messages
- Loading state
- Links to register/login

**Acceptance Criteria**:
- [ ] Form validation (email format, password length)
- [ ] Submit button disabled while loading
- [ ] Error messages show on failure
- [ ] Success redirects to dashboard
- [ ] Register and login both work
- [ ] Mobile responsive
- [ ] Accessible (labels, keyboard nav)

**Steps**:
1. Create LoginPage.tsx
2. Create RegisterPage.tsx
3. Create form component
4. Add validation
5. Add API calls
6. Add error handling
7. Add redirect logic
8. Style with Tailwind
9. Test login/register flow

**Deliverables**:
- src/pages/LoginPage.tsx
- src/pages/RegisterPage.tsx
- Auth pages styled and working

---

### Task 7.5: Navigation & Routing
**Effort**: 2 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Set up React Router with all routes

**File**: `src/App.tsx`

**Routes**:
- `/` → Dashboard (protected)
- `/login` → Login page
- `/register` → Register page
- `/rooms` → Room management (protected)
- `/tenants` → Tenant management (protected)
- `/payments` → Payment management (protected)
- `/expenses` → Expense management (protected)
- `*` → 404 page

**Protected Route Wrapper**:
- Redirects to login if not authenticated
- Checks token validity

**Acceptance Criteria**:
- [ ] All routes work
- [ ] Protected routes redirect to login
- [ ] Navigation works
- [ ] URLs update correctly
- [ ] Back button works
- [ ] Page refreshes maintain auth

**Steps**:
1. Create App.tsx with BrowserRouter
2. Create routes array
3. Create ProtectedRoute wrapper
4. Create 404 NotFound page
5. Create MainLayout component
6. Create Sidebar navigation
7. Add logout function to nav
8. Test all routes

**Deliverables**:
- src/App.tsx with all routes
- src/components/ProtectedRoute.tsx
- Navigation components

---

### Task 7.6: Tailwind CSS & Styling Setup
**Effort**: 2 hours | **Priority**: P0 | **Complexity**: Low

**Description**: Configure Tailwind CSS and create design system

**Files**:
- `tailwind.config.js`
- `postcss.config.js`
- `src/index.css`
- `src/styles/` folder with theme utilities

**Features**:
- Color palette (brand colors, status colors)
- Typography (headings, body, small text)
- Spacing constants
- Responsive breakpoints

**Acceptance Criteria**:
- [ ] Tailwind properly configured
- [ ] All pages styled consistently
- [ ] Dark mode compatible (future)
- [ ] Mobile responsive
- [ ] Accessible contrast ratios

**Steps**:
1. Initialize Tailwind in project
2. Create tailwind.config.js with custom colors
3. Create postcss.config.js
4. Create index.css with Tailwind imports
5. Create color/spacing utilities
6. Create component-level CSS as needed
7. Test responsive design

**Deliverables**:
- Tailwind configured
- Design tokens defined
- Styling applied to all pages

---

## Phase 8: Integration & Testing (Week 4)

### Task 8.1: Backend Testing
**Effort**: 3 hours | **Priority**: P2 | **Complexity**: Medium

**Description**: Write tests for backend API endpoints

**Framework**: pytest

**Test Coverage**:
- Auth endpoints (register, login, me)
- Room CRUD endpoints
- Tenant CRUD endpoints
- Payment CRUD endpoints
- Expense CRUD endpoints
- Dashboard metrics

**Acceptance Criteria**:
- [ ] All critical endpoints have tests
- [ ] Tests cover success and failure cases
- [ ] Tests validate response formats
- [ ] Tests verify status codes
- [ ] 80%+ code coverage

**Steps**:
1. Install pytest and pytest-flask
2. Create test file structure
3. Write fixtures for test data
4. Write tests for auth
5. Write tests for each resource
6. Test error cases
7. Run tests and achieve coverage

**Deliverables**:
- tests/ folder with test files
- Test report showing coverage

---

### Task 8.2: Frontend Integration Testing
**Effort**: 3 hours | **Priority**: P2 | **Complexity**: Medium

**Description**: Test frontend components and flows

**Testing Approach**:
- Component rendering tests
- User interaction tests
- API integration tests
- Form validation tests

**Tools**: Vitest, React Testing Library

**Test Coverage**:
- Login flow
- Room CRUD
- Tenant CRUD
- Payment recording
- Dashboard metrics

**Acceptance Criteria**:
- [ ] Key user flows tested
- [ ] Components render correctly
- [ ] Forms validate
- [ ] API calls work
- [ ] Error handling works

**Steps**:
1. Install testing libraries
2. Create test setup files
3. Write component tests
4. Write integration tests
5. Test user flows
6. Mock API calls
7. Run tests

**Deliverables**:
- src/__tests__/ with test files
- Test report

---

### Task 8.3: End-to-End Testing
**Effort**: 2 hours | **Priority**: P2 | **Complexity**: Medium

**Description**: Test complete user workflows

**Scenarios to Test**:
1. Register → Login → Create Room → Create Tenant → Record Payment → View Dashboard
2. Create multiple rooms → Check occupancy grid
3. Record expenses → View financial summary
4. Search and filter tenants
5. Mark payment as paid
6. Export data

**Tools**: Manual testing + Playwright (future)

**Acceptance Criteria**:
- [ ] All main workflows complete successfully
- [ ] No errors in console
- [ ] Data persists correctly
- [ ] All features accessible
- [ ] Mobile responsive works

**Steps**:
1. Document test cases
2. Create test data set
3. Run through each workflow
4. Verify all outputs
5. Test on mobile
6. Document any issues found

**Deliverables**:
- Test case documentation
- Test results report

---

### Task 8.4: Bug Fixes & Polish
**Effort**: 3 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Fix any bugs found during testing

**Process**:
1. List all bugs found
2. Prioritize by severity
3. Fix each bug
4. Re-test fix
5. Verify no regressions

**Common Bug Areas**:
- Form validation edge cases
- Date formatting issues
- Number formatting (currency)
- Responsive layout issues
- Loading states not showing
- Error messages not displaying

**Acceptance Criteria**:
- [ ] All critical bugs fixed
- [ ] No console errors
- [ ] All features work smoothly
- [ ] No broken links

---

## Phase 9: Deployment & Documentation (Week 4)

### Task 9.1: Backend Deployment Setup
**Effort**: 2 hours | **Priority**: P1 | **Complexity**: Medium

**Description**: Prepare backend for production

**Steps**:
1. Switch database to PostgreSQL
2. Update environment variables
3. Set up error logging
4. Configure CORS for production
5. Add rate limiting
6. Create production .env file
7. Test production build locally

**Deployment Options**:
- Heroku
- Railway
- PythonAnywhere
- Self-hosted VPS

**Acceptance Criteria**:
- [ ] Backend runs on production server
- [ ] Database connected
- [ ] Environment variables secure
- [ ] CORS configured
- [ ] Errors logged properly

**Deliverables**:
- Production config files
- Deployment guide

---

### Task 9.2: Frontend Deployment Setup
**Effort**: 1.5 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Build and deploy frontend

**Steps**:
1. Run npm build
2. Configure API endpoint for production
3. Test build locally
4. Deploy to hosting

**Deployment Options**:
- Vercel (recommended for Vite)
- Netlify
- GitHub Pages (if static)

**Acceptance Criteria**:
- [ ] Build completes without errors
- [ ] Frontend loads in browser
- [ ] API calls work with production backend
- [ ] Performance acceptable
- [ ] Mobile responsive

**Deliverables**:
- Production build
- Deployment URL

---

### Task 9.3: Backend API Documentation
**Effort**: 2 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Create comprehensive API documentation

**File**: `API_DOCS.md`

**Contents**:
- Base URL
- Authentication (JWT token header format)
- All endpoints with:
  - Method and path
  - Description
  - Request parameters/body
  - Response format (with examples)
  - Error codes
  - curl examples

**Endpoints to Document**:
- Auth (register, login, me)
- Rooms (all CRUD)
- Tenants (all CRUD)
- Payments (all CRUD + mark-paid)
- Expenses (all CRUD)
- Dashboard (metrics, summary)

**Acceptance Criteria**:
- [ ] All endpoints documented
- [ ] Examples are accurate
- [ ] Error codes explained
- [ ] Easy to follow

**Steps**:
1. Create API_DOCS.md
2. Document each endpoint
3. Add examples
4. Add authentication info
5. Add error codes
6. Add curl examples

**Deliverables**:
- API_DOCS.md with complete documentation

---

### Task 9.4: User Documentation & Guide
**Effort**: 2.5 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Create user guide and documentation

**File**: `USER_GUIDE.md`

**Contents**:
1. Getting Started
   - Creating account
   - First login
2. Room Management
   - Adding rooms
   - Editing rooms
   - Understanding room status
3. Tenant Management
   - Adding tenants
   - Assigning to rooms
   - Changing room assignments
   - Removing tenants
4. Payment Tracking
   - Understanding payment statuses
   - Recording payments
   - Viewing payment history
   - Identifying overdue payments
5. Expenses
   - Recording expenses
   - Categorizing expenses
6. Dashboard & Reports
   - Understanding metrics
   - Viewing financial summary
   - Date range filtering
7. Tips & Troubleshooting
   - Common issues
   - FAQ

**Acceptance Criteria**:
- [ ] Step-by-step instructions
- [ ] Screenshots/diagrams helpful
- [ ] Covers all features
- [ ] Easy to understand
- [ ] Searchable

**Steps**:
1. Outline documentation structure
2. Write each section
3. Add screenshots (optional)
4. Add example data
5. Include tips and best practices

**Deliverables**:
- USER_GUIDE.md
- Screenshots of key features (optional)

---

### Task 9.5: Setup & Deployment Guide
**Effort**: 1.5 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Document how to set up and deploy the project

**File**: `SETUP.md` and `DEPLOYMENT.md`

**Contents**:

**SETUP.md**:
- Prerequisites (Python, Node.js, etc.)
- Backend setup steps
- Frontend setup steps
- Database initialization
- Running locally

**DEPLOYMENT.md**:
- Production database setup
- Environment variables
- Backend deployment steps
- Frontend deployment steps
- Domain/SSL setup
- Monitoring and logs
- Backup procedures

**Acceptance Criteria**:
- [ ] Clear step-by-step instructions
- [ ] Easy to follow
- [ ] Troubleshooting section
- [ ] Tested deployment process

**Deliverables**:
- SETUP.md for local development
- DEPLOYMENT.md for production

---

### Task 9.6: README & Project Overview
**Effort**: 1 hour | **Priority**: P1 | **Complexity**: Low

**Description**: Update main README.md with project overview

**Contents**:
- Project description
- Features
- Tech stack
- Quick start
- Directory structure
- Documentation links
- Contributing guidelines (future)
- License

**Acceptance Criteria**:
- [ ] Clear project overview
- [ ] Easy to understand
- [ ] All links work
- [ ] Looks professional

**Deliverables**:
- Updated README.md

---

## Task Dependencies & Timeline

```
Week 1:
├── Phase 1: Backend Setup & Database
│   ├── 1.1 Backend Project (2h)
│   ├── 1.2 Database Models (3h)
│   ├── 1.3 Database Init (1.5h)
│   ├── 1.4 Auth Routes (2.5h)
│   └── 2.1 Room API (2h)
├── Phase 7: Frontend Setup
│   ├── 7.1 Vite Setup (2h)
│   ├── 7.2 API Client (1h)
│   └── 7.3 Auth Store (2h)

Week 2:
├── 2.2 Room UI (4h)
├── 2.3 Room Grid (3h)
├── 3.1 Tenant API (2.5h)
├── 3.2 Tenant UI (4h)
├── 3.3 Room Assignment (2h)
├── 7.4 Login Page (2h)
└── 7.5 Routing (2h)

Week 3:
├── 4.1 Payment API (3h)
├── 4.2 Payment UI (4h)
├── 4.3 Auto-Gen Payments (2.5h)
├── 5.1 Expense API (2h)
├── 5.2 Expense UI (3.5h)
├── 5.3 Financial Summary API (2.5h)
├── 6.1 Dashboard Layout (2h)
├── 6.2 Charts (3.5h)
└── 7.6 Tailwind Setup (2h)

Week 4:
├── 6.3 Recent Activity (1.5h)
├── 6.4 Date Filtering (2h)
├── 8.1 Backend Tests (3h)
├── 8.2 Frontend Tests (3h)
├── 8.3 E2E Testing (2h)
├── 8.4 Bug Fixes (3h)
├── 9.1 Backend Deploy (2h)
├── 9.2 Frontend Deploy (1.5h)
├── 9.3 API Docs (2h)
├── 9.4 User Guide (2.5h)
├── 9.5 Setup Guide (1.5h)
└── 9.6 README (1h)

Total: ~120 hours
```

---

## Effort Estimates by Phase

| Phase | Tasks | Hours | Days (4h/day) |
|-------|-------|-------|--------------|
| 1: Project Setup | 4 | 9.5 | 2.4 |
| 2: Room Management | 3 | 9 | 2.3 |
| 3: Tenant Management | 3 | 8.5 | 2.1 |
| 4: Payment Tracking | 4 | 11.5 | 2.9 |
| 5: Income & Expenses | 4 | 8.5 | 2.1 |
| 6: Dashboard | 4 | 9 | 2.3 |
| 7: Frontend Setup | 6 | 12 | 3 |
| 8: Testing | 4 | 11 | 2.8 |
| 9: Deployment & Docs | 6 | 14 | 3.5 |
| **TOTAL** | **38** | **~120** | **~25 days** |

---

## Phase 10: Dashboard Report Export (Future Development - Phase 2)

**Estimated Effort**: 12-15 hours | **Priority**: High | **Timeline**: Post v1.0 Launch

### Overview
This phase adds comprehensive report export functionality to the dashboard, allowing users to export financial data and reports in multiple formats for custom time periods (monthly, quarterly, yearly, or custom date ranges).

---

### Task 10.1: Report Generation API Endpoint
**Effort**: 3 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Create backend endpoint for generating financial reports

**Endpoint**:
- `GET /api/reports/financial`

**Query Parameters**:
```
?start_date=2025-01-01&end_date=2025-12-31&include_sections=income,expenses,occupancy,payments
```

**Response**:
```json
{
  "report": {
    "period": "2025-01-01 to 2025-12-31",
    "generated_date": "2025-10-24T10:30:00",
    "sections": {
      "income": {
        "total_paid_rent": 18000000,
        "payment_count": 12,
        "collection_rate": 95.5,
        "monthly_breakdown": [...]
      },
      "expenses": {
        "total_expenses": 2400000,
        "by_category": {
          "maintenance": 800000,
          "utilities": 900000,
          "supplies": 300000,
          "cleaning": 400000
        },
        "monthly_breakdown": [...]
      },
      "occupancy": {
        "average_occupancy_rate": 82.5,
        "total_rooms": 10,
        "occupied_rooms": 8.25,
        "vacancy_cost": 150000,
        "occupancy_trend": [...]
      },
      "payments": {
        "total_rent_due": 18000000,
        "total_paid": 17100000,
        "overdue_amount": 600000,
        "pending_amount": 300000,
        "payment_status_breakdown": {...}
      },
      "financial_summary": {
        "gross_income": 18000000,
        "total_expenses": 2400000,
        "net_profit": 15600000,
        "profit_margin": 86.7
      }
    }
  }
}
```

**Acceptance Criteria**:
- [ ] Returns accurate financial data for date range
- [ ] Can include/exclude sections dynamically
- [ ] Calculates collection rate correctly
- [ ] Monthly breakdowns included
- [ ] Handles edge cases (no data, partial periods)
- [ ] Performance good even with large datasets

**Steps**:
1. Create report_utils.py with calculation functions
2. Create /api/reports/financial endpoint
3. Implement date range validation
4. Implement section filtering
5. Add monthly breakdown calculations
6. Test with various date ranges
7. Optimize for performance

**Deliverables**:
- report_utils.py with report generation logic
- /api/reports/financial endpoint
- Report calculations verified

---

### Task 10.2: PDF Export Functionality (Backend)
**Effort**: 3 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Generate formatted PDF reports

**Library**: ReportLab or PyPDF2

**Features**:
- Professional formatted PDF
- Company/property header (customizable)
- Report period prominently displayed
- Tables for detailed data
- Charts embedded (income trend, expense breakdown)
- Footer with generated date and page numbers
- Multiple pages if needed
- IDR currency formatting

**Report Sections in PDF**:
1. Cover page (property name, period, generated date)
2. Executive Summary (key metrics)
3. Income Report (monthly breakdown, collection rate)
4. Expense Report (category breakdown, monthly details)
5. Occupancy Report (occupancy rates, trends)
6. Payment Details (status breakdown, overdue list)
7. Financial Summary (net profit/loss)

**Acceptance Criteria**:
- [ ] PDF generates without errors
- [ ] Layout professional and readable
- [ ] All sections included
- [ ] Currency formatting correct
- [ ] File size reasonable
- [ ] Can be opened in any PDF reader

**Endpoint**:
- `GET /api/reports/export/pdf?start_date=...&end_date=...`

**Steps**:
1. Install ReportLab or similar
2. Create PDF generation function
3. Design report layout
4. Add tables for data
5. Embed charts (convert Recharts data to images or SVG)
6. Test PDF generation
7. Verify formatting on multiple devices

**Deliverables**:
- PDF export functionality
- PDF generation tested
- API endpoint returning PDF file

---

### Task 10.3: Excel Export Functionality (Backend)
**Effort**: 2.5 hours | **Priority**: P0 | **Complexity**: Low

**Description**: Export detailed data to Excel format

**Library**: openpyxl or xlsxwriter

**Excel Sheets**:
1. **Summary** - Key metrics, totals, percentages
2. **Income** - Detailed payment records (date, tenant, amount, status)
3. **Expenses** - Detailed expense records (date, category, amount, description)
4. **Occupancy** - Room occupancy details (room, tenant, dates)
5. **Monthly Breakdown** - Monthly summaries (revenue, expenses, net profit)
6. **Payments Status** - Payment status overview

**Features**:
- Professional formatting (colors, bold headers)
- Column widths auto-adjusted
- Formulas for totals (SUM, AVERAGE)
- Number formatting (IDR currency)
- Filters enabled on headers
- Chart in Excel (optional)
- Report title and date in header

**Acceptance Criteria**:
- [ ] Excel file opens correctly
- [ ] All data accurate
- [ ] Formatting professional
- [ ] Formulas work
- [ ] File size reasonable
- [ ] Currency formatting correct

**Endpoint**:
- `GET /api/reports/export/excel?start_date=...&end_date=...`

**Steps**:
1. Install openpyxl
2. Create Excel generation function
3. Create summary sheet
4. Create detailed data sheets
5. Add formatting
6. Add formulas for calculations
7. Test Excel file

**Deliverables**:
- Excel export functionality
- API endpoint returning Excel file

---

### Task 10.4: CSV Export Functionality (Backend)
**Effort**: 1.5 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Export raw data to CSV format

**CSV Files** (can be separate files or one file with sections):
- Payments CSV (id, tenant_name, amount, due_date, paid_date, status)
- Expenses CSV (date, category, amount, description)
- Tenants CSV (name, room_number, phone, email, move_in_date)
- Rooms CSV (room_number, floor, type, monthly_rate, status)

**Features**:
- Headers included
- Proper encoding (UTF-8 for Indonesian names)
- Date format: YYYY-MM-DD
- Currency as numbers (not formatted)
- Easy to import to other tools

**Acceptance Criteria**:
- [ ] CSV opens in Excel/Sheets
- [ ] Data accurate
- [ ] Proper encoding
- [ ] Can import to accounting software

**Endpoint**:
- `GET /api/reports/export/csv?type=payments&start_date=...&end_date=...`

**Steps**:
1. Create CSV generation function
2. Generate multiple CSV files
3. Zip files together
4. Return as downloadable
5. Test with Excel and Google Sheets

**Deliverables**:
- CSV export functionality
- API endpoint returning CSV files

---

### Task 10.5: Report Export Frontend Component
**Effort**: 3 hours | **Priority**: P0 | **Complexity**: Medium

**Description**: Create UI for generating and exporting reports

**Component**: `ExportReportModal.tsx`

**Features**:
- Report type selector (Financial Summary, Detailed Report, Quick Report)
- Date range selector (Month, Quarter, Year, Custom)
- Sections selector (checkboxes for Income, Expenses, Occupancy, Payments)
- Format selector (PDF, Excel, CSV)
- Preview button (show report in modal)
- Export button (download file)
- Progress indicator while generating

**UI Flow**:
1. User clicks "Export Report" button on dashboard
2. Modal opens with options
3. User selects period, format, sections
4. User clicks "Generate"
5. Loading indicator shows
6. When ready, download starts automatically
7. Toast notification "Report downloaded"

**Report Types**:
- **Financial Summary**: Key metrics only (quick overview)
- **Detailed Report**: Full data with all sections (PDF, Excel)
- **Data Export**: Raw data only (CSV)

**Date Range Presets**:
- This Month
- Last Month
- Last 3 Months
- Last 6 Months
- Last 12 Months (Yearly)
- Custom (date picker)

**Acceptance Criteria**:
- [ ] Modal displays all options
- [ ] Date picker works
- [ ] Format selector works
- [ ] Section selector works
- [ ] Report generates correctly
- [ ] Download starts automatically
- [ ] File naming includes date/period
- [ ] Error handling for failed exports
- [ ] Mobile responsive

**Steps**:
1. Create ExportReportModal component
2. Create DateRangePresets component
3. Create SectionSelector component
4. Create FormatSelector component
5. Add API call to fetch report
6. Add download handler
7. Add loading and error states
8. Test all formats and options

**Deliverables**:
- ExportReportModal component
- Report export UI functional

---

### Task 10.6: Report Preview Component
**Effort**: 2 hours | **Priority**: P1 | **Complexity**: Low

**Description**: Show report preview before download

**Component**: `ReportPreview.tsx`

**Features**:
- Display report data in modal
- Show all metrics and calculations
- Scrollable content
- Print option
- Copy data option
- Close to go back to export options

**Acceptance Criteria**:
- [ ] All report data displays
- [ ] Readable formatting
- [ ] Print works correctly
- [ ] Mobile scrollable

**Steps**:
1. Create ReportPreview component
2. Format report data for display
3. Add print styling
4. Add copy functionality
5. Test display on mobile

**Deliverables**:
- ReportPreview component

---

### Task 10.7: Report Scheduling (Backend) - Optional
**Effort**: 3 hours | **Priority**: P2 | **Complexity**: Medium

**Description**: Auto-generate and email reports on schedule

**Features**:
- User can set report generation schedule
- Options: Monthly (on specific date), Quarterly, Yearly
- Report automatically emailed to user
- User can select sections and format in preferences

**Database Addition**:
```
ReportSchedules
├── id, user_id, report_type, frequency
├── day_of_month, email_address, enabled
├── sections_included, format_preference
└── last_generated_at, next_scheduled_at
```

**Acceptance Criteria**:
- [ ] Schedule saved to database
- [ ] Report generates at scheduled time
- [ ] Email sent with report attachment
- [ ] User can enable/disable schedule
- [ ] User can modify schedule

**Steps**:
1. Create ReportSchedule model
2. Create APScheduler integration
3. Create email sending function
4. Create API endpoints for schedule management
5. Create frontend UI for scheduling
6. Test scheduling

**Deliverables**:
- Report scheduling backend
- Frontend UI for scheduling

---

### Task 10.8: Report Customization UI (Frontend)
**Effort**: 2 hours | **Priority**: P2 | **Complexity**: Low

**Description**: Allow user to customize report appearance

**Features**:
- Add property logo/header
- Custom report title
- Include/exclude logo
- Select color theme
- Add custom footer text
- Choose which metrics to show

**Acceptance Criteria**:
- [ ] Settings saved to user preferences
- [ ] Applied to all exported reports
- [ ] PDF reflects customization

**Steps**:
1. Create report settings form
2. Store in database
3. Apply to PDF generation
4. Test customization

**Deliverables**:
- Report customization UI
- Settings storage and application

---

### Task 10.9: Export History & Management (Backend)
**Effort**: 2 hours | **Priority**: P2 | **Complexity**: Low

**Description**: Track generated reports and allow re-download

**Database Addition**:
```
ExportHistory
├── id, user_id, report_type, date_range
├── format, generated_at, file_path, file_size
└── file_name, download_count
```

**Features**:
- Automatically save generated reports
- List of previous exports
- Re-download without regenerating
- Delete old exports
- Search by date range
- Filter by format

**Acceptance Criteria**:
- [ ] Reports saved on server
- [ ] Can re-download
- [ ] Can list previous exports
- [ ] Can delete old files

**Steps**:
1. Create ExportHistory model
2. Save reports to disk/cloud storage
3. Create API for export history
4. Create history list UI
5. Test save and re-download

**Deliverables**:
- Export history tracking
- Re-download functionality

---

### Task 10.10: Report Email Delivery
**Effort**: 2 hours | **Priority**: P2 | **Complexity**: Medium

**Description**: Email reports to user

**Features**:
- Attach report to email
- Professional email template
- Include report summary in email body
- Link to view in browser (optional)
- Notification that report is ready

**Email Template**:
```
Subject: Your Kos Management Report - [Period]

Body:
Dear [User Name],

Your financial report for [Period] has been generated.

Summary:
- Total Income: IDR [Amount]
- Total Expenses: IDR [Amount]
- Net Profit: IDR [Amount]
- Occupancy Rate: [%]

See attached file for complete report.

Best regards,
Kos Management System
```

**Acceptance Criteria**:
- [ ] Email sends successfully
- [ ] Attachment includes
- [ ] No errors in email
- [ ] HTML formatting works

**Steps**:
1. Set up email service (SendGrid, AWS SES, etc.)
2. Create email template
3. Create send email function
4. Test email delivery
5. Add to scheduled reports

**Deliverables**:
- Email delivery functionality
- Email template

---

## Phase 10 Summary

| Task | Hours | Priority |
|------|-------|----------|
| 10.1 Report Generation API | 3 | P0 |
| 10.2 PDF Export | 3 | P0 |
| 10.3 Excel Export | 2.5 | P0 |
| 10.4 CSV Export | 1.5 | P1 |
| 10.5 Export UI | 3 | P0 |
| 10.6 Preview Component | 2 | P1 |
| 10.7 Report Scheduling | 3 | P2 |
| 10.8 Customization UI | 2 | P2 |
| 10.9 Export History | 2 | P2 |
| 10.10 Email Delivery | 2 | P2 |
| **Total** | **~24.5** | **~6 days** |

**Implementation Order**:
1. Start with API endpoints (10.1, 10.2, 10.3, 10.4)
2. Then frontend components (10.5, 10.6)
3. Then advanced features (10.7, 10.8, 10.9, 10.10)

**Recommended Timing**: Start after v1.0 launch is stable

---

## Quality Checklist

Before marking any task as "COMPLETE", verify:

- [ ] Code is written and tested
- [ ] No console errors or warnings
- [ ] All acceptance criteria met
- [ ] Code follows project conventions
- [ ] Responsive design verified
- [ ] Error handling included
- [ ] Documentation updated
- [ ] Related tests written
- [ ] No breaking changes to other features
- [ ] Works on both desktop and mobile

---

## Next Steps

1. **Approve this breakdown** - Review and confirm task scope
2. **Start Task 1.1** - Begin backend project structure
3. **Follow the dependency order** - Each task depends on previous
4. **Test as you go** - Don't wait until end to test
5. **Update as needed** - Adjust if requirements change

---

**Document Version**: 1.0
**Last Updated**: October 24, 2025
**Status**: Ready for Implementation

