"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ============== AUTH SCHEMAS ==============

class UserCreate(BaseModel):
    """User creation schema"""
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=4)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "claudio",
                "password": "secure123"
            }
        }


class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=80)
    password: Optional[str] = Field(None, min_length=4)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "claudio_updated",
                "password": "newsecure123"
            }
        }


class UserRegister(BaseModel):
    """User registration schema (deprecated - use UserCreate)"""
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=4)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "claudio",
                "password": "secure123"
            }
        }


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "claudio",
                "password": "secure123"
            }
        }


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "username": "claudio",
                    "created_at": "2024-10-24T00:00:00"
                }
            }
        }


# ============== ROOM SCHEMAS ==============

class RoomCreate(BaseModel):
    """Room creation schema"""
    room_number: str = Field(..., max_length=20)
    floor: int = Field(default=2, ge=1, le=2)  # Floor 2 = A (Atas), Floor 1 = B (Bawah)
    room_type: str = Field(default="single", max_length=50)
    monthly_rate: float = Field(..., gt=0)
    status: Optional[str] = Field(default="available", max_length=20)
    amenities: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "room_number": "A1",
                "floor": 2,
                "room_type": "single",
                "monthly_rate": 1500000,
                "status": "available",
                "amenities": "WiFi, AC, TV"
            }
        }


class RoomUpdate(BaseModel):
    """Room update schema"""
    room_number: Optional[str] = None
    floor: Optional[int] = Field(None, ge=1, le=2)  # Floor 2 = A (Atas), Floor 1 = B (Bawah)
    room_type: Optional[str] = None
    monthly_rate: Optional[float] = None
    status: Optional[str] = None
    amenities: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "floor": 1,
                "status": "occupied",
                "amenities": "WiFi, AC"
            }
        }


class RoomResponse(BaseModel):
    """Room response schema"""
    id: int
    room_number: str
    floor: int
    room_type: str
    monthly_rate: float
    status: str
    amenities: Optional[str] = None
    current_tenant: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "room_number": "401",
                "floor": 4,
                "room_type": "single",
                "monthly_rate": 1500000,
                "status": "available",
                "amenities": "WiFi, AC",
                "current_tenant": None,
                "created_at": "2024-10-24T00:00:00",
                "updated_at": "2024-10-24T00:00:00"
            }
        }


# ============== TENANT SCHEMAS ==============

class TenantCreate(BaseModel):
    """Tenant creation schema"""
    name: str = Field(..., max_length=120)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    id_number: Optional[str] = Field(None, max_length=50)
    move_in_date: Optional[str] = None
    current_room_id: Optional[int] = None
    status: Optional[str] = Field(default="active", max_length=20)
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Budi Santoso",
                "phone": "08123456789",
                "email": "budi@example.com",
                "id_number": "1234567890123456",
                "move_in_date": "2024-10-24T00:00:00",
                "current_room_id": 1,
                "status": "active"
            }
        }


class TenantUpdate(BaseModel):
    """Tenant update schema"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    id_number: Optional[str] = None
    move_in_date: Optional[str] = None
    current_room_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "moved_out"
            }
        }


class TenantResponse(BaseModel):
    """Tenant response schema"""
    id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    id_number: Optional[str] = None
    move_in_date: Optional[str] = None
    move_out_date: Optional[str] = None
    current_room_id: Optional[int] = None
    status: str
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# ============== PAYMENT SCHEMAS ==============

class PaymentCreate(BaseModel):
    """Payment creation schema"""
    tenant_id: int
    amount: float = Field(..., gt=0)
    due_date: str
    status: Optional[str] = Field(default="pending", max_length=20)
    payment_method: Optional[str] = None
    receipt_number: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": 1,
                "amount": 1500000,
                "due_date": "2024-11-24T00:00:00",
                "status": "pending",
                "payment_method": "transfer",
                "receipt_number": "RCP001"
            }
        }


class PaymentUpdate(BaseModel):
    """Payment update schema"""
    amount: Optional[float] = None
    due_date: Optional[str] = None
    status: Optional[str] = None
    payment_method: Optional[str] = None
    receipt_number: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "paid",
                "payment_method": "cash"
            }
        }


class PaymentMarkPaid(BaseModel):
    """Mark payment as paid schema"""
    payment_method: Optional[str] = None
    receipt_number: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "payment_method": "transfer",
                "receipt_number": "TRF123456"
            }
        }


class ManualPaymentCreate(BaseModel):
    """Manual payment creation schema - admin inputs period, system calculates amount and dates"""
    tenant_id: int
    period_months: int = Field(..., ge=1, le=12)  # 1-12 months
    status: Optional[str] = Field(default="pending", max_length=20)  # pending, paid, etc
    payment_method: Optional[str] = None
    receipt_number: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": 1,
                "period_months": 2,
                "status": "pending",
                "payment_method": "cash",
                "notes": "Payment for 2 months"
            }
        }


class PaymentResponse(BaseModel):
    """Payment response schema"""
    id: int
    tenant_id: int
    amount: float
    due_date: Optional[str] = None
    paid_date: Optional[str] = None
    status: str
    payment_method: Optional[str] = None
    receipt_number: Optional[str] = None
    period_months: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# ============== EXPENSE SCHEMAS ==============

class ExpenseCreate(BaseModel):
    """Expense creation schema"""
    date: str
    category: str = Field(..., max_length=50)
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    receipt_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-10-24T00:00:00",
                "category": "utilities",
                "amount": 500000,
                "description": "Electric bill"
            }
        }


class ExpenseUpdate(BaseModel):
    """Expense update schema"""
    date: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "category": "maintenance",
                "amount": 750000
            }
        }


class ExpenseResponse(BaseModel):
    """Expense response schema"""
    id: int
    date: Optional[str] = None
    category: str
    amount: float
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# ============== DASHBOARD SCHEMAS ==============

class DashboardMetrics(BaseModel):
    """Dashboard metrics response"""
    total_rooms: int
    occupied_rooms: int
    available_rooms: int
    occupancy_rate: float
    total_income: float
    total_expenses: float
    net_profit: float
    overdue_count: int
    overdue_amount: float
    pending_count: int
    start_date: str
    end_date: str

    class Config:
        json_schema_extra = {
            "example": {
                "total_rooms": 10,
                "occupied_rooms": 8,
                "available_rooms": 2,
                "occupancy_rate": 80.0,
                "total_income": 12000000,
                "total_expenses": 2000000,
                "net_profit": 10000000,
                "overdue_count": 1,
                "overdue_amount": 1500000,
                "pending_count": 2,
                "start_date": "2024-10-01T00:00:00",
                "end_date": "2024-11-01T00:00:00"
            }
        }


class DashboardSummary(BaseModel):
    """Dashboard summary response"""
    recent_payments: list
    recent_expenses: list
    overdue_tenants: list

    class Config:
        json_schema_extra = {
            "example": {
                "recent_payments": [],
                "recent_expenses": [],
                "overdue_tenants": []
            }
        }


# ============== ERROR SCHEMAS ==============

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Not found",
                "detail": "Resource not found"
            }
        }
