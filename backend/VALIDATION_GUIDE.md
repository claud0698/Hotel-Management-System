# Input Validation Guide - Phase 8 Task 8.2

**Comprehensive Input Validation for Hotel Management System API**

---

## Overview

This guide documents the comprehensive input validation implemented for all API endpoints. All validation is performed at the schema level using Pydantic validators.

---

## Validation Categories

### 1. Date Validation

#### Rules
- **Format**: ISO 8601 (YYYY-MM-DD) only
- **Check-in Date**: Cannot be in the past
- **Check-out Date**: Must be after check-in date
- **Duration**: Maximum 365 days per reservation

#### Examples
```python
# Valid
check_in_date: "2025-12-20"  # Future date
check_out_date: "2025-12-25"  # 5 days later

# Invalid
check_in_date: "2025-10-01"  # Past date
check_out_date: "2025-12-20"  # Not after check-in
check_in_date: "2026-12-20"  # 400+ days from now
```

#### Error Messages
- `Invalid date format. Expected YYYY-MM-DD`
- `Check-in date cannot be in the past`
- `Check-out date must be after check-in date`
- `Maximum stay duration is 365 days`

### 2. Numeric Validation

#### Positive Amounts (Payments, Rates)
- Must be > 0
- Maximum: 999,999,999,999 (12 digits)
- Examples: rate_per_night, total_amount, payment amount (non-adjustment)

#### Non-negative Amounts (Discounts, Deposits)
- Can be >= 0
- Maximum: 999,999,999,999
- Examples: discount_amount, deposit_amount, children count

#### Integer Ranges
- **Adults**: 1-10
- **Children**: 0-10
- **Total Occupancy**: <= 10
- **Room Type ID, Guest ID**: > 0

#### Examples
```python
# Valid
rate_per_night: 500000
discount_amount: 100000
children: 3
adults: 2

# Invalid
rate_per_night: -500000  # Negative
discount_amount: 200000  # Exceeds subtotal
children: 11  # Exceeds max
adults: 0  # Must be >= 1
```

#### Error Messages
- `Amount must be greater than 0. Got: {value}`
- `Amount cannot be negative. Got: {value}`
- `Amount exceeds maximum allowed value`
- `Total occupancy cannot exceed 10`
- `At least 1 adult is required`

### 3. String Validation

#### Username
- **Length**: 3-80 characters
- **Format**: Letters, numbers, underscore, dash only
- **No spaces or special characters**

#### Password
- **Length**: 6-200 characters
- **No format restrictions** (flexibility for security)

#### Phone Number
- **Length**: 9-20 characters
- **Format**: Digits, spaces, dash, plus, parentheses only
- **Examples**: `+1-555-0123`, `081234567890`, `(555) 123-4567`

#### Full Name
- **Length**: 2-200 characters
- **Format**: Letters, spaces, hyphens, apostrophes only
- **Examples**: `John Smith`, `Mary-Jane O'Neill`

#### Room Number
- **Length**: 1-20 characters
- **Format**: Letters, numbers, dash, period only
- **Examples**: `101`, `A-101`, `3.205`

#### Email
- **Must be valid email format** (EmailStr validation)
- **Maximum length**: Not specified (EmailStr handles)

#### Examples
```python
# Valid usernames
"john_smith", "user-123", "admin"

# Invalid usernames
"ab" (too short)
"john smith" (has space)
"john@smith" (has special char)

# Valid phone numbers
"+1-555-0123"
"081234567890"
"(555) 123-4567"

# Invalid phone numbers
"123" (too short)
"555-abcd-1234" (has letters)
"john's phone" (invalid chars)

# Valid names
"John Smith"
"Mary-Jane O'Neill"

# Invalid names
"John123" (has numbers)
"John!" (has special chars)
```

#### Error Messages
- `Username must be at least 3 characters`
- `Username can only contain letters, numbers, underscore, and dash`
- `Phone number must be at least 9 characters`
- `Invalid phone number format`
- `Full name can only contain letters, spaces, hyphens, and apostrophes`

### 4. Enumeration Validation

#### Payment Methods
Valid values:
- `cash`
- `credit_card`
- `debit_card`
- `bank_transfer`
- `e_wallet`
- `check`
- `other`

#### Payment Types
Valid values:
- `full` - Complete payment
- `downpayment` - Partial/advance payment
- `deposit` - Security deposit (refundable)
- `adjustment` - Corrections/discounts

