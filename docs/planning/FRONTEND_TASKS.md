# Frontend Development Tasks - Hotel Management System MVP v1.0

**Version**: 1.0
**Last Updated**: November 7, 2025
**Estimated Timeline**: 5-6 weeks (frontend only)

---

## Current State Analysis

### ✅ What We Already Have (Reusable)

**Infrastructure** (100% reusable):
- ✅ React 19 + TypeScript setup
- ✅ Vite build configuration
- ✅ Tailwind CSS setup
- ✅ React Router v7 routing
- ✅ Protected route component
- ✅ i18n setup (English + Indonesian)

**Components** (90% reusable):
- ✅ Layout component (Navbar + Sidebar wrapper)
- ✅ Navbar component (user display, language switcher, logout)
- ✅ Sidebar component (navigation menu)
- ✅ LoginPage component

**State Management** (70% reusable):
- ✅ Zustand setup
- ✅ authStore - **Keep and enhance with role support**
- ✅ languageStore - **Keep as-is**
- ❌ roomStore - **Modify (add room types)**
- ❌ tenantStore - **Replace with guestStore**
- ❌ dashboardStore - **Modify for hotel metrics**

**API Client** (60% reusable):
- ✅ Base API client structure
- ✅ Token management
- ✅ Error handling with 401 auto-logout
- ❌ API types - **Update for hotel models**
- ❌ API endpoints - **Replace tenant/expense with hotel endpoints**

**Pages** (30% reusable):
- ✅ LoginPage - **Keep as-is**
- ✅ DashboardPage - **Modify for hotel metrics**
- ✅ RoomsPage - **Modify for hotel rooms**
- ❌ RoomDetailPage - **Remove or redesign**
- ❌ TenantsPage - **Replace with GuestsPage**
- ❌ PaymentsPage - **Redesign for reservations**
- ❌ ExpensesPage - **Remove (out of scope)**
- ✅ UsersPage - **Keep and enhance with role management**

---

## Dependencies

### Current Dependencies (Keep):
```json
{
  "react": "^19.1.1",
  "react-dom": "^19.1.1",
  "react-router-dom": "^7.0.0",
  "react-i18next": "^16.2.0",
  "i18next": "^25.6.0",
  "zustand": "^4.5.5",
  "tailwindcss": "^3.4.1"
}
```

### New Dependencies Needed:
```json
{
  "axios": "^1.6.0",              // HTTP client (add)
  "date-fns": "^3.0.0",           // Date formatting
  "react-icons": "^5.0.0",        // Icon library
  "react-hook-form": "^7.50.0"    // Form management (optional)
}
```

---

## Task Breakdown by Phase

---

## **PHASE 1: Foundation & Types (Week 1)**

### Task F1.1: Update API Types for Hotel Models
**Estimated Time**: 3 hours
**Priority**: High
**Dependencies**: Backend Task 1.1

**Description**: Update TypeScript interfaces in api.ts for hotel models

**Changes Needed**:
1. Update `User` type - add role, full_name, status
2. Update `Room` type - add room_type_id, view_type, remove monthly_rate
3. Create `RoomType` interface (new)
4. Create `Guest` interface (replaces Tenant)
5. Create `Reservation` interface (new)
6. Update `Payment` interface (simplified)
7. Remove `Tenant`, `Expense` interfaces
8. Update `DashboardMetrics` interface

**New Interfaces**:
```typescript
export interface User {
  id: number;
  username: string;
  email?: string;
  full_name?: string;
  role: 'admin' | 'user';
  status: 'active' | 'inactive';
  created_at: string;
}

export interface RoomType {
  id: number;
  name: string;
  code: string;
  base_capacity_adults: number;
  base_capacity_children: number;
  bed_config: string;
  default_rate: number;
  amenities?: string;
  created_at: string;
  updated_at: string;
}

export interface Guest {
  id: number;
  full_name: string;
  email?: string;
  phone?: string;
  id_type?: string;
  id_number?: string;
  nationality?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Reservation {
  id: number;
  confirmation_number: string;
  guest_id: number;
  guest?: Guest;  // populated
  check_in_date: string;
  check_out_date: string;
  room_type_id: number;
  room_type?: RoomType;  // populated
  room_id?: number;
  room?: Room;  // populated
  adults: number;
  children: number;
  rate_per_night: number;
  total_amount: number;
  special_requests?: string;
  status: 'confirmed' | 'checked_in' | 'checked_out' | 'cancelled';
  booking_source?: string;
  checked_in_at?: string;
  checked_out_at?: string;
  created_at: string;
  updated_at: string;
}
```

**Acceptance Criteria**:
- [ ] All types match backend models
- [ ] No TypeScript errors
- [ ] Old types removed (Tenant, Expense)

**Files to Modify**:
- `frontend/src/services/api.ts`

---

### Task F1.2: Update API Client Endpoints
**Estimated Time**: 4 hours
**Priority**: High
**Dependencies**: Task F1.1, Backend tasks

**Description**: Replace old endpoints with hotel-specific endpoints

