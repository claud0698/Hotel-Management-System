# Remaining Frontend Tasks - Implementation Guide

## Overview
This document provides step-by-step guidance for completing the remaining frontend pages. All infrastructure is in place; these are enhancements to existing pages.

---

## 1. Enhanced Dashboard Page

**Current File:** `frontend/src/pages/DashboardPage.tsx`
**Status:** Partial (needs charts)

### Implementation Tasks

#### A. Add Chart Libraries
```bash
npm install recharts date-fns
```

#### B. Update Dashboard Page
```typescript
// Key additions needed:
import { LineChart, BarChart, PieChart } from 'recharts'
import { startOfMonth, endOfMonth, format } from 'date-fns'

// Components to add:
1. Occupancy Rate Chart (BarChart)
   - X: Days of month
   - Y: Occupied rooms count
   - Color: Green for high occupancy

2. Revenue Trend (LineChart)
   - X: Days of month
   - Y: Daily revenue
   - Show vs previous month comparison

3. Payment Status Pie (PieChart)
   - Segments: Paid, Pending, Overdue
   - Colors: Green, Yellow, Red

4. Quick Stats Grid
   - Occupancy Rate %
   - Check-ins Today
   - Check-outs Today
   - Revenue Today
   - Outstanding Balance
```

#### C. Features to Implement
- [ ] Month/date range picker
- [ ] Real-time metric updates
- [ ] Export dashboard data (PDF/CSV)
- [ ] Customizable widgets
- [ ] Performance metrics

---

## 2. Enhanced Rooms Page

**Current File:** `frontend/src/pages/RoomsPage.tsx`
**Status:** Partial (needs room images)

### Implementation Tasks

#### A. Add Image Handling
```typescript
// Types needed in api.ts (already defined):
interface RoomImage {
  id: number
  room_id: number
  image_type: 'main_photo' | 'bedroom' | 'bathroom' | 'living_area' | 'amenities' | 'other'
  image_path: string
  // ... other fields
}

// API methods needed:
async uploadRoomImage(roomId: number, file: File, imageType: string): Promise<RoomImage>
async deleteRoomImage(imageId: number): Promise<{ message: string }>
```

#### B. Room Card Enhancement
```typescript
// Current: Text-based room info
// Needed: Visual room cards with:
1. Room image carousel
   - Main photo prominent
   - Thumbnail strips
   - Upload new photo button

2. Room details
   - Room number
   - Floor
   - Room type
   - Current status badge (available/occupied/out_of_order)
   - Custom rate (if differs from type rate)

3. Quick actions
   - View details modal
   - Edit room
   - Change status
   - Upload images
   - Delete (with confirmation)
```

#### C. Features to Implement
- [ ] File upload with preview
- [ ] Image drag-and-drop
- [ ] Image cropping tool
- [ ] Room status timeline
- [ ] Maintenance history
- [ ] Occupancy calendar

---

## 3. Enhanced Payments Page

**Current File:** `frontend/src/pages/PaymentsPage.tsx`
**Status:** Partial (basic CRUD only)

### Implementation Tasks

#### A. Payment Flow Implementation
```typescript
// Business logic:
1. Payment Creation
   - Select reservation
   - Fetch current balance
   - Enter payment amount
   - Select payment method (cash, card, transfer, check, other)
   - Add payment type (full, downpayment, deposit, adjustment)

2. Payment Recording
   - Generate receipt number
   - Attach receipt/proof
   - Update reservation balance
   - Automatic status change (if balance = 0)

3. Settlement Logic
   - Calculate remaining balance
   - Show deposit settlement options
   - Track payment history per reservation
```

#### B. Payment Receipt System
```typescript
// Features needed:
1. Receipt Generation
   - Template with hotel info
   - Guest details
   - Payment details
   - Amount in words
   - Signature line

2. Receipt Storage
   - API: Upload receipt image/PDF
   - Local preview
   - Download option
   - Email receipt to guest

3. Attachment Management (PaymentAttachment type already defined)
   - Support multiple file types (receipt, invoice, proof)
   - File upload validation
   - Storage location (local/S3/GCS)
```

#### C. Features to Implement
- [ ] Deposit settlement workflow
- [ ] Payment history per reservation
- [ ] Receipt printing
- [ ] Payment reminders/due dates
- [ ] Accounting reports
- [ ] Payment reconciliation

---

## 4. Additional Enhancements

### A. Error Toast Notifications
```bash
npm install sonner
# or
npm install react-toastify
```

Usage:
```typescript
import { toast } from 'sonner'

// Replace Alert components in pages with:
try {
  await createReservation(data)
  toast.success('Reservation created successfully')
} catch (error) {
  toast.error(error.message)
}
```

