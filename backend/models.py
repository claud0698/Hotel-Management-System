"""
SQLAlchemy Models for Hotel Management System v1.0
Designed for Supabase PostgreSQL
Created: November 8, 2025
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, Numeric, Date, CheckConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base = declarative_base()


def hash_password(password: str) -> str:
    """Hash a password for storage"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# MODEL 1: User
# ============================================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), index=True)
    full_name = Column(String(100))
    phone = Column(String(20))
    role = Column(String(10), nullable=False, default='user')  # admin, user
    status = Column(String(10), default='active')  # active, inactive
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'user')"),
        CheckConstraint("status IN ('active', 'inactive')"),
    )

    # Relationships
    created_reservations = relationship("Reservation", foreign_keys="Reservation.created_by")
    created_payments = relationship("Payment", foreign_keys="Payment.created_by")
    uploaded_room_images = relationship("RoomImage", foreign_keys="RoomImage.uploaded_by")
    uploaded_type_images = relationship("RoomTypeImage", foreign_keys="RoomTypeImage.uploaded_by")
    uploaded_attachments = relationship("PaymentAttachment", foreign_keys="PaymentAttachment.uploaded_by")
    verified_attachments = relationship("PaymentAttachment", foreign_keys="PaymentAttachment.verified_by")

    def set_password(self, password: str):
        """Set password hash"""
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Check password"""
        return verify_password(password, self.password_hash)

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone,
            "role": self.role,
            "status": self.status,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


# ============================================================================
# MODEL 2: RoomType
# ============================================================================
class RoomType(Base):
    __tablename__ = "room_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True, nullable=False, index=True)
    description = Column(Text)
    base_capacity_adults = Column(Integer, default=2)
    base_capacity_children = Column(Integer, default=1)
    bed_config = Column(String(100))
    default_rate = Column(Numeric(12, 2), nullable=False)
    amenities = Column(Text)
    max_occupancy = Column(Integer)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rooms = relationship("Room", back_populates="room_type")
    room_images = relationship("RoomTypeImage", back_populates="room_type")
    guests_preferred = relationship("Guest", back_populates="preferred_room_type")
    reservations = relationship("Reservation", foreign_keys="Reservation.room_type_id")

    def to_dict(self):
        """Convert room type to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "base_capacity_adults": self.base_capacity_adults,
            "base_capacity_children": self.base_capacity_children,
            "bed_config": self.bed_config,
            "default_rate": float(self.default_rate) if self.default_rate else 0,
            "amenities": self.amenities,
            "max_occupancy": self.max_occupancy,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<RoomType(id={self.id}, name={self.name}, code={self.code})>"


# ============================================================================
# MODEL 3: Room
# ============================================================================
class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    room_number = Column(String(10), unique=True, nullable=False, index=True)
    floor = Column(Integer)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False, index=True)
    status = Column(String(20), default='available', index=True)  # available, occupied, out_of_order
    view_type = Column(String(50))
    notes = Column(Text)
    custom_rate = Column(Numeric(12, 2))  # Room-level rate override
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("status IN ('available', 'occupied', 'out_of_order')"),
        Index("idx_rooms_type", "room_type_id"),
    )

    # Relationships
    room_type = relationship("RoomType", back_populates="rooms")
    room_images = relationship("RoomImage", back_populates="room")
    reservations = relationship("Reservation", foreign_keys="Reservation.room_id")

    def get_effective_rate(self) -> float:
        """Get the effective rate for this room (custom_rate or room_type default_rate)"""
        if self.custom_rate:
            return float(self.custom_rate)
        return float(self.room_type.default_rate)

    def to_dict(self):
        """Convert room to dictionary"""
        return {
            "id": self.id,
            "room_number": self.room_number,
            "floor": self.floor,
            "room_type_id": self.room_type_id,
            "room_type_name": self.room_type.name if self.room_type else None,
            "status": self.status,
            "view_type": self.view_type,
            "notes": self.notes,
            "custom_rate": float(self.custom_rate) if self.custom_rate else None,
            "effective_rate": self.get_effective_rate(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Room(id={self.id}, room_number={self.room_number}, status={self.status})>"


# ============================================================================
# MODEL 3b: RoomImage
# ============================================================================
class RoomImage(Base):
    __tablename__ = "room_images"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    image_name = Column(String(255), nullable=False)
    image_type = Column(String(20), nullable=False)  # main_photo, bedroom, bathroom, living_area, amenities, other
    image_path = Column(String(500), nullable=False)
    storage_location = Column(String(50), nullable=False)  # local, s3, gcs, azure
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))
    original_filename = Column(String(255))
    image_width = Column(Integer)
    image_height = Column(Integer)
    uploaded_by = Column(Integer, ForeignKey("users.id"), index=True)
    description = Column(Text)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("image_type IN ('main_photo', 'bedroom', 'bathroom', 'living_area', 'amenities', 'other')"),
        CheckConstraint("storage_location IN ('local', 's3', 'gcs', 'azure')"),
        Index("idx_room_images_order", "room_id", "display_order"),
    )

    # Relationships
    room = relationship("Room", back_populates="room_images")
    uploaded_by_user = relationship("User", foreign_keys=[uploaded_by])

    def __repr__(self):
        return f"<RoomImage(id={self.id}, room_id={self.room_id}, type={self.image_type})>"