**Changes Needed**:
1. Update auth endpoints (add role to response)
2. Add room type endpoints
3. Update room endpoints
4. Add guest endpoints (replace tenant endpoints)
5. Add reservation endpoints
6. Update payment endpoints
7. Remove expense endpoints
8. Update dashboard endpoints

**New API Client Methods**:
```typescript
class ApiClient {
  // Auth
  login(username, password): Promise<LoginResponse>
  getCurrentUser(): Promise<{user: User}>

  // Room Types
  getRoomTypes(): Promise<RoomType[]>
  createRoomType(data): Promise<RoomType>
  updateRoomType(id, data): Promise<RoomType>
  deleteRoomType(id): Promise<void>

  // Rooms
  getRooms(): Promise<Room[]>
  getRoom(id): Promise<Room>
  checkAvailability(checkIn, checkOut, roomTypeId): Promise<AvailabilityResponse>

  // Guests
  getGuests(): Promise<Guest[]>
  searchGuests(query): Promise<Guest[]>
  createGuest(data): Promise<Guest>
  updateGuest(id, data): Promise<Guest>
  getGuestReservations(id): Promise<Reservation[]>

  // Reservations
  getReservations(filters?): Promise<Reservation[]>
  getReservation(id): Promise<Reservation>
  createReservation(data): Promise<Reservation>
  updateReservation(id, data): Promise<Reservation>
  cancelReservation(id): Promise<Reservation>
  checkIn(id, roomId): Promise<Reservation>
  checkOut(id): Promise<Reservation>
  extendStay(id, newCheckOut): Promise<Reservation>
  getArrivals(date?): Promise<Reservation[]>
  getDepartures(date?): Promise<Reservation[]>
  getInHouse(): Promise<Reservation[]>

  // Payments
  getPayments(reservationId): Promise<Payment[]>
  createPayment(data): Promise<Payment>

  // Dashboard
  getDashboardMetrics(): Promise<DashboardMetrics>
  getDashboardSummary(dateFrom?, dateTo?): Promise<DashboardSummary>
}
```

**Acceptance Criteria**:
- [ ] All new endpoints implemented
- [ ] Old endpoints removed
- [ ] Token included in all requests
- [ ] Error handling working
- [ ] 401 triggers auto-logout

**Files to Modify**:
- `frontend/src/services/api.ts`

---

### Task F1.3: Update AuthStore with Role Support
**Estimated Time**: 2 hours
**Priority**: High
**Dependencies**: Task F1.1

**Description**: Add role-based permission helpers to authStore

**Changes Needed**:
1. Add role to user state
2. Add permission helpers:
   - `isAdmin()` - check if user is admin
   - `canDelete()` - check if user can delete
   - `canEditUsers()` - check if user can manage users