### B. Form Validation Library
```bash
npm install react-hook-form zod
```

Usage:
```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const schema = z.object({
  full_name: z.string().min(1, 'Name required'),
  id_number: z.string().min(1, 'ID required'),
})

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
})
```

### C. Loading States for Pages
Implement consistent loading patterns:
```typescript
// Pattern:
if (isLoading && !data) return <PageSkeleton />
if (isLoading) return <LoadingSpinner />

// Create skeleton components:
- DashboardSkeleton
- RoomsSkeleton
- ReservationsSkeleton
- GuestsSkeleton
- PaymentsSkeleton
```

### D. Internationalization (i18n) Completion
Already setup with i18next. Add translations for:
- New pages (Reservations, Guests, Payments enhancements)
- Modal titles and buttons
- Validation messages
- Status labels
- Payment types

Files to update:
```
locales/
├── en.json
└── id.json
```

---

## Implementation Priority

### High Priority (Core Functionality)
1. **Enhanced Dashboard** - Key business metrics
2. **Enhanced Payments** - Revenue tracking
3. **Error Notifications** - Better UX
4. **Form Validation** - Data integrity

### Medium Priority (Polish)
5. **Enhanced Rooms** - Visual improvements
6. **Receipt Generation** - Accounting
7. **Loading Skeletons** - Professional feel

### Low Priority (Nice to Have)
8. **i18n Completion** - Multi-language
9. **Export Features** - Reporting
10. **Advanced Filtering** - Search refinement

---

## Code Examples

### Example 1: Implement Payment Amount Validation
```typescript
// paymentStore.ts - add method
getReservationBalance: async (reservationId: number) => {
  try {
    const response = await apiClient.getReservationBalance(reservationId)
    return response // { balance, total_amount, total_paid }
  } catch (error) {
    // handle error
  }
}

// PaymentsPage.tsx - in form
const [reservationBalance, setReservationBalance] = useState(0)

const handleReservationChange = async (reservationId: string) => {
  const balance = await getReservationBalance(parseInt(reservationId))
  setReservationBalance(balance.balance)
}

// Validate payment amount
const isValidAmount = paymentAmount > 0 && paymentAmount <= reservationBalance
```

### Example 2: Add Chart to Dashboard
```typescript
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

// In DashboardPage component
const occupancyData = [
  { date: '2025-11-01', occupied: 15, available: 10 },
  { date: '2025-11-02', occupied: 18, available: 7 },
  // ... generate from metrics
]

return (
  <Card title="Occupancy Trend">
    <BarChart width={500} height={300} data={occupancyData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="occupied" fill="#10b981" />
      <Bar dataKey="available" fill="#ef4444" />
    </BarChart>
  </Card>
)
```

### Example 3: File Upload for Room Images
```typescript
const handleImageUpload = async (file: File, imageType: string) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('image_type', imageType)

  try {
    const response = await fetch(
      `http://localhost:8001/api/rooms/${roomId}/images`,
      {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      }
    )
    const data = await response.json()
    toast.success('Image uploaded')
  } catch (error) {
    toast.error('Upload failed')
  }
}
```

---

## Testing Checklist

### Dashboard
- [ ] Metrics calculate correctly
- [ ] Charts update with data
- [ ] Date picker filters work
- [ ] Responsive on mobile
- [ ] No 404 errors in console

### Rooms
- [ ] Images upload successfully
- [ ] Images display in carousel
- [ ] Room status changes work
- [ ] Delete with confirmation
- [ ] Mobile responsive

### Payments
- [ ] Balance calculates correctly
- [ ] Payment types selectable
- [ ] Receipt uploads work
- [ ] Email receipt functionality
- [ ] Accounting reports accurate

---

## Resources & References

### Frontend Libraries
- Recharts: https://recharts.org/
- React Hook Form: https://react-hook-form.com/
- Zod Validation: https://zod.dev/
- Sonner Toast: https://sonner.emilkowal.ski/
- date-fns: https://date-fns.org/

### Related Documentation
- `FRONTEND_DEVELOPMENT.md` - Current state
- `API_QUICK_REFERENCE.md` - Backend endpoints
- `BACKEND_ARCHITECTURE_SUMMARY.md` - Data models

---

## Support Commands

```bash
# Install additional dependencies
npm install recharts date-fns react-hook-form zod sonner

# Check for TypeScript errors
npx tsc --noEmit

# Lint code
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

---

**Last Updated:** November 8, 2025
**Estimated Completion:** 1-2 weeks (with 1-2 developers)
**Difficulty:** Medium (All infrastructure in place)
