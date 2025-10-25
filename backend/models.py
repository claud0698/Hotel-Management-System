"""
SQLAlchemy Models for Kos Management Dashboard
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base = declarative_base()

# Database instance (used for compatibility)
class DBInstance:
    pass

db = DBInstance()


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)


class User(Base):
    """Admin user for authentication"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password: str):
        """Set password hash"""
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Check password"""
        return verify_password(password, self.password_hash)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Room(Base):
    """Room information"""
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    room_number = Column(String(20), unique=True, nullable=False)
    floor = Column(Integer, nullable=False)  # Floor 2 = A (Atas/Upper), Floor 1 = B (Bawah/Lower)
    room_type = Column(String(50), nullable=False)  # single, double, suite
    monthly_rate = Column(Float, nullable=False)
    status = Column(String(20), default='available')  # available, occupied, maintenance
    amenities = Column(Text)  # JSON or comma-separated
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    tenants = relationship('Tenant', backref='room', lazy=True)
    room_history = relationship('RoomHistory', backref='room', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'room_number': self.room_number,
            'floor': self.floor,
            'room_type': self.room_type,
            'monthly_rate': self.monthly_rate,
            'status': self.status,
            'amenities': self.amenities,
            'current_tenant': self.tenants[0].to_dict() if self.tenants else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Tenant(Base):
    """Tenant information"""
    __tablename__ = 'tenants'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(20))
    email = Column(String(120))
    id_number = Column(String(50))  # KTP, passport, etc
    move_in_date = Column(DateTime)
    move_out_date = Column(DateTime)
    current_room_id = Column(Integer, ForeignKey('rooms.id'))
    status = Column(String(20), default='active')  # active, inactive, moved_out
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    payments = relationship('Payment', backref='tenant', lazy=True, cascade='all, delete-orphan')
    room_history = relationship('RoomHistory', backref='tenant', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'id_number': self.id_number,
            'move_in_date': self.move_in_date.isoformat() if self.move_in_date else None,
            'move_out_date': self.move_out_date.isoformat() if self.move_out_date else None,
            'current_room_id': self.current_room_id,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class RoomHistory(Base):
    """Track which tenant lived in which room and when"""
    __tablename__ = 'room_history'

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    move_in_date = Column(DateTime, nullable=False)
    move_out_date = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'tenant_id': self.tenant_id,
            'move_in_date': self.move_in_date.isoformat() if self.move_in_date else None,
            'move_out_date': self.move_out_date.isoformat() if self.move_out_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Payment(Base):
    """Payment records for tenants"""
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime)
    status = Column(String(20), default='pending')  # pending, paid, overdue
    payment_method = Column(String(50))  # cash, transfer, etc
    receipt_number = Column(String(100))
    period_months = Column(Integer, default=1)  # Number of months this payment covers
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'amount': self.amount,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'status': self.status,
            'payment_method': self.payment_method,
            'receipt_number': self.receipt_number,
            'period_months': self.period_months,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Expense(Base):
    """Expense records"""
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    category = Column(String(50), nullable=False)  # utilities, maintenance, supplies, etc
    amount = Column(Float, nullable=False)
    description = Column(Text)
    receipt_url = Column(String(255))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'category': self.category,
            'amount': self.amount,
            'description': self.description,
            'receipt_url': self.receipt_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