# ============================================================================
# MODEL 3c: RoomTypeImage
# ============================================================================
class RoomTypeImage(Base):
    __tablename__ = "room_type_images"

    id = Column(Integer, primary_key=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False, index=True)
    image_name = Column(String(255), nullable=False)
    image_type = Column(String(20), nullable=False)  # showcase, floorplan, amenities, other
    image_path = Column(String(500), nullable=False)
    storage_location = Column(String(50), nullable=False)  # local, s3, gcs, azure
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))
    original_filename = Column(String(255))
    image_width = Column(Integer)
    image_height = Column(Integer)
    uploaded_by = Column(Integer, ForeignKey("users.id"), index=True)
    description = Column(Text)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("image_type IN ('showcase', 'floorplan', 'amenities', 'other')"),
        CheckConstraint("storage_location IN ('local', 's3', 'gcs', 'azure')"),
        Index("idx_room_type_images_order", "room_type_id", "display_order"),
    )

    # Relationships
    room_type = relationship("RoomType", back_populates="room_images")
    uploaded_by_user = relationship("User", foreign_keys=[uploaded_by])

    def __repr__(self):
        return f"<RoomTypeImage(id={self.id}, room_type_id={self.room_type_id}, type={self.image_type})>"


# ============================================================================
# MODEL 4: Guest
# ============================================================================
class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), index=True)
    phone = Column(String(20), index=True)
    phone_country_code = Column(String(5))
    id_type = Column(String(50))
    id_number = Column(String(50))
    nationality = Column(String(50))
    birth_date = Column(Date)
    notes = Column(Text)
    is_vip = Column(Boolean, default=False)
    preferred_room_type_id = Column(Integer, ForeignKey("room_types.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    preferred_room_type = relationship("RoomType", back_populates="guests_preferred")
    reservations = relationship("Reservation", back_populates="guest")

    def to_dict(self):
        """Convert guest to dictionary"""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "phone_country_code": self.phone_country_code,
            "id_type": self.id_type,
            "id_number": self.id_number,
            "nationality": self.nationality,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "notes": self.notes,
            "is_vip": self.is_vip,
            "preferred_room_type_id": self.preferred_room_type_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Guest(id={self.id}, name={self.full_name}, vip={self.is_vip})>"


# ============================================================================
# MODEL 4.5: Guest Image (ID Photo)
# ============================================================================
class GuestImage(Base):
    __tablename__ = "guest_images"

    id = Column(Integer, primary_key=True)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False, index=True)
    image_type = Column(String(50), nullable=False)  # id_photo, passport_photo, license_photo, etc.
    file_path = Column(String(500), nullable=False)  # Storage path (GCS, S3, local, etc.)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(100))  # image/jpeg, image/png, etc.
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"))  # Receptionist who uploaded
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    guest = relationship("Guest", backref="images")
    uploaded_by = relationship("User", backref="guest_images_uploaded")

    def to_dict(self):
        """Convert guest image to dictionary"""
        return {
            "id": self.id,
            "guest_id": self.guest_id,
            "image_type": self.image_type,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "uploaded_by_user_id": self.uploaded_by_user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<GuestImage(id={self.id}, guest_id={self.guest_id}, type={self.image_type})>"


# ============================================================================
# MODEL 5: Reservation
# ============================================================================
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)
    confirmation_number = Column(String(20), unique=True, nullable=False, index=True)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False, index=True)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), index=True)
    adults = Column(Integer, default=1)
    children = Column(Integer, default=0)
    rate_per_night = Column(Numeric(12, 2), nullable=False)
    number_of_nights = Column(Integer)  # Calculated field
    subtotal = Column(Numeric(12, 2), nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0)
    discount_id = Column(Integer, ForeignKey("discounts.id"))
    total_amount = Column(Numeric(12, 2), nullable=False)
    special_requests = Column(Text)
    status = Column(String(20), default='confirmed', index=True)  # confirmed, checked_in, checked_out, cancelled
    booking_source = Column(String(50))
    booking_channel_id = Column(Integer, ForeignKey("booking_channels.id"))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    checked_in_by = Column(Integer, ForeignKey("users.id"))  # Receptionist who did check-in
    checked_in_at = Column(DateTime)
    checked_out_at = Column(DateTime)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("status IN ('confirmed', 'checked_in', 'checked_out', 'cancelled')"),
        Index("idx_reservations_dates", "check_in_date", "check_out_date"),
        Index("idx_reservations_guest_dates", "guest_id", "check_in_date", "check_out_date"),
    )

    # Relationships
    guest = relationship("Guest", back_populates="reservations")
    room_type = relationship("RoomType", foreign_keys=[room_type_id])
    room = relationship("Room")
    created_by_user = relationship("User", foreign_keys=[created_by])
    checked_in_by_user = relationship("User", foreign_keys=[checked_in_by])
    discount = relationship("Discount")
    booking_channel = relationship("BookingChannel")
    payments = relationship("Payment", back_populates="reservation")

    def calculate_total_paid(self) -> float:
        """Calculate total amount paid for this reservation"""
        total = sum(float(p.amount) for p in self.payments if not p.is_refund and not p.is_voided)
        return total

    def calculate_balance(self) -> float:
        """Calculate remaining balance"""
        total_paid = self.calculate_total_paid()
        return float(self.total_amount) - total_paid

    def to_dict(self):
        """Convert reservation to dictionary"""
        return {
            "id": self.id,
            "confirmation_number": self.confirmation_number,
            "guest_id": self.guest_id,
            "guest_name": self.guest.full_name if self.guest else None,
            "check_in_date": self.check_in_date.isoformat() if self.check_in_date else None,
            "check_out_date": self.check_out_date.isoformat() if self.check_out_date else None,
            "room_type_id": self.room_type_id,
            "room_id": self.room_id,
            "room_number": self.room.room_number if self.room else None,
            "adults": self.adults,
            "children": self.children,
            "rate_per_night": float(self.rate_per_night) if self.rate_per_night else 0,
            "number_of_nights": self.number_of_nights,
            "subtotal": float(self.subtotal) if self.subtotal else 0,
            "discount_amount": float(self.discount_amount) if self.discount_amount else 0,
            "total_amount": float(self.total_amount) if self.total_amount else 0,
            "special_requests": self.special_requests,
            "status": self.status,
            "booking_source": self.booking_source,
            "total_paid": self.calculate_total_paid(),
            "balance": self.calculate_balance(),
            "checked_in_at": self.checked_in_at.isoformat() if self.checked_in_at else None,
            "checked_in_by": self.checked_in_by,
            "checked_in_by_name": self.checked_in_by_user.username if self.checked_in_by_user else None,
            "checked_out_at": self.checked_out_at.isoformat() if self.checked_out_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Reservation(id={self.id}, conf={self.confirmation_number}, guest_id={self.guest_id})>"


# ============================================================================
# MODEL 6: Payment
# ============================================================================
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(20), nullable=False, index=True)  # cash, credit_card, debit_card, bank_transfer, e_wallet, other
    reference_number = Column(String(100))
    transaction_id = Column(String(100), index=True)
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_refund = Column(Boolean, default=False)
    refund_reason = Column(Text)
    is_voided = Column(Boolean, default=False)
    has_proof = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("payment_method IN ('cash', 'credit_card', 'debit_card', 'bank_transfer', 'e_wallet', 'other')"),
    )

    # Relationships
    reservation = relationship("Reservation", back_populates="payments")
    created_by_user = relationship("User", foreign_keys=[created_by])
    attachments = relationship("PaymentAttachment", back_populates="payment")

    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            "id": self.id,
            "reservation_id": self.reservation_id,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "amount": float(self.amount) if self.amount else 0,
            "payment_method": self.payment_method,
            "reference_number": self.reference_number,
            "transaction_id": self.transaction_id,
            "notes": self.notes,
            "is_refund": self.is_refund,
            "refund_reason": self.refund_reason,
            "is_voided": self.is_voided,
            "has_proof": self.has_proof,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Payment(id={self.id}, reservation_id={self.reservation_id}, amount={self.amount})>"


