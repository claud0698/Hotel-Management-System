from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """Admin user for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Room(db.Model):
    """Room information"""
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # single, double, suite
    monthly_rate = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='available')  # available, occupied, maintenance
    amenities = db.Column(db.Text)  # JSON or comma-separated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenants = db.relationship('Tenant', backref='room', lazy=True)
    room_history = db.relationship('RoomHistory', backref='room', lazy=True)

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
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Tenant(db.Model):
    """Tenant information"""
    __tablename__ = 'tenants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    id_number = db.Column(db.String(50))  # KTP, passport, etc
    move_in_date = db.Column(db.DateTime)
    move_out_date = db.Column(db.DateTime)
    current_room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    status = db.Column(db.String(20), default='active')  # active, inactive, moved_out
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    payments = db.relationship('Payment', backref='tenant', lazy=True, cascade='all, delete-orphan')
    room_history = db.relationship('RoomHistory', backref='tenant', lazy=True, cascade='all, delete-orphan')

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
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class RoomHistory(db.Model):
    """Track which tenant lived in which room and when"""
    __tablename__ = 'room_history'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    move_in_date = db.Column(db.DateTime, nullable=False)
    move_out_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'tenant_id': self.tenant_id,
            'move_in_date': self.move_in_date.isoformat(),
            'move_out_date': self.move_out_date.isoformat() if self.move_out_date else None,
            'created_at': self.created_at.isoformat()
        }


class Payment(db.Model):
    """Payment records for tenants"""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    paid_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    payment_method = db.Column(db.String(50))  # cash, transfer, etc
    receipt_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'amount': self.amount,
            'due_date': self.due_date.isoformat(),
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'status': self.status,
            'payment_method': self.payment_method,
            'receipt_number': self.receipt_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Expense(db.Model):
    """Expense records"""
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # utilities, maintenance, supplies, etc
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    receipt_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'category': self.category,
            'amount': self.amount,
            'description': self.description,
            'receipt_url': self.receipt_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