**Updated AuthStore**:
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;

  // Permission helpers
  isAdmin: () => boolean;
  canDelete: () => boolean;
  canEditUsers: () => boolean;

  // Existing actions...
}
```

**Acceptance Criteria**:
- [ ] Role stored in state
- [ ] Permission helpers working
- [ ] UI elements conditionally rendered based on role

**Files to Modify**:
- `frontend/src/stores/authStore.ts`

---

## **PHASE 2: Layout & Navigation (Week 1-2)**

### Task F2.1: Update Sidebar Navigation
**Estimated Time**: 2 hours
**Priority**: High
**Dependencies**: Task F1.3

**Description**: Update sidebar menu for hotel system

**New Menu Items**:
```
Dashboard
Reservations (new)
├─ All Reservations
├─ New Reservation
├─ Check-In
└─ Check-Out
Guests (replaces Tenants)
Rooms
├─ All Rooms
└─ Room Types (admin only)
Payments (modified)
Users (admin only)
```

**Changes**:
- Replace "Tenants" with "Guests"
- Add "Reservations" with submenu
- Remove "Expenses"
- Add "Room Types" under Rooms (admin only)
- Conditional rendering based on role

**Acceptance Criteria**:
- [ ] All menu items updated
- [ ] Admin-only items hidden for users
- [ ] Active route highlighting works
- [ ] Icons updated for hotel context

**Files to Modify**:
- `frontend/src/components/Sidebar.tsx`

---

### Task F2.2: Update Navbar Component
**Estimated Time**: 1 hour
**Priority**: Medium
**Dependencies**: Task F1.3

**Description**: Display user role in navbar

**Changes**:
- Show user role badge (Admin/User)
- Keep language switcher
- Keep logout button

**Acceptance Criteria**:
- [ ] Role displayed next to username
- [ ] Role styled with color (admin = blue, user = green)
- [ ] Responsive on mobile

**Files to Modify**:
- `frontend/src/components/Navbar.tsx`

---

### Task F2.3: Update i18n Translations
**Estimated Time**: 2 hours
**Priority**: Medium
**Dependencies**: None

**Description**: Update translation files for hotel terminology

**Changes**:
1. Update existing keys:
   - "tenants" → "guests"
   - "move_in" → "check_in"
   - "move_out" → "check_out"
   - "monthly_rate" → "rate_per_night"

2. Add new keys:
   - "reservations", "confirmation_number"
   - "arrivals", "departures", "in_house"
   - "room_types", "room_type"
   - "extend_stay", "walk_in"
   - "balance", "payment_status"

3. Remove unused keys:
   - "expenses", "expense_category"
   - "net_profit" (keep revenue)

**Acceptance Criteria**:
- [ ] All UI text translated (EN + ID)
- [ ] No missing translation warnings
- [ ] Hotel terminology consistent

**Files to Modify**:
- `frontend/src/locales/en.json`
- `frontend/src/locales/id.json`

---

## **PHASE 3: Room Management (Week 2)**

### Task F3.1: Create Room Types Page
**Estimated Time**: 5 hours
**Priority**: High
**Dependencies**: Task F1.2

**Description**: Admin page to manage room types

**Create**: `frontend/src/pages/RoomTypesPage.tsx`

**Features**:
- List all room types in table
- Create/Edit/Delete room types (admin only)
- Show room count per type
- Modal form for create/edit

**UI Elements**:
- Table with columns: Code, Name, Capacity, Bed Config, Default Rate, Rooms Count, Actions
- "Add Room Type" button
- Edit/Delete actions per row
- Form fields: name, code, capacities, bed_config, default_rate, amenities (textarea)

**Acceptance Criteria**:
- [ ] Admin can create room types
- [ ] Admin can edit room types
- [ ] Admin can delete (with confirmation)
- [ ] Cannot delete if rooms exist with that type
- [ ] Form validation working
- [ ] Success/error messages shown

**Important Notes**:
- ⚠️ **Custom Rate for Rooms**: Remember that individual rooms can have custom rates (either fixed price or percentage markup/discount). The default_rate here is for the room TYPE, but rooms can override it. See Room task F3.2 for custom rate input implementation.

**Files to Create**:
- `frontend/src/pages/RoomTypesPage.tsx`

**Files to Modify**:
- `frontend/src/App.tsx` (add route)

---

### Task F3.2: Update Rooms Page
**Estimated Time**: 4 hours
**Priority**: High
**Dependencies**: Task F3.1

**Description**: Update rooms page for hotel system

**Modify**: `frontend/src/pages/RoomsPage.tsx`

**Changes**:
- Display room type instead of room_type string
- Show room status with new values (available, occupied, out_of_order)
- Remove tenant display (will show in reservations)
- Add room type filter dropdown
- Update status colors

**New Features**:
- Filter by room type
- Filter by floor
- Filter by status
- Create room with room type selection

**Acceptance Criteria**:
- [ ] Rooms displayed with room type name
- [ ] Status colors: green (available), blue (occupied), red (out_of_order)
- [ ] Filters working
- [ ] Admin can create/edit/delete
- [ ] User can only view
- [ ] **Admin can manually change room status** (dropdown or button to set available/occupied/out_of_order)

**Custom Rate Input** (in create/edit form):
- ⚠️ **IMPORTANT**: Provide TWO input options for room pricing:
  1. **Fixed Price**: Direct price input (e.g., "600000")
  2. **Percentage**: Markup/discount percentage (e.g., "20" for +20%, "-10" for -10%)
- Use a toggle/selector to let admin choose: "Fixed Price" or "Percentage"
- Show: "Room Type Default Rate: IDR 500,000" for reference
- When percentage selected: Show preview calculation (e.g., "500,000 × 1.20 = 600,000")
- **Backend will handle conversion**: Frontend sends the choice, backend converts percentage to fixed price
- Store only final fixed price in `custom_rate` field

**Files to Modify**:
- `frontend/src/pages/RoomsPage.tsx`

---

### Task F3.3: Create/Update Room Store
**Estimated Time**: 2 hours
**Priority**: Medium
**Dependencies**: Task F1.2

**Description**: Update room store for room types

**Modify**: `frontend/src/stores/roomStore.ts`

**Changes**:
- Add roomTypes state
- Add fetchRoomTypes() action
- Add createRoomType(), updateRoomType(), deleteRoomType()
- Update room interface

**Acceptance Criteria**:
- [ ] Room types loaded and cached
- [ ] CRUD operations working
- [ ] Error handling in place

**Files to Modify**:
- `frontend/src/stores/roomStore.ts`

---

## **PHASE 4: Guest Management (Week 2-3)**

### Task F4.1: Create Guests Page
**Estimated Time**: 6 hours
**Priority**: High
**Dependencies**: Task F1.2

**Description**: Replace TenantsPage with GuestsPage

**Create**: `frontend/src/pages/GuestsPage.tsx` (rewrite TenantsPage)

**Features**:
- List all guests in table
- Search by name, email, phone
- Create/Edit guest
- View guest reservation history
- Cannot delete guests (or soft delete)

**UI Elements**:
- Search bar
- Guest table: Name, Email, Phone, Nationality, Last Stay, Actions
- "Add Guest" button
- Modal form for create/edit
- Guest detail modal showing reservation history

**Form Fields**:
- full_name (required)
- email, phone
- id_type, id_number
- nationality
- notes (textarea)

**Acceptance Criteria**:
- [ ] Guests displayed in table
- [ ] Search working (fuzzy match)
- [ ] Can create/edit guests
- [ ] Guest history shows past reservations
- [ ] Form validation working
- [ ] Both admin and user can create guests

**Files to Create**:
- `frontend/src/pages/GuestsPage.tsx`

**Files to Modify**:
- `frontend/src/App.tsx` (update route)

---

### Task F4.2: Create Guest Store
**Estimated Time**: 2 hours
**Priority**: High
**Dependencies**: Task F1.2

**Description**: Create Zustand store for guests

**Create**: `frontend/src/stores/guestStore.ts`

**State**:
```typescript
interface GuestState {
  guests: Guest[];
  isLoading: boolean;
  error: string | null;

