# 🚀 Quick Start Guide - Kos Management Dashboard

## Start Everything in 3 Steps

### Step 1: Terminal 1 - Start Backend
```bash
cd backend
python app.py
```
✅ Backend runs on `http://localhost:5000`

### Step 2: Terminal 2 - Start Frontend
```bash
cd frontend
npm install  # Only needed first time
npm run dev
```
✅ Frontend runs on `http://localhost:8002`

### Step 3: Open Browser
Navigate to: **http://localhost:8002**

## Login
- **Username**: admin
- **Password**: password

---

## 🎯 What You Can Do

### Dashboard
View all key metrics in one place:
- Occupancy rate
- Monthly revenue & expenses
- Net profit
- Payment status
- Recent activity

### Rooms
- Create new rooms with monthly rates
- View all rooms with status
- Edit room details
- Delete rooms

### Tenants
- Add tenant information
- Assign tenants to rooms
- Track move-in dates
- Update tenant status

### Payments
- Record rent payments
- Select tenant and number of months (1, 2, 3, etc.)
- Track payment status
- Filter by status

### Expenses
- Record business expenses
- Categorize (Utilities, Maintenance, Supplies, Cleaning, Other)
- Track amounts and dates
- View total expenses

---

## 📁 Project Files

**Key Frontend Files** (in `/frontend/src/`)
```
pages/          # All page components
├── LoginPage.tsx
├── DashboardPage.tsx
├── RoomsPage.tsx
├── TenantsPage.tsx
├── PaymentsPage.tsx
└── ExpensesPage.tsx

services/       # API communication
└── api.ts

stores/         # State management
├── authStore.ts
├── roomStore.ts
├── tenantStore.ts
└── dashboardStore.ts

components/     # Reusable components
├── Navbar.tsx
├── Sidebar.tsx
└── Layout.tsx

App.tsx         # Main app with routing
```

**Backend Running On**: `localhost:5000`
- API Docs: `http://localhost:5000/api/docs`
- Health Check: `http://localhost:5000/health`

---

## 🔍 Example Workflow

1. **Login** → Use admin/password
2. **Create Rooms** → Add 2-3 rooms with monthly rates
3. **Add Tenants** → Create 2-3 tenants and assign to rooms
4. **Record Payments** → Select tenant, enter 1 month, click "Record Payment"
5. **Add Expenses** → Record some property expenses
6. **View Dashboard** → See all metrics update in real-time

---

## ⚙️ Configuration

### Frontend Port (Change from 8002)
Edit `frontend/vite.config.ts`:
```typescript
server: {
  port: 3000,  // Change to any port
}
```

### Backend URL (If on different server)
Create `frontend/.env`:
```env
VITE_API_URL=http://your-backend-url:5000/api
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot connect to API" | Make sure backend is running on port 5000 |
| "Port 8002 already in use" | Run `npm run dev -- --port 3000` |
| "npm install errors" | Delete `node_modules`, run `npm install` again |
| "Login not working" | Use credentials: admin / password |
| "Styles look broken" | Clear browser cache (Ctrl+Shift+Delete) |

---

## 📚 Documentation

- **Full Setup Guide**: See `frontend/SETUP.md`
- **Feature Details**: See `FRONTEND_SUMMARY.md`
- **Project Overview**: See `PROJECT_OVERVIEW.md`
- **Requirements**: See `PRD.md`

---

## 🎓 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python FastAPI |
| Frontend | React 19 + TypeScript |
| State Mgmt | Zustand |
| Styling | Tailwind CSS |
| Routing | React Router v7 |
| Build | Vite |

---

## ✨ Key Features

✅ Authentication (with login page)
✅ Dashboard with real-time metrics
✅ Room management (CRUD)
✅ Tenant management (CRUD)
✅ Payment tracking (with duration-based entry)
✅ Expense tracking (with categories)
✅ Responsive design (mobile, tablet, desktop)
✅ Color-coded status indicators
✅ Protected routes
✅ Token-based authentication

---

## 🚀 Next Steps

1. **Test the application** - Try all features
2. **Add sample data** - Create a few rooms and tenants
3. **Check metrics** - Verify dashboard calculations
4. **Review code** - Explore the implementation
5. **Customize** - Modify colors, add features, etc.

---

## 💡 Tips

- Use the sidebar to navigate between features
- Click emoji icons for quick visual reference
- Status badges show at a glance (green=good, yellow=warning, red=alert)
- All forms have input validation
- Deletion requires confirmation
- Recent activity automatically updates

---

**Happy Managing!** 🏠