#### Room Statuses
Valid values:
- `available` - Room is unoccupied and available
- `occupied` - Guest currently in room
- `maintenance` - Under maintenance
- `reserved` - Reserved but not checked in
- `blocked` - Blocked from bookings

#### ID Types
Valid values:
- `passport`
- `national_id`
- `driver_license`
- `visa`
- `other`

#### Examples
```python
# Valid
payment_method: "bank_transfer"
payment_type: "downpayment"
room_status: "occupied"

# Invalid
payment_method: "cryptocurrency"
payment_type: "partial"  # Must be one of valid types
room_status: "cleaning"  # Use "maintenance" instead
```

#### Error Messages
- `Invalid payment method. Must be one of: {list}`
- `Invalid payment type. Must be one of: {list}`
- `Invalid room status. Must be one of: {list}`

### 5. Business Logic Validation

#### Reservation Pricing
```python
# Rule: total_amount = subtotal - discount_amount

# Example
subtotal = 1500000
discount_amount = 100000
total_amount = 1400000  # Valid: 1500000 - 100000

total_amount = 1500000  # Invalid: doesn't match formula
```

#### Discount Validation
```python
# Rule: discount_amount <= subtotal

# Valid
subtotal: 1500000
discount_amount: 500000

# Invalid
subtotal: 1500000
discount_amount: 2000000  # Exceeds subtotal
```

#### Deposit Validation
```python
# Rule: deposit_amount <= total_amount

# Valid
total_amount: 1500000
deposit_amount: 500000

# Invalid
total_amount: 1500000
deposit_amount: 2000000  # Exceeds total
```

#### Occupancy Validation
```python
# Rule: adults >= 1, children >= 0, (adults + children) <= 10

# Valid
adults: 2
children: 3
total: 5

# Invalid
adults: 0  # No adults
children: 8
total: 8 (valid count but needs adult)

adults: 7
children: 5
total: 12  # Exceeds maximum
```

#### Payment Amount Validation
```python
# Rule for adjustment:
# amount can be positive or negative

# Rule for other types (full, downpayment, deposit):
# amount must be > 0

# Valid
payment_type: "adjustment"
amount: -50000  # Refund

payment_type: "full"
amount: 1500000  # Payment

# Invalid
payment_type: "downpayment"
amount: 0  # Must be > 0

payment_type: "full"
amount: -500000  # Cannot be negative for full payment
```

---

## Validation at Different Layers

### Field-Level Validation
Applied directly in schema Field definitions:

```python
class ReservationCreate(BaseModel):
    # Min/max length
    special_requests: Optional[str] = Field(None, max_length=500)

    # Numeric ranges
    adults: int = Field(default=1, ge=1, le=10)
    children: int = Field(default=0, ge=0, le=10)

    # Positive amounts
    rate_per_night: float = Field(..., gt=0)
    total_amount: float = Field(..., gt=0)

    # Non-negative amounts
    discount_amount: float = Field(default=0.0, ge=0)
    deposit_amount: float = Field(default=0.0, ge=0)
```

### Field Validator
Applied to individual fields:

```python
@field_validator("check_in_date")
@classmethod
def validate_date_format(cls, v: str) -> str:
    try:
        datetime.fromisoformat(v).date()
        return v
    except (ValueError, TypeError):
        raise ValueError("Invalid date format. Expected YYYY-MM-DD")

@field_validator("payment_method")
@classmethod
def validate_payment_method(cls, v: str) -> str:
    valid_methods = ["cash", "credit_card", "bank_transfer", ...]
    if v.lower() not in valid_methods:
        raise ValueError(f"Invalid payment method")
    return v.lower()
```

### Model Validator
Applied across multiple fields:

```python
@model_validator(mode="after")
def validate_date_range(self) -> "ReservationCreate":
    """Validate check-in and check-out dates"""
    check_in = datetime.fromisoformat(self.check_in_date).date()
    check_out = datetime.fromisoformat(self.check_out_date).date()

    if check_in < date.today():
        raise ValueError("Check-in date cannot be in the past")

    if check_out <= check_in:
        raise ValueError("Check-out date must be after check-in date")

    return self

@model_validator(mode="after")
def validate_pricing(self) -> "ReservationCreate":
    """Validate pricing calculations"""
    expected_total = self.subtotal - self.discount_amount
    if abs(self.total_amount - expected_total) > 0.01:
        raise ValueError("Total does not match subtotal - discount")

    return self
```

