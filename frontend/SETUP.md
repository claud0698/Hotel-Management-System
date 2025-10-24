# Kos Management Dashboard - Frontend Setup Guide

## Overview

This is a React + TypeScript frontend application for the Kos Management Dashboard. It provides a user-friendly interface for managing property rooms, tenants, payments, and expenses.

### Tech Stack
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool (lightning-fast)
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Router** - Client-side routing
- **Fetch API** - HTTP client

## Prerequisites

- Node.js 18+ and npm/yarn
- Backend server running (see backend README)

## Installation

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Setup

Create a `.env` file (or copy from `.env.example`):

```bash
cp .env.example .env
```

Then edit `.env` to match your backend URL:

```env
VITE_API_URL=http://localhost:5000/api
```

If your backend is on a different port or server, update the URL accordingly.

### 3. Start Development Server

```bash
npm run dev
```

The app will start at `http://localhost:5173` (Vite's default)

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Navbar.tsx      # Top navigation bar
│   ├── Sidebar.tsx     # Left sidebar navigation
│   └── Layout.tsx      # Main layout wrapper
├── pages/              # Page components (full page views)
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── RoomsPage.tsx
│   ├── TenantsPage.tsx
│   ├── PaymentsPage.tsx
│   └── ExpensesPage.tsx
├── services/           # API communication
│   └── api.ts          # API client with all endpoints
├── stores/             # Zustand state management
│   ├── authStore.ts    # Authentication state
│   ├── roomStore.ts    # Room data state
│   ├── tenantStore.ts  # Tenant data state
│   └── dashboardStore.ts # Dashboard metrics state
├── App.tsx             # Main app with routing
├── index.css           # Global styles + Tailwind
└── main.tsx            # App entry point
```

## Key Features

### 🔐 Authentication
- Login with username/password
- Token-based authentication (stored in localStorage)
- Protected routes (redirects to login if not authenticated)
- Demo credentials: `admin` / `password`

### 🏘️ Room Management
- View all rooms with status (available, occupied, maintenance)
- Create new rooms with details (room number, floor, type, monthly rate)
- Edit room information
- Delete rooms
- Visual status indicators

### 👥 Tenant Management
- Add new tenants with full information
- Assign tenants to rooms
- Track move-in dates
- Update tenant status (active, inactive, moved out)
- Edit and delete tenants
- View tenant list with filters

### 💰 Payment Tracking
- Record monthly rent payments
- Support for multiple months payment (with automatic date calculation)
- Track payment status (paid, pending, overdue)
- Filter payments by status
- Simple payment method tracking (cash, transfer, etc.)

### 💸 Expense Tracking
- Log business expenses by category
- Categories: Utilities, Maintenance, Supplies, Cleaning, Other
- Edit and delete expenses
- View total expenses
- Track with descriptions and dates

### 📊 Dashboard
- Key metrics cards:
  - Occupancy rate with color coding
  - Monthly revenue
  - Monthly expenses breakdown
  - Net profit/loss
- Room status summary
- Payment status alerts
- Recent activity (payments and expenses)
- Date range filtering

## Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
```

## API Integration

All API calls go through `src/services/api.ts`. The API client handles:
- Base URL configuration
- Authentication token management
- Request/response formatting
- Error handling
- Type safety with TypeScript interfaces

### Using the API Client

```typescript
import { apiClient } from '@/services/api';

// Rooms
const rooms = await apiClient.getRooms();
const room = await apiClient.getRoom(1);
await apiClient.createRoom(roomData);

// Tenants
const tenants = await apiClient.getTenants();
await apiClient.createTenant(tenantData);

// Payments
const payments = await apiClient.getPayments();
await apiClient.createPayment(paymentData);

// Expenses
const expenses = await apiClient.getExpenses();
await apiClient.createExpense(expenseData);

// Dashboard
const metrics = await apiClient.getDashboardMetrics();
const summary = await apiClient.getDashboardSummary();
```

## State Management with Zustand

Each feature has a dedicated Zustand store:

```typescript
import { useAuthStore } from '@/stores/authStore';
import { useRoomStore } from '@/stores/roomStore';
import { useTenantStore } from '@/stores/tenantStore';
import { useDashboardStore } from '@/stores/dashboardStore';

// Use in components
const { user, login, logout } = useAuthStore();
const { rooms, fetchRooms, createRoom } = useRoomStore();
```

## Styling with Tailwind CSS

The project uses Tailwind CSS for styling. Custom components are defined in `src/index.css`:

```css
.btn-primary    /* Blue button */
.btn-secondary  /* Gray button */
.btn-danger     /* Red button */
.card           /* Card container */
.input          /* Form input */
.label          /* Form label */
```

All pages use Tailwind utility classes for responsive, modern design.

## Troubleshooting

### "Cannot connect to API"
- Check that backend is running on `localhost:5000`
- Verify `VITE_API_URL` in `.env` matches backend address
- Check browser console for CORS errors

### "Login not working"
- Backend authentication is currently in demo mode (hardcoded credentials)
- Demo username: `admin`
- Demo password: `password`
- Backend uses simplified token validation

### "Port 5173 already in use"
```bash
# Use a different port
npm run dev -- --port 3000
```

### "Styles not loading"
- Run `npm install` to ensure all dependencies installed
- Delete `node_modules` and `package-lock.json`, then reinstall
- Ensure Tailwind CSS is properly configured

## Building for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

Deploy the `dist` folder to your hosting service (Vercel, Netlify, etc.)

## Environment Variables

Create a `.env.production` file for production builds:

```env
VITE_API_URL=https://your-backend-api.com/api
VITE_APP_ENV=production
```

## Performance Optimizations

- Lazy loading of routes
- Memoization where needed
- Efficient state updates with Zustand
- Image optimization (emojis used instead of images)
- Minimal dependencies

## Future Enhancements

- [ ] Data export to CSV/PDF
- [ ] Advanced charts and analytics
- [ ] Room occupancy calendar view
- [ ] Payment reminders
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Mobile app (React Native)

## Support

For issues or questions:
1. Check the browser console for error messages
2. Verify backend is running correctly
3. Check network tab in DevTools for failed API calls
4. Review backend logs for error details

## Contributing

When adding new features:
1. Create components in `src/components/` or pages in `src/pages/`
2. Use TypeScript for type safety
3. Use Tailwind CSS for styling
4. Update Zustand stores for state management
5. Add API methods to `src/services/api.ts`
6. Test thoroughly before committing

## License

Private project for Kos Management Dashboard