# ============================================================================
# MODEL 7: PaymentAttachment
# ============================================================================
class PaymentAttachment(Base):
    __tablename__ = "payment_attachments"

    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # invoice, receipt, transfer_proof, credit_card_slip, other
    file_path = Column(String(500), nullable=False)
    storage_location = Column(String(50), nullable=False)  # local, s3, gcs, azure
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))
    original_filename = Column(String(255))
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    description = Column(Text)
    is_verified = Column(Boolean, default=False, index=True)
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("file_type IN ('invoice', 'receipt', 'transfer_proof', 'credit_card_slip', 'other')"),
        CheckConstraint("storage_location IN ('local', 's3', 'gcs', 'azure')"),
        Index("idx_payment_attachments_created", "created_at"),
    )

    # Relationships
    payment = relationship("Payment", back_populates="attachments")
    uploaded_by_user = relationship("User", foreign_keys=[uploaded_by])
    verified_by_user = relationship("User", foreign_keys=[verified_by])

    def __repr__(self):
        return f"<PaymentAttachment(id={self.id}, payment_id={self.payment_id}, type={self.file_type})>"


# ============================================================================
# MODEL 8: Setting
# ============================================================================
class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_value = Column(Text)
    setting_type = Column(String(20), default='string')  # string, integer, boolean, json, decimal
    is_editable = Column(Boolean, default=True)
    description = Column(Text)
    category = Column(String(50), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("setting_type IN ('string', 'integer', 'boolean', 'json', 'decimal')"),
    )

    def __repr__(self):
        return f"<Setting(key={self.setting_key}, type={self.setting_type})>"


