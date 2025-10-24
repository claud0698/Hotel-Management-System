# Frontend Components Reference Guide

## 📋 Complete Component Inventory

### Pages (Main Features)

#### **LoginPage** (`src/pages/LoginPage.tsx`)
- **Purpose**: User authentication
- **Features**:
  - Username/password input fields
  - Login form submission
  - Error message display
  - Loading state
  - Demo credentials info
  - Responsive design with gradient background
- **State Used**: `useAuthStore`
- **Routes To**: Dashboard on success
- **Public Route**: Yes

#### **DashboardPage** (`src/pages/DashboardPage.tsx`)
- **Purpose**: Main overview with key metrics
- **Features**:
  - Occupancy rate card (with color coding)
  - Monthly revenue card
  - Monthly expenses card
  - Net profit card (green/red based on value)
  - Room status summary
  - Payment status alerts
  - Recent payments list (last 5)
  - Recent expenses list (last 5)
  - Loading state
  - Currency formatting (IDR)
- **State Used**: `useDashboardStore`
- **Data Fetched**:
  - Dashboard metrics
  - Dashboard summary
- **Auto-refresh**: On component mount

#### **RoomsPage** (`src/pages/RoomsPage.tsx`)
- **Purpose**: Manage property rooms
- **Features**:
  - View all rooms in grid layout
  - Create new room form
    - Room number (required, unique)
    - Floor number
    - Room type (single, double, suite)
    - Monthly rate (required, in IDR)
    - Status (available, occupied, maintenance)
    - Amenities (comma-separated)
  - Edit room details (via delete/recreate pattern)
  - Delete room with confirmation
  - Status-based color badges
  - Show current tenant if assigned
  - Error handling and messages
  - Loading states
- **State Used**: `useRoomStore`
- **Protected Route**: Yes
- **Data Operations**: CRUD

#### **TenantsPage** (`src/pages/TenantsPage.tsx`)
- **Purpose**: Manage tenant information
- **Features**:
  - View all tenants in table
  - Create new tenant form
    - Full name (required)
    - Phone number
    - Email address
    - ID number (KTP/Passport)
    - Move-in date
    - Room assignment (dropdown with available rooms)
    - Status (active, inactive, moved out)
    - Notes
  - Edit existing tenant
  - Delete tenant with confirmation
  - Room assignment validation
  - Status-based color indicators
  - Quick action buttons
  - Form validation
- **State Used**: `useTenantStore`, `useRoomStore`
- **Protected Route**: Yes
- **Data Operations**: CRUD
- **Dependencies**: Requires rooms data

#### **PaymentsPage** (`src/pages/PaymentsPage.tsx`)
- **Purpose**: Record and track rent payments
- **Features**:
  - Create payment form
    - Tenant selection (dropdown)
    - Number of months (1, 2, 3+)
    - Payment date picker
    - Payment method (cash, transfer, check, other)
    - Optional notes
  - Automatic monthly date calculation
  - Creates multiple payment records at once
  - View all payments in table
  - Filter by status (all, paid, pending, overdue)
  - Status-based color indicators
  - Payment method tracking
  - Paid date auto-set to current
  - Currency formatting
  - Tenant name lookup
- **State Used**: Direct API calls
- **Protected Route**: Yes
- **Data Operations**: Create, Read, Filter
- **Special Feature**: Duration-based payment entry (e.g., "2 months" = 2 entries)

#### **ExpensesPage** (`src/pages/ExpensesPage.tsx`)
- **Purpose**: Track business expenses
- **Features**:
  - Create expense form
    - Date picker (any date, not just today)
    - Category dropdown (utilities, maintenance, supplies, cleaning, other)
    - Amount (in IDR)
    - Description
    - Receipt URL (optional)
  - Edit existing expense
  - Delete expense with confirmation
  - View all expenses in table
  - Total expenses calculation and display
  - Category label with emoji
  - Date formatting (local format)
  - Currency formatting
  - Form validation
  - Error handling
- **State Used**: Direct API calls
- **Protected Route**: Yes
- **Data Operations**: CRUD
- **Special Feature**: Category icons and descriptions

---

### Layout Components

#### **Navbar** (`src/components/Navbar.tsx`)
- **Purpose**: Top navigation bar
- **Features**:
  - Logo/branding (Kos Dashboard 🏠)
  - Welcome message with username
  - Logout button
  - Responsive design
  - White background with shadow