---

## API Error Responses

When validation fails, the API returns:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "check_in_date"],
      "msg": "Check-in date cannot be in the past",
      "input": "2025-10-01"
    },
    {
      "type": "greater_than",
      "loc": ["body", "rate_per_night"],
      "msg": "Input should be greater than 0",
      "input": -500000
    }
  ]
}
```

HTTP Status Code: **422 Unprocessable Entity**

---

## Validation Testing

All validations are tested in `test_reservations_api.py`, `test_auth_payments.py`, and `test_rooms_guests.py`:

### Date Validation Tests
```python
def test_past_checkin_date_rejected(self, client, user_token):
    """Test that past check-in dates are rejected"""
    payload = {
        "check_in_date": (today - timedelta(days=1)).isoformat(),
        ...
    }
    response = client.post("/api/reservations", json=payload, ...)
    assert response.status_code == 400
```

### Numeric Validation Tests
```python
def test_record_payment_negative_amount(self, client, admin_token):
    """Test that negative amounts are rejected for non-adjustment payments"""
    payload = {
        "amount": -100000,
        "payment_type": "full",  # Not adjustment
    }
    response = client.post("/api/payments", json=payload, ...)
    assert response.status_code == 400 or response.status_code == 422
```

### Payment Type Validation Tests
```python
def test_invalid_payment_type(self, client, admin_token):
    """Test that only valid payment types are accepted"""
    payload = {
        "payment_type": "invalid_type",
    }
    response = client.post("/api/payments", json=payload, ...)
    assert response.status_code == 422
```

---

## Common Validation Errors

### 1. Date Format Error
**Input**: `"2025/12/20"` (using slashes instead of dashes)
**Error**: `Invalid date format. Expected YYYY-MM-DD`
**Fix**: Use `"2025-12-20"`

### 2. Past Date Error
**Input**: `check_in_date: "2025-09-01"` (in the past)
**Error**: `Check-in date cannot be in the past`
**Fix**: Use a future date

### 3. Pricing Mismatch Error
**Input**:
```json
{
  "subtotal": 1500000,
  "discount_amount": 100000,
  "total_amount": 1500000  // Should be 1400000
}
```
**Error**: `Total amount must equal subtotal minus discount`
**Fix**: Calculate correctly: `1500000 - 100000 = 1400000`

### 4. Invalid Enumeration Error
**Input**: `payment_method: "paypal"`
**Error**: `Invalid payment method. Must be one of: cash, credit_card, ...`
**Fix**: Use one of the valid payment methods

### 5. Occupancy Error
**Input**:
```json
{
  "adults": 0,
  "children": 5
}
```
**Error**: `At least 1 adult is required`
**Fix**: Ensure `adults >= 1`

---

## Validation Best Practices

### 1. Always Validate on Input
- All API requests must pass schema validation
- Pydantic automatically validates before handler executes

### 2. Provide Clear Error Messages
- Error messages explain what went wrong and expected format
- Include examples in error messages when helpful

### 3. Use Appropriate Field Validators
- Use `Field()` constraints for simple rules (min/max)
- Use `@field_validator()` for format/pattern validation
- Use `@model_validator()` for cross-field validation

### 4. Test Edge Cases
- Minimum/maximum values
- Boundary conditions
- Invalid formats
- Missing required fields

### 5. Document Validation Rules
- Add descriptions to all fields
- Document constraints in API docs
- Include examples in schema definitions

---

## Summary

**Phase 8 Task 8.2: Complete ✅**

Implemented comprehensive input validation covering:

| Category | Coverage |
|----------|----------|
| **Date Validation** | Format, range, past date prevention |
| **Numeric Validation** | Range, positive/non-negative, maximums |
| **String Validation** | Length, format, pattern matching |
| **Enumeration** | Payment methods, types, statuses |
| **Business Logic** | Pricing, occupancy, deposit, discount |
| **Field-level** | Type, length, range constraints |
| **Model-level** | Cross-field validation, calculations |

All validations are:
- ✅ Implemented in Pydantic schemas
- ✅ Tested in comprehensive test suite
- ✅ Documented with clear error messages
- ✅ Applied consistently across all endpoints

---

**Next Phase**: Phase 8 Task 8.3 - Error Handling & Logging
