# 🏨 Deposit System Implementation Guide

**Last Updated**: November 8, 2025
**Version**: 1.0
**Status**: Backend Complete, Frontend TODO

---

## Overview

The Hotel Management System includes a **security deposit system** that allows hotel staff to collect deposits at booking/check-in and settle them at checkout. Deposits are **fully refundable**.

---

## Key Concepts

### What is a Deposit?
A **security deposit** is an optional upfront payment held as collateral. It can be applied to:
- Room damages
- Extra charges not pre-authorized
- Remaining balance if guest hasn't paid in full

### Default Behavior
- **Default deposit**: 0% (no deposit required)
- **Can be customized**: Per reservation, admin can set any amount
- **Always refundable**: 100% refunded if no charges incurred
- **Applied at checkout**: Automatically deducted from balance owed

---

## Backend API Reference

### 1. Creating a Reservation with Deposit

**Endpoint**: `POST /api/reservations`

```json
{
  "guest_id": 1,
  "room_type_id": 2,
  "check_in_date": "2025-12-20",
  "check_out_date": "2025-12-23",
  "adults": 2,
  "children": 0,
  "rate_per_night": 500000,
  "subtotal": 1500000,
  "discount_amount": 0,
  "total_amount": 1500000,
  "deposit_amount": 0,  // ← Default: 0 (no deposit)
  "special_requests": "Late check-in"
}
```

**Response**:
```json
{
  "id": 1,
  "confirmation_number": "ABC123XYZ",
  "total_amount": 1500000,
  "deposit_amount": 0,
  "status": "confirmed",
  "created_at": "2025-11-08T10:00:00"
}
```

### 2. Check Balance (Before Check-Out)

**Endpoint**: `GET /api/reservations/{id}/balance`

**Response**:
```json
{
  "reservation_id": 1,
  "confirmation_number": "ABC123XYZ",
  "guest_name": "John Doe",
  "total_amount": 1500000,
  "total_paid": 800000,
  "balance": 700000,           // ← Amount still owed
  "deposit_amount": 500000,     // ← Deposit being held
  "deposit_returned_at": null,  // ← null until checkout
  "final_balance_after_deposit": 200000,  // ← Balance after deposit applied
  "payment_status": "partial_paid",
  "reservation_status": "checked_in"
}
```

### 3. Check-Out with Deposit Settlement

**Endpoint**: `POST /api/reservations/{id}/check-out`

**Response**:
```json
{
  "message": "Guest checked out successfully",
  "reservation_id": 1,
  "confirmation_number": "ABC123XYZ",
  "guest_name": "John Doe",
  "checked_out_at": "2025-12-23T11:00:00",
  "total_amount": 1500000,
  "total_paid": 800000,
  "balance_before_deposit": 700000,
  "deposit_settlement": {
    "deposit_held": 500000,
    "balance_owed": 700000,
    "to_refund": 0,
    "settlement_note": "Deposit 500000 applied. Guest still owes 200000"
  },
  "final_balance_owed": 200000,  // ← What guest still needs to pay
  "deposit_returned_at": "2025-12-23T11:00:00"
}
```

---

## Deposit Settlement Scenarios

### Scenario 1: Full Payment + Deposit Return
```
Reservation total: 1,500,000
Deposit held:        500,000
Guest paid:        1,500,000

At checkout:
- Balance owed: 0
- Deposit: Return full 500,000
- Guest owes: 0
```

### Scenario 2: Partial Payment + Deposit Applied
```
Reservation total: 1,500,000
Deposit held:        500,000
Guest paid:          800,000

At checkout:
- Balance owed: 700,000
- Apply deposit: 500,000
- Remaining: 200,000
- Refund deposit: 0
- Guest owes: 200,000
```

### Scenario 3: Overpayment + Excess Refund
```
Reservation total: 1,500,000
Deposit held:        500,000
Guest paid:        2,000,000

At checkout:
- Balance owed: -500,000 (overpaid)
- Deposit: Return full 500,000
- Excess refund: 500,000
- Total refund: 1,000,000
- Guest owes: 0
```

---

## Frontend Implementation Tasks

### Task 1: Reservation Form - Deposit Input
**File**: `frontend/src/pages/NewReservationPage.tsx`

**Requirements**:
- [ ] Add "Deposit Amount" field to reservation form
- [ ] Default value: 0 (calculate: total_amount × 0%)
- [ ] Allow custom override (admin can change)
- [ ] Display deposit amount in currency
- [ ] Show deposit in summary before submitting
- [ ] After successful creation, **reset deposit to 0** for next reservation