- **State Used**: `useAuthStore`
- **Navigation**: Logo links to home
- **Actions**:
  - Logout → redirects to /login
  - Clears auth state

#### **Sidebar** (`src/components/Sidebar.tsx`)
- **Purpose**: Left navigation menu
- **Features**:
  - Navigation links to all features
  - Active route highlighting
  - Emoji icons for each section
  - Dark theme
  - Fixed positioning
  - Scrollable if content exceeds height
  - Menu items:
    - Dashboard 📊
    - Rooms 🏘️
    - Tenants 👥
    - Payments 💰
    - Expenses 💸
- **State Used**: `useLocation` (React Router)
- **Styling**: Dark gray background (#1F2937), white text
- **Responsive**: Hidden on very small screens (can be enhanced)

#### **Layout** (`src/components/Layout.tsx`)
- **Purpose**: Main wrapper for authenticated pages
- **Features**:
  - Combines Navbar + Sidebar
  - Wraps page content
  - Conditional rendering based on auth status
  - Responsive grid layout
  - Full-height layout
- **State Used**: `useAuthStore`
- **Child**: Any page component
- **Styling**: Flexbox layout for proper spacing

---

### Store (State Management)

#### **AuthStore** (`src/stores/authStore.ts`)
- **State**:
  - `user`: Current logged-in user
  - `token`: JWT token
  - `isLoading`: Request state
  - `error`: Error message
  - `isAuthenticated`: Boolean flag
- **Actions**:
  - `login(username, password)`: Login user
  - `logout()`: Clear auth and redirect
  - `getCurrentUser()`: Fetch current user
  - `setToken(token)`: Set token manually
  - `clearError()`: Clear error state
- **Persistence**: Token stored in localStorage

#### **RoomStore** (`src/stores/roomStore.ts`)
- **State**:
  - `rooms`: Array of all rooms
  - `selectedRoom`: Currently selected room
  - `isLoading`: Request state
  - `error`: Error message
- **Actions**:
  - `fetchRooms()`: Get all rooms
  - `fetchRoom(id)`: Get single room
  - `createRoom(data)`: Create new room
  - `updateRoom(id, data)`: Update room
  - `deleteRoom(id)`: Delete room
  - `setSelectedRoom(room)`: Set selected
  - `clearError()`: Clear error

#### **TenantStore** (`src/stores/tenantStore.ts`)
- **State**:
  - `tenants`: Array of all tenants
  - `selectedTenant`: Currently selected tenant
  - `isLoading`: Request state
  - `error`: Error message
- **Actions**:
  - `fetchTenants()`: Get all tenants
  - `fetchTenant(id)`: Get single tenant
  - `createTenant(data)`: Create new tenant
  - `updateTenant(id, data)`: Update tenant
  - `deleteTenant(id)`: Delete tenant
  - `setSelectedTenant(tenant)`: Set selected
  - `clearError()`: Clear error

#### **DashboardStore** (`src/stores/dashboardStore.ts`)
- **State**:
  - `metrics`: Dashboard metrics object
  - `summary`: Dashboard summary data
  - `isLoading`: Request state
  - `error`: Error message
  - `dateRange`: Selected date range
- **Actions**:
  - `fetchMetrics(startDate?, endDate?)`: Get metrics
  - `fetchSummary()`: Get summary
  - `setDateRange(start, end)`: Set date filter
  - `clearError()`: Clear error

---

### API Service

#### **ApiClient** (`src/services/api.ts`)
- **Purpose**: Centralized HTTP communication
- **Features**:
  - Fetch-based HTTP client
  - Token management
  - Base URL configuration
  - Error handling
  - Request/response logging
- **Methods** (30+ total):
  - Auth: `login()`, `getCurrentUser()`
  - Rooms: `getRooms()`, `getRoom()`, `createRoom()`, `updateRoom()`, `deleteRoom()`
  - Tenants: `getTenants()`, `getTenant()`, `createTenant()`, `updateTenant()`, `deleteTenant()`
  - Payments: `getPayments()`, `getPayment()`, `createPayment()`, `updatePayment()`, `markPaymentAsPaid()`, `deletePayment()`
  - Expenses: `getExpenses()`, `getExpense()`, `createExpense()`, `updateExpense()`, `deleteExpense()`
  - Dashboard: `getDashboardMetrics()`, `getDashboardSummary()`
- **Type Definitions** (10+ interfaces):
  - `User`, `Room`, `Tenant`, `Payment`, `Expense`
  - `DashboardMetrics`, `DashboardSummary`, `LoginResponse`

---

## 🔄 Data Flow

```
User Action in Component
    ↓
Calls Store Action
    ↓
Store calls API Client
    ↓
API Client makes HTTP request to Backend
    ↓
Backend processes and returns response
    ↓
API Client returns typed response
    ↓
Store updates state
    ↓
Component re-renders with new data
```

---

## 🎯 Component Relationships

```
App.tsx (Router)
├── Protected Routes
│   └── Layout
│       ├── Navbar (with logout)
│       ├── Sidebar (navigation)
│       └── Page Component
│           ├── DashboardPage
│           │   └── uses DashboardStore
│           ├── RoomsPage
│           │   └── uses RoomStore
│           ├── TenantsPage
│           │   └── uses TenantStore + RoomStore
│           ├── PaymentsPage
│           │   └── Direct API calls
│           └── ExpensesPage
│               └── Direct API calls
└── Public Routes
    └── LoginPage
        └── uses AuthStore
```

---

## 🔌 Data Models

### User
```typescript
{
  id: number
  username: string
  email: string
  created_at: string
}
```

### Room
```typescript
{
  id: number
  room_number: string
  floor: number
  room_type: 'single' | 'double' | 'suite'
  monthly_rate: number
  status: 'available' | 'occupied' | 'maintenance'
  amenities?: string
  current_tenant?: Tenant
  created_at: string
  updated_at: string
}
```

### Tenant
```typescript
{
  id: number
  name: string
  phone?: string
  email?: string
  id_number?: string
  move_in_date?: string
  move_out_date?: string
  current_room_id?: number
  status: 'active' | 'inactive' | 'moved_out'
  notes?: string
  created_at: string
  updated_at: string
}
```

### Payment
```typescript
{
  id: number
  tenant_id: number
  amount: number
  due_date: string
  paid_date?: string
  status: 'pending' | 'paid' | 'overdue'
  payment_method?: string
  receipt_number?: string
  notes?: string
  created_at: string
  updated_at: string
}
```

### Expense
```typescript
{
  id: number
  date: string
  category: string
  amount: number
  description?: string
  receipt_url?: string
  created_at: string
  updated_at: string
}
```

### DashboardMetrics
```typescript
{
  total_rooms: number
  occupied_rooms: number
  available_rooms: number
  occupancy_rate: number
  total_income: number
  total_expenses: number
  net_profit: number
  overdue_count: number
  overdue_amount: number
  pending_count: number
  start_date: string
  end_date: string
}
```

---

## 🎨 Component Styling

All components use **Tailwind CSS** utility classes:

### Common Classes Used
- `bg-white`, `bg-gray-50`, `bg-blue-600` - Backgrounds
- `text-gray-900`, `text-blue-700`, `text-red-600` - Text colors
- `px-6`, `py-4` - Padding
- `rounded-lg`, `shadow` - Shapes and effects
- `hover:bg-blue-700` - Interactive states
- `flex`, `grid`, `space-y-4` - Layout

### Responsive Design
- `md:col-span-2` - Responsive columns
- `md:grid-cols-2 lg:grid-cols-3` - Responsive grids
- `overflow-x-auto` - Horizontal scrolling for tables

---

## 🚀 Using Components

### In Your Code
```typescript
import { DashboardPage } from './pages/DashboardPage'
import { useRoomStore } from './stores/roomStore'

function MyComponent() {
  const { rooms, fetchRooms } = useRoomStore()

  useEffect(() => {
    fetchRooms()
  }, [])

  return <div>{/* use rooms data */}</div>
}
```

---

## 📝 Creating New Components

### Page Component Template
```typescript
import { useState, useEffect } from 'react'
import { useStore } from '../stores/yourStore'

export function YourPage() {
  const { data, isLoading, error, fetchData } = useStore()
  const [form, setForm] = useState({})

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <h1 className="text-3xl font-bold">Page Title</h1>

      {/* Error */}
      {error && <div className="p-4 bg-red-50">{error}</div>}

      {/* Content */}
      {isLoading ? <p>Loading...</p> : <div>{/* your content */}</div>}
    </div>
  )
}
```

---

This reference guide covers all components in the frontend application!