  fetchGuests: () => Promise<void>;
  searchGuests: (query: string) => Promise<void>;
  createGuest: (data) => Promise<Guest>;
  updateGuest: (id, data) => Promise<Guest>;
  getGuestReservations: (id) => Promise<Reservation[]>;
}
```

**Acceptance Criteria**:
- [ ] Guests loaded and cached
- [ ] Search working
- [ ] CRUD operations working
- [ ] Error handling

**Files to Create**:
- `frontend/src/stores/guestStore.ts`

---

## **PHASE 5: Reservation System (Week 3-5)** ← **Most Complex**

### Task F5.1: Create Availability Search Component
**Estimated Time**: 6 hours
**Priority**: Critical
**Dependencies**: Task F1.2, F3.1

**Description**: Reusable component for checking room availability

**Create**: `frontend/src/components/AvailabilitySearch.tsx`

**Features**:
- Date range picker (check-in, check-out)
- Room type selector
- Number of guests (adults, children)
- Search button
- Display available rooms
- Display rate and total price

**UI**:
- Form with: Check-in Date, Check-out Date, Room Type, Adults, Children
- "Search Availability" button
- Results list showing: Room Type, Available Count, Rate per Night, Total (nights × rate)
- "Select" button for each room type

**Business Logic**:
- Calculate nights = checkout - checkin
- Call availability API
- Display results
- Allow selection

**Acceptance Criteria**:
- [ ] Date range validation (checkout > checkin)
- [ ] Availability API called correctly
- [ ] Results displayed clearly
- [ ] Nights and total calculated
- [ ] Can select room type
- [ ] Reusable in multiple pages

**Files to Create**:
- `frontend/src/components/AvailabilitySearch.tsx`

---

### Task F5.2: Create New Reservation Page
**Estimated Time**: 8 hours
**Priority**: Critical
**Dependencies**: Task F5.1, F4.1

**Description**: Multi-step reservation creation form

**Create**: `frontend/src/pages/NewReservationPage.tsx`

**Steps**:
1. **Step 1: Guest Selection**
   - Search existing guest OR create new guest
   - Form to create new guest inline

2. **Step 2: Availability Search**
   - Use AvailabilitySearch component
   - Select room type
   - Optionally assign specific room

3. **Step 3: Reservation Details**
   - Confirm dates, guest, room type
   - Edit rate if needed (admin only)
   - Add special requests
   - Select booking source

4. **Step 4: Confirmation**
   - Review all details
   - Create reservation
   - Show confirmation number

**Acceptance Criteria**:
- [ ] Can search/create guest
- [ ] Availability check working
- [ ] Can create reservation
- [ ] Confirmation number displayed
- [ ] Form validation at each step
- [ ] Can go back/forward between steps
- [ ] Admin can override rate

**Files to Create**:
- `frontend/src/pages/NewReservationPage.tsx`
- `frontend/src/components/GuestSelector.tsx` (helper component)

**Files to Modify**:
- `frontend/src/App.tsx` (add route)

---

### Task F5.3: Create Reservations List Page
**Estimated Time**: 6 hours
**Priority**: High
**Dependencies**: Task F5.2

**Description**: View all reservations with filters

**Create**: `frontend/src/pages/ReservationsPage.tsx`

**Features**:
- List all reservations in table
- Filters: Status, Date range, Guest name, Room number
- Search by confirmation number
- Color-coded by status
- Click row to view details

**Table Columns**:
- Confirmation #, Guest Name, Room, Check-In, Check-Out, Status, Total, Actions

**Actions per row**:
- View/Edit (icon)
- Check-In (if confirmed)
- Check-Out (if checked_in)
- Cancel (admin only, if not checked_out)

**Acceptance Criteria**:
- [ ] All reservations displayed
- [ ] Filters working
- [ ] Search by confirmation working
- [ ] Status color-coded
- [ ] Actions available based on status
- [ ] Pagination working (if many reservations)

**Files to Create**:
- `frontend/src/pages/ReservationsPage.tsx`

**Files to Modify**:
- `frontend/src/App.tsx` (add route)

---

### Task F5.4: Create Reservation Detail/Edit Modal
**Estimated Time**: 5 hours
**Priority**: High
**Dependencies**: Task F5.3

**Description**: View and edit reservation details

**Create**: `frontend/src/components/ReservationModal.tsx`

**Features**:
- Display all reservation details
- Edit mode for: dates, room, rate, special requests
- Show guest info (read-only, link to guest)
- Show payment history
- Actions: Extend Stay, Cancel, Check-In, Check-Out

**Sections**:
1. Guest Information
2. Reservation Details (dates, room, rate)
3. Payment Summary (total, paid, balance)
4. Special Requests
5. Status History (created, checked-in, checked-out dates)

**Acceptance Criteria**:
- [ ] All details displayed
- [ ] Can edit if not checked-out
- [ ] Date changes check availability
- [ ] Actions work based on status
- [ ] Payment balance calculated

**Files to Create**:
- `frontend/src/components/ReservationModal.tsx`

---

### Task F5.5: Create Reservation Store
**Estimated Time**: 3 hours
**Priority**: High
**Dependencies**: Task F1.2

**Description**: Zustand store for reservations

**Create**: `frontend/src/stores/reservationStore.ts`

**State**:
```typescript
interface ReservationState {
  reservations: Reservation[];
  isLoading: boolean;
  error: string | null;