**UI Pattern**:
```
Deposit Amount: [_________] (Default: 0)
                ✓ Calculate from total
                ✓ Custom amount (optional)

Summary:
  Total: 1,500,000
  Deposit: 0
  Payment due on checkout: 1,500,000
```

---

### Task 2: Check-In Screen - Display Deposit
**File**: `frontend/src/pages/CheckInPage.tsx`

**Requirements**:
- [ ] Display "Deposit Held" on check-in confirmation
- [ ] Show deposit amount prominently
- [ ] Explain what happens at checkout
- [ ] Link to balance inquiry

**UI Pattern**:
```
✓ Check-In Successful

Guest: John Doe
Room: 301 (Deluxe)
Check-In: 2025-12-20
Check-Out: 2025-12-23

💰 Security Deposit Held: 500,000
   (Refundable at checkout)

Total to Collect:
  - Room charges: 1,500,000
  - Less deposit: -500,000
  ─────────────────────
  Due now: 1,000,000
```

---

### Task 3: Balance Inquiry - Deposit Details
**File**: `frontend/src/components/BalanceInquiry.tsx`

**Requirements**:
- [ ] Call GET /api/reservations/{id}/balance
- [ ] Display deposit_amount
- [ ] Display final_balance_after_deposit
- [ ] Show deposit_returned_at (if already checked out)
- [ ] Color-code based on settlement status

**UI Pattern**:
```
Balance Inquiry
━━━━━━━━━━━━━━━━━━
Reservation: ABC123XYZ
Guest: John Doe

Charges:
  Total: 1,500,000
  Paid: 800,000
  Balance Owed: 700,000

Security Deposit:
  Amount Held: 500,000
  Status: Not yet returned

Final Balance (after deposit):
  Guest Owes: 200,000
```

---

### Task 4: Check-Out Screen - Deposit Settlement
**File**: `frontend/src/pages/CheckOutPage.tsx`

**Requirements**:
- [ ] Display deposit_settlement details from checkout response
- [ ] Show settlement calculation step-by-step
- [ ] Show "settlement_note" with clear explanation
- [ ] Display final_balance_owed
- [ ] Show refund amount if applicable
- [ ] Print settlement details for guest receipt

**UI Pattern**:
```
Check-Out Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Guest: John Doe
Room: 301

Charges Summary:
  Total Room Cost: 1,500,000
  Paid to Date: 800,000
  Balance Owed: 700,000

Deposit Settlement:
  ├─ Deposit Held: 500,000
  ├─ Applied to balance: 500,000
  ├─ Remaining owed: 200,000
  └─ Note: "Deposit applied. Guest still owes 200,000"

Final Settlement:
  💰 Guest Still Owes: 200,000

  OR if fully paid:
  💰 Refund to Guest: 500,000
```

---

### Task 5: Balance Calculation Helper
**File**: `frontend/src/utils/depositCalculations.ts`

**Functions to implement**:
```typescript
// Calculate deposit amount
function calculateDepositAmount(
  totalAmount: number,
  depositPercentage: number = 0
): number {
  return totalAmount * (depositPercentage / 100);
}

// Calculate final balance after deposit
function calculateFinalBalance(
  totalAmount: number,
  totalPaid: number,
  depositAmount: number
): number {
  const balance = totalAmount - totalPaid;
  return Math.max(0, balance - depositAmount);
}

// Determine if deposit should be refunded
function getDepositRefundAmount(
  balance: number,
  depositAmount: number
): number {
  if (balance <= 0) {
    return depositAmount;
  }
  if (balance < depositAmount) {
    return depositAmount - balance;
  }
  return 0;
}

// Generate settlement note
function generateSettlementNote(
  balance: number,
  depositAmount: number
): string {
  if (balance <= 0) {
    return `All charges paid. Returning full deposit of ${depositAmount}`;
  }
  if (depositAmount >= balance) {
    const refund = depositAmount - balance;
    return `Deposit of ${depositAmount} used to cover ${balance} balance. Refund ${refund}`;
  }
  return `Deposit ${depositAmount} applied. Guest still owes ${balance - depositAmount}`;
}
```

---

## Default Deposit Policy

### Rule 1: Always Start with 0%
```
When creating a new reservation:
- Set deposit_amount = 0 by default
- Allow staff to override if needed
- After override, reset to 0 for next reservation
```