# ============================================================================
# MODEL 9: Discount (V1.1+ - Created but not used in v1.0)
# ============================================================================
class Discount(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, index=True)
    description = Column(Text)
    discount_type = Column(String(20), nullable=False)  # percentage, fixed_amount
    discount_value = Column(Numeric(12, 2), nullable=False)
    max_discount_amount = Column(Numeric(12, 2))
    applicable_room_types = Column(Text)  # JSON array
    applicable_guests = Column(Text)  # JSON array
    valid_from = Column(Date)
    valid_until = Column(Date)
    usage_limit = Column(Integer)
    usage_count = Column(Integer, default=0)
    min_stay_nights = Column(Integer)
    min_booking_amount = Column(Numeric(12, 2))
    max_bookings_per_guest = Column(Integer)
    status = Column(String(20), default='active', index=True)  # active, inactive, expired
    is_auto_applied = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("discount_type IN ('percentage', 'fixed_amount')"),
        CheckConstraint("status IN ('active', 'inactive', 'expired')"),
        Index("idx_discounts_dates", "valid_from", "valid_until"),
    )

    def __repr__(self):
        return f"<Discount(id={self.id}, code={self.code}, type={self.discount_type})>"


# ============================================================================
# MODEL 10: BookingChannel (V1.1+ - Simplified for V1.0)
# ============================================================================
class BookingChannel(Base):
    __tablename__ = "booking_channels"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text)
    channel_type = Column(String(50), nullable=False)  # ota, direct, corporate, api
    api_url = Column(String(255))
    api_key = Column(String(255))
    api_secret = Column(String(255))
    webhook_url = Column(String(255))
    is_enabled = Column(Boolean, default=True, index=True)
    auto_confirm = Column(Boolean, default=False)
    sync_enabled = Column(Boolean, default=False)
    sync_interval_minutes = Column(Integer, default=60)
    commission_percentage = Column(Numeric(5, 2), default=0)
    commission_fixed_amount = Column(Numeric(12, 2), default=0)
    support_contact = Column(String(255))
    support_email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("channel_type IN ('ota', 'direct', 'corporate', 'api')"),
    )

    def __repr__(self):
        return f"<BookingChannel(id={self.id}, code={self.code}, name={self.name})>"


# Database instance for compatibility
class DBInstance:
    pass


db = DBInstance()