  fetchReservations: (filters?) => Promise<void>;
  getReservation: (id) => Promise<Reservation>;
  createReservation: (data) => Promise<Reservation>;
  updateReservation: (id, data) => Promise<Reservation>;
  cancelReservation: (id) => Promise<void>;
  checkIn: (id, roomId) => Promise<Reservation>;
  checkOut: (id) => Promise<Reservation>;
  extendStay: (id, newCheckOut) => Promise<Reservation>;
  checkAvailability: (checkIn, checkOut, roomTypeId) => Promise<any>;
}
```

**Acceptance Criteria**:
- [ ] All CRUD operations working
- [ ] Availability checking working
- [ ] Error handling
- [ ] Loading states

**Files to Create**:
- `frontend/src/stores/reservationStore.ts`

---

## **PHASE 6: Check-In/Out Operations (Week 5)**

### Task F6.1: Create Check-In Page
**Estimated Time**: 5 hours
**Priority**: Critical
**Dependencies**: Task F5.5

**Description**: Today's arrivals and check-in processing

**Create**: `frontend/src/pages/CheckInPage.tsx`

**Features**:
- Display today's expected arrivals
- Filter by checked-in status (show only confirmed)
- Search by guest name or confirmation number
- Click reservation to check-in
- Assign room if not already assigned
- Mark as checked-in

**UI**:
- Title: "Check-In - Arrivals Today"
- Date selector (defaults to today)
- Table: Confirmation #, Guest, Room Type, Room Assigned, Adults, Special Requests, Action
- "Check In" button per row

**Check-In Flow**:
1. Click "Check In" on reservation
2. If room not assigned, show room selector (available rooms of that type)
3. Confirm room assignment
4. Call check-in API
5. Update reservation status
6. Show success message

**Acceptance Criteria**:
- [ ] Today's arrivals displayed
- [ ] Can assign room during check-in
- [ ] Cannot check-in without room
- [ ] Reservation status updates to checked_in
- [ ] Room status updates to occupied
- [ ] Success notification shown

**Files to Create**:
- `frontend/src/pages/CheckInPage.tsx`
- `frontend/src/components/RoomSelector.tsx` (helper)

**Files to Modify**:
- `frontend/src/App.tsx` (add route)

---

### Task F6.2: Create Check-Out Page
**Estimated Time**: 5 hours
**Priority**: Critical
**Dependencies**: Task F5.5, F7.1

**Description**: Today's departures and check-out processing

**Create**: `frontend/src/pages/CheckOutPage.tsx`

**Features**:
- Display today's expected departures
- Show only checked-in reservations
- Display payment balance
- Record final payment
- Mark as checked-out

**UI**:
- Title: "Check-Out - Departures Today"
- Date selector (defaults to today)
- Table: Room, Guest, Check-In, Total, Paid, Balance, Action
- "Check Out" button per row

**Check-Out Flow**:
1. Click "Check Out" on reservation
2. Show modal with:
   - Guest details
   - Stay summary (dates, room, nights)
   - Payment summary (total, paid, balance)
   - Payment form (if balance remaining)
3. Record final payment (optional)
4. Confirm check-out
5. Call check-out API
6. Show receipt/summary

**Acceptance Criteria**:
- [ ] Today's departures displayed
- [ ] Balance calculated correctly
- [ ] Can record final payment
- [ ] Reservation status updates to checked_out
- [ ] Room status updates to available
- [ ] Receipt/summary shown

**Files to Create**:
- `frontend/src/pages/CheckOutPage.tsx`
- `frontend/src/components/CheckOutModal.tsx`

**Files to Modify**:
- `frontend/src/App.tsx` (add route)

---

### Task F6.3: Create In-House Guests Page
**Estimated Time**: 4 hours
**Priority**: High
**Dependencies**: Task F5.5

**Description**: Display currently checked-in guests with quick actions

**Create**: `frontend/src/pages/InHouseGuestsPage.tsx`

**Features**:
- List all checked-in guests (status = 'checked_in')
- Table with: Room, Guest Name, Check-In Date, Check-Out Date, Nights Remaining
- Filter/sort by room number, guest name, checkout date
- Quick actions: View Details, Extend Stay, Early Check-Out
- Color-coding: Red if checking out today, Yellow if checking out tomorrow

**UI**:
- Title: "In-House Guests"
- Guest count badge
- Table with sortable columns
- Action buttons per row

**Acceptance Criteria**:
- [ ] Shows only checked-in reservations
- [ ] Sortable by room, name, checkout date
- [ ] "Extend Stay" opens modal to change checkout date
- [ ] "Check Out" navigates to check-out page with pre-selected reservation
- [ ] Auto-refreshes data
- [ ] Responsive on tablet

**Files to Create**:
- `frontend/src/pages/InHouseGuestsPage.tsx`

**Files to Modify**:
- `frontend/src/App.tsx` (add route)
- `frontend/src/components/Sidebar.tsx` (add menu item)

---

## **PHASE 7: Payment Tracking (Week 6)**

### Task F7.1: Update Payments Page
**Estimated Time**: 5 hours
**Priority**: High
**Dependencies**: Task F5.3

**Description**: Redesign payments page for reservation-based payments

**Modify**: `frontend/src/pages/PaymentsPage.tsx`

**Features**:
- List all payments with reservation details
- Filter by reservation (dropdown)
- Filter by date range
- Create payment against reservation
- Show balance per reservation

**Table Columns**:
- Date, Reservation #, Guest, Amount, Method, Reference, Balance, Actions

**Payment Form**:
- Select reservation (search by confirmation or guest)
- Payment date (default today)
- Amount
- **Payment method dropdown** (Cash, Credit Card, Debit Card, Bank Transfer, Other)
- Reference number (optional)
- Notes (optional)

**Acceptance Criteria**:
- [ ] All payments displayed
- [ ] Can filter by reservation
- [ ] Can record payment
- [ ] **Payment method dropdown with 5 options** (validated)
- [ ] Balance updates after payment
- [ ] Admin can edit/delete payments
- [ ] User can only create payments

**Files to Modify**:
- `frontend/src/pages/PaymentsPage.tsx`

---

### Task F7.2: Create Payment Form Component
**Estimated Time**: 3 hours
**Priority**: Medium
**Dependencies**: Task F7.1

**Description**: Reusable payment recording form

**Create**: `frontend/src/components/PaymentForm.tsx`

**Props**:
- reservation (optional - pre-select reservation)
- onSuccess (callback after payment created)

**Features**:
- Reservation selector (if not provided)
- Show reservation total and balance
- Payment form fields
- Validation

**Acceptance Criteria**:
- [ ] Reusable in multiple places
- [ ] Shows balance before payment
- [ ] Validates amount > 0
- [ ] Validates payment method selected
- [ ] Calls create payment API

**Files to Create**:
- `frontend/src/components/PaymentForm.tsx`

---

## **PHASE 8: Dashboard (Week 6-7)**

### Task F8.1: Update Dashboard Page
**Estimated Time**: 6 hours
**Priority**: High
**Dependencies**: All previous tasks

**Description**: Redesign dashboard for hotel metrics

**Modify**: `frontend/src/pages/DashboardPage.tsx`

**Sections**:

1. **Today's Summary** (Top Cards)
   - Arrivals Today (count + list link)
   - Departures Today (count + list link)
   - In-House Guests (count + list link)
   - Available Rooms (count)

2. **Occupancy Metrics** (Cards)
   - Current Occupancy Rate (%)
   - Occupied Rooms / Total Rooms
   - Rooms by Status (available, occupied, out_of_order)

3. **Revenue Summary** (Cards)
   - Total Revenue This Month
   - Total Payments This Month
   - Outstanding Balance

4. **Quick Access** (Buttons/Links)
   - New Reservation
   - Check In
   - Check Out
   - View Reservations

5. **Upcoming** (Simple Lists)
   - Next 7 Days Arrivals (by day)
   - Next 7 Days Departures (by day)

**No Charts** (per MVP scope)

**Acceptance Criteria**:
- [ ] All metrics displayed correctly
- [ ] Real-time data (no caching)
- [ ] Date range selector (This Month, Last Month, Custom)
- [ ] Quick access links working
- [ ] Responsive layout
- [ ] Loads < 3 seconds

**Files to Modify**:
- `frontend/src/pages/DashboardPage.tsx`

---

### Task F8.2: Update Dashboard Store
**Estimated Time**: 2 hours
**Priority**: High
**Dependencies**: Task F1.2

**Description**: Update dashboard store for hotel metrics

**Modify**: `frontend/src/stores/dashboardStore.ts`

**State**:
```typescript
interface DashboardState {
  metrics: DashboardMetrics | null;
  summary: DashboardSummary | null;
  isLoading: boolean;
  error: string | null;