### Rule 2: Customizable Per Reservation
```
Admin can set deposits for:
- VIP guests: 0% (trusted)
- First-time guests: 10-20%
- Groups/Events: 25-50%
- Standard guests: 0% (default)
```

### Rule 3: Fully Refundable
```
Deposits are ALWAYS refundable:
- If guest pays in full: return 100%
- If guest has balance: apply to balance, return excess
- At checkout: automatically settle and process refund
```

---

## Form Implementation Example

### Reservation Form (React/TypeScript)
```typescript
export function NewReservationForm() {
  const [formData, setFormData] = useState({
    guest_id: '',
    room_type_id: '',
    check_in_date: '',
    check_out_date: '',
    total_amount: 0,
    deposit_amount: 0,  // ← Always defaults to 0
  });

  const handleTotalChange = (newTotal: number) => {
    // When total changes, recalculate with default (0%)
    setFormData({
      ...formData,
      total_amount: newTotal,
      deposit_amount: 0,  // ← Reset to default
    });
  };

  const handleDepositOverride = (customDeposit: number) => {
    setFormData({
      ...formData,
      deposit_amount: customDeposit,
    });
  };

  const handleNextReservation = () => {
    // After submission, reset deposit to 0 for next form
    setFormData({
      ...formData,
      deposit_amount: 0,  // ← Always reset to default
    });
  };

  return (
    <form>
      <input
        type="number"
        value={formData.total_amount}
        onChange={(e) => handleTotalChange(Number(e.target.value))}
        placeholder="Total amount"
      />

      <input
        type="number"
        value={formData.deposit_amount}
        onChange={(e) => handleDepositOverride(Number(e.target.value))}
        placeholder="Deposit (defaults to 0)"
      />

      <summary>
        Total: {formData.total_amount}
        Deposit: {formData.deposit_amount}
        Due on checkout: {formData.total_amount}
      </summary>

      <button type="submit">Create Reservation</button>
    </form>
  );
}
```

---

## Testing Checklist

### Frontend Tests
- [ ] Deposit defaults to 0 on new reservation form
- [ ] Can override default deposit amount
- [ ] Deposit resets to 0 after form submission
- [ ] Check-in shows deposit held
- [ ] Balance inquiry shows deposit and final balance
- [ ] Check-out displays settlement calculation
- [ ] Refund amount calculated correctly
- [ ] Settlement note is clear and accurate

### Integration Tests
- [ ] Create reservation (0% deposit by default)
- [ ] Check-in shows deposit held correctly
- [ ] Check balance shows correct final_balance_after_deposit
- [ ] Check-out processes deposit and calculates refunds
- [ ] Test scenarios: fully paid, partial paid, overpaid

---

## Common Issues & Solutions

### Issue 1: Deposit Not Resetting to Default
**Solution**: Always set `deposit_amount = 0` in form reset/initialization

### Issue 2: Incorrect Settlement Calculation
**Solution**: Use backend `final_balance_after_deposit` value, don't calculate client-side

### Issue 3: Confusing Refund Display
**Solution**: Show clear settlement note from backend `deposit_settlement.settlement_note`

### Issue 4: Deposit Not Applied at Checkout
**Solution**: Ensure checkout endpoint is called with `POST /api/reservations/{id}/check-out`

---

## API Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/reservations` | POST | Create with deposit_amount |
| `/api/reservations/{id}/balance` | GET | Check deposit & final balance |
| `/api/reservations/{id}/check-in` | POST | Display deposit info |
| `/api/reservations/{id}/check-out` | POST | Settle deposit & calculate refund |

---

## Related Documentation

- [README.md](../README.md#deposit-management) - Deposit overview
- [BACKEND_TASKS.md](./planning/BACKEND_TASKS.md#deposit-system) - Backend implementation
- API Docs: `/api/docs` - Live API documentation

---

## Next Steps for Frontend Team

1. **Review this guide** - Understand deposit system completely
2. **Create tasks** from "Frontend Implementation Tasks" section
3. **Implement in order**:
   - Task 1: Reservation form
   - Task 2: Check-in display
   - Task 3: Balance inquiry
   - Task 4: Check-out settlement
   - Task 5: Helper utilities
4. **Test with backend** - Verify all scenarios work correctly
5. **Document in code** - Add comments explaining deposit logic

---

**Status**: 🟢 Backend Complete | 🟡 Frontend TODO

**Questions?** Check API docs at `http://localhost:8000/api/docs`