  fetchMetrics: () => Promise<void>;
  fetchSummary: (dateFrom?, dateTo?) => Promise<void>;
}

interface DashboardMetrics {
  date: string;
  arrivals_today: number;
  departures_today: number;
  in_house: number;
  available_rooms: number;
  total_rooms: number;
  occupancy_rate: number;
  rooms_by_status: {
    available: number;
    occupied: number;
    out_of_order: number;
  };
}

interface DashboardSummary {
  date_from: string;
  date_to: string;
  total_revenue: number;
  total_payments: number;
  outstanding_balance: number;
}
```

**Acceptance Criteria**:
- [ ] Metrics fetched and cached
- [ ] Summary with date range working
- [ ] Error handling
- [ ] Loading states

**Files to Modify**:
- `frontend/src/stores/dashboardStore.ts`

---

## **PHASE 9: User Management (Week 7)**

### Task F9.1: Update Users Page with Role Management
**Estimated Time**: 4 hours
**Priority**: Medium
**Dependencies**: Task F1.3

**Description**: Add role field to user management

**Modify**: `frontend/src/pages/UsersPage.tsx`

**Changes**:
- Add role column to user table
- Add role selector in create/edit form
- Add full_name field
- Add status field (active/inactive)
- Show role badges (colored)

**Form Fields**:
- username (required)
- password (required for create, optional for edit)
- email
- full_name
- role (admin/user) - dropdown
- status (active/inactive) - toggle

**Acceptance Criteria**:
- [ ] Admin can create users with role
- [ ] Admin can edit user role
- [ ] Admin can activate/deactivate users
- [ ] Cannot change own role
- [ ] Cannot delete self
- [ ] Role displayed with color badge

**Files to Modify**:
- `frontend/src/pages/UsersPage.tsx`

---

## **PHASE 10: Polish & Testing (Week 8)**

### Task F10.1: Add Loading States
**Estimated Time**: 3 hours
**Priority**: High
**Dependencies**: All previous tasks

**Description**: Consistent loading indicators across app

**Create**: `frontend/src/components/LoadingSpinner.tsx`

**Changes**:
- Add loading spinners to all async operations
- Add skeleton screens for tables
- Add button loading states
- Disable forms during submission

**Acceptance Criteria**:
- [ ] Loading spinner shows during API calls
- [ ] Buttons show loading state
- [ ] Forms disabled during submission
- [ ] Consistent across all pages

**Files to Create**:
- `frontend/src/components/LoadingSpinner.tsx`
- `frontend/src/components/TableSkeleton.tsx`

**Files to Modify**:
- All page components

---

### Task F10.2: Add Error Handling & Notifications
**Estimated Time**: 3 hours
**Priority**: High
**Dependencies**: All previous tasks

**Description**: User-friendly error messages and notifications

**Create**: `frontend/src/components/Toast.tsx`

**Features**:
- Toast notifications for success/error
- Clear error messages (not just "Error 500")
- Retry logic for failed requests
- Network error detection

**Notification Types**:
- Success (green)
- Error (red)
- Warning (yellow)
- Info (blue)

**Acceptance Criteria**:
- [ ] Success notifications shown
- [ ] Error messages clear and helpful
- [ ] Network errors handled gracefully
- [ ] Auto-dismiss after 5 seconds

**Files to Create**:
- `frontend/src/components/Toast.tsx`
- `frontend/src/stores/notificationStore.ts`

---

### Task F10.3: Add Form Validation
**Estimated Time**: 4 hours
**Priority**: High
**Dependencies**: All form tasks

**Description**: Client-side validation for all forms

**Validation Rules**:
- Required fields
- Email format
- Phone format
- Date ranges (checkout > checkin)
- Positive numbers (amounts, rates)
- Unique constraints (confirmation numbers)

**Acceptance Criteria**:
- [ ] All forms validated
- [ ] Error messages displayed inline
- [ ] Submit button disabled if invalid
- [ ] Clear validation on field change

**Files to Modify**:
- All forms/pages with input

---

### Task F10.4: Mobile Responsiveness
**Estimated Time**: 5 hours
**Priority**: High
**Dependencies**: All UI tasks

**Description**: Ensure all pages work on tablets and phones

**Breakpoints**:
- Desktop: > 1024px
- Tablet: 768px - 1024px
- Mobile: < 768px

**Changes**:
- Responsive tables (stack on mobile)
- Collapsible sidebar on mobile
- Touch-friendly buttons (min 44px)
- Horizontal scrolling for wide tables

**Acceptance Criteria**:
- [ ] All pages usable on tablet
- [ ] Critical flows work on mobile
- [ ] Navigation works on small screens
- [ ] Forms easy to fill on touch devices

**Files to Modify**:
- All page components
- Layout components

---

### Task F10.5: Accessibility (A11y)
**Estimated Time**: 3 hours
**Priority**: Medium
**Dependencies**: All UI tasks

**Description**: Basic accessibility improvements

**Changes**:
- Proper heading hierarchy (h1, h2, h3)
- Alt text for images
- Aria labels for buttons/links
- Keyboard navigation
- Focus indicators
- Color contrast (WCAG AA)

**Acceptance Criteria**:
- [ ] Can navigate with keyboard
- [ ] Screen reader compatible
- [ ] Focus indicators visible
- [ ] Color contrast ratio > 4.5:1

**Files to Modify**:
- All components

---

## **PHASE 11: Deployment Prep (Week 8)**

### Task F11.1: Environment Configuration
**Estimated Time**: 2 hours
**Priority**: High
**Dependencies**: None

**Description**: Environment-specific configuration

**Create**: `.env.example`

**Environment Variables**:
```
VITE_API_URL=http://localhost:8001/api
VITE_APP_NAME=Hotel Management System
VITE_APP_VERSION=1.0.0
```

**Changes**:
- Read API URL from env
- Add version display
- Different configs for dev/staging/prod

**Acceptance Criteria**:
- [ ] API URL configurable
- [ ] Works in dev, staging, prod
- [ ] .env.example documented

**Files to Create**:
- `.env.example`

**Files to Modify**:
- `frontend/src/services/api.ts`

---

### Task F11.2: Build Optimization
**Estimated Time**: 2 hours
**Priority**: Medium
**Dependencies**: None

**Description**: Optimize production build

**Changes**:
1. Code splitting (lazy load routes)
2. Tree shaking (remove unused code)
3. Minification
4. Asset optimization

**Vite Config**:
```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['tailwindcss'],
          state: ['zustand'],
        },
      },
    },
  },
});
```

**Acceptance Criteria**:
- [ ] Bundle size < 200KB gzipped
- [ ] Lazy loading routes working
- [ ] Build time < 30 seconds

**Files to Modify**:
- `frontend/vite.config.ts`

---

## Summary

### Total Estimated Time: **100 hours (~12-13 weeks at 8 hours/week or 5-6 weeks full-time)**

### Task Count: **33 tasks** (added F6.3: In-House Guests Page)

### Critical Path:
1. Phase 1: Foundation (Week 1)
2. Phase 2: Layout (Week 1-2)
3. Phase 3: Rooms (Week 2)
4. Phase 4: Guests (Week 2-3)
5. Phase 5: Reservations (Week 3-5) ← **Most Complex**
6. Phase 6: Check-in/out (Week 5)
7. Phase 7: Payments (Week 6)
8. Phase 8: Dashboard (Week 6-7)
9. Phase 9: Users (Week 7)
10. Phase 10: Polish (Week 8)
11. Phase 11: Deploy (Week 8)

### Priority Distribution:
- **Critical**: 4 tasks (Reservations, Check-in, Check-out, Availability)
- **High**: 21 tasks
- **Medium**: 7 tasks

---

## Quick Start Checklist

**Week 1:**
- [ ] F1.1: Update API types
- [ ] F1.2: Update API client
- [ ] F1.3: Update auth store with roles
- [ ] F2.1: Update sidebar navigation
- [ ] F2.2: Update navbar
- [ ] F2.3: Update translations

**Week 2:**
- [ ] F3.1: Room types page
- [ ] F3.2: Update rooms page
- [ ] F3.3: Room store
- [ ] F4.1: Guests page
- [ ] F4.2: Guest store

**Week 3-4:**
- [ ] F5.1: Availability search component
- [ ] F5.2: New reservation page
- [ ] F5.3: Reservations list page
- [ ] F5.4: Reservation detail modal
- [ ] F5.5: Reservation store

**Week 5:**
- [ ] F6.1: Check-in page
- [ ] F6.2: Check-out page

**Week 6:**
- [ ] F7.1: Update payments page
- [ ] F7.2: Payment form component
- [ ] F8.1: Update dashboard
- [ ] F8.2: Dashboard store

**Week 7:**
- [ ] F9.1: Users page with roles
- [ ] F10.1: Loading states
- [ ] F10.2: Error handling
- [ ] F10.3: Form validation

**Week 8:**
- [ ] F10.4: Mobile responsiveness
- [ ] F10.5: Accessibility
- [ ] F11.1: Environment config
- [ ] F11.2: Build optimization

---

## New NPM Packages to Install

```bash
npm install axios date-fns react-icons
```

Optional (for better forms):
```bash
npm install react-hook-form
```

---

## Development Best Practices

1. **Component Reusability**: Extract common UI patterns
2. **Type Safety**: Use TypeScript interfaces for all data
3. **Error Boundaries**: Add React error boundaries
4. **Consistent Styling**: Use Tailwind utility classes
5. **Code Splitting**: Lazy load route components
6. **Performance**: Avoid unnecessary re-renders (React.memo)
7. **Testing**: Write tests for critical flows (optional for MVP)

---

## Next Steps

1. **Review backend tasks** - Frontend depends on backend API
2. **Start with Phase 1** (Foundation & Types)
3. **Work sequentially** through phases
4. **Test each component** before moving on
5. **Keep backend and frontend in sync**

**Ready to code?** Start with Phase 1, Task F1.1! 🚀
