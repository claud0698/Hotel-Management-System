from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models import db, User, Room, Tenant, Payment, Expense, RoomHistory
from sqlalchemy import func

# Blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
rooms_bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')
tenants_bp = Blueprint('tenants', __name__, url_prefix='/api/tenants')
payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')
expenses_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


# ============== AUTH ROUTES ==============

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new admin user"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return {'error': 'Missing required fields'}, 400

    if User.query.filter_by(username=data['username']).first():
        return {'error': 'Username already exists'}, 409

    if User.query.filter_by(email=data['email']).first():
        return {'error': 'Email already exists'}, 409

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return {'message': 'User created successfully', 'user': user.to_dict()}, 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with username and password"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return {'error': 'Missing username or password'}, 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return {'error': 'Invalid username or password'}, 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=30))
    return {
        'access_token': access_token,
        'user': user.to_dict()
    }, 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged-in user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return {'error': 'User not found'}, 404

    return {'user': user.to_dict()}, 200


# ============== ROOM ROUTES ==============

@rooms_bp.route('', methods=['GET'])
@jwt_required()
def get_rooms():
    """Get all rooms"""
    rooms = Room.query.all()
    return {'rooms': [room.to_dict() for room in rooms]}, 200


@rooms_bp.route('/<int:room_id>', methods=['GET'])
@jwt_required()
def get_room(room_id):
    """Get a specific room"""
    room = Room.query.get(room_id)
    if not room:
        return {'error': 'Room not found'}, 404
    return {'room': room.to_dict()}, 200


@rooms_bp.route('', methods=['POST'])
@jwt_required()
def create_room():
    """Create a new room"""
    data = request.get_json()

    if not data or not data.get('room_number') or not data.get('monthly_rate'):
        return {'error': 'Missing required fields'}, 400

    if Room.query.filter_by(room_number=data['room_number']).first():
        return {'error': 'Room number already exists'}, 409

    room = Room(
        room_number=data['room_number'],
        floor=data.get('floor', 1),
        room_type=data.get('room_type', 'single'),
        monthly_rate=data['monthly_rate'],
        status=data.get('status', 'available'),
        amenities=data.get('amenities')
    )

    db.session.add(room)
    db.session.commit()

    return {'message': 'Room created', 'room': room.to_dict()}, 201


@rooms_bp.route('/<int:room_id>', methods=['PUT'])
@jwt_required()
def update_room(room_id):
    """Update a room"""
    room = Room.query.get(room_id)
    if not room:
        return {'error': 'Room not found'}, 404

    data = request.get_json()

    room.room_number = data.get('room_number', room.room_number)
    room.floor = data.get('floor', room.floor)
    room.room_type = data.get('room_type', room.room_type)
    room.monthly_rate = data.get('monthly_rate', room.monthly_rate)
    room.status = data.get('status', room.status)
    room.amenities = data.get('amenities', room.amenities)
    room.updated_at = datetime.utcnow()

    db.session.commit()

    return {'message': 'Room updated', 'room': room.to_dict()}, 200


@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
@jwt_required()
def delete_room(room_id):
    """Delete a room"""
    room = Room.query.get(room_id)
    if not room:
        return {'error': 'Room not found'}, 404

    db.session.delete(room)
    db.session.commit()

    return {'message': 'Room deleted'}, 200


# ============== TENANT ROUTES ==============

@tenants_bp.route('', methods=['GET'])
@jwt_required()
def get_tenants():
    """Get all tenants"""
    tenants = Tenant.query.all()
    return {'tenants': [tenant.to_dict() for tenant in tenants]}, 200


@tenants_bp.route('/<int:tenant_id>', methods=['GET'])
@jwt_required()
def get_tenant(tenant_id):
    """Get a specific tenant"""
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return {'error': 'Tenant not found'}, 404
    return {'tenant': tenant.to_dict()}, 200


@tenants_bp.route('', methods=['POST'])
@jwt_required()
def create_tenant():
    """Create a new tenant"""
    data = request.get_json()

    if not data or not data.get('name'):
        return {'error': 'Missing required fields'}, 400

    tenant = Tenant(
        name=data['name'],
        phone=data.get('phone'),
        email=data.get('email'),
        id_number=data.get('id_number'),
        move_in_date=datetime.fromisoformat(data['move_in_date']) if data.get('move_in_date') else None,
        current_room_id=data.get('current_room_id'),
        status=data.get('status', 'active'),
        notes=data.get('notes')
    )

    db.session.add(tenant)
    db.session.flush()

    # Create room history entry if room is assigned
    if tenant.current_room_id:
        room_history = RoomHistory(
            room_id=tenant.current_room_id,
            tenant_id=tenant.id,
            move_in_date=tenant.move_in_date or datetime.utcnow()
        )
        db.session.add(room_history)

        # Update room status
        room = Room.query.get(tenant.current_room_id)
        if room:
            room.status = 'occupied'

    db.session.commit()

    return {'message': 'Tenant created', 'tenant': tenant.to_dict()}, 201


@tenants_bp.route('/<int:tenant_id>', methods=['PUT'])
@jwt_required()
def update_tenant(tenant_id):
    """Update a tenant"""
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return {'error': 'Tenant not found'}, 404

    data = request.get_json()

    tenant.name = data.get('name', tenant.name)
    tenant.phone = data.get('phone', tenant.phone)
    tenant.email = data.get('email', tenant.email)
    tenant.id_number = data.get('id_number', tenant.id_number)
    tenant.move_in_date = datetime.fromisoformat(data['move_in_date']) if data.get('move_in_date') else tenant.move_in_date
    tenant.status = data.get('status', tenant.status)
    tenant.notes = data.get('notes', tenant.notes)
    tenant.updated_at = datetime.utcnow()

    # Handle room assignment changes
    if 'current_room_id' in data and data['current_room_id'] != tenant.current_room_id:
        old_room_id = tenant.current_room_id
        new_room_id = data['current_room_id']

        # Update old room status
        if old_room_id:
            old_room = Room.query.get(old_room_id)
            if old_room:
                old_room.status = 'available'
                # Update room history
                old_history = RoomHistory.query.filter_by(
                    room_id=old_room_id,
                    tenant_id=tenant_id,
                    move_out_date=None
                ).first()
                if old_history:
                    old_history.move_out_date = datetime.utcnow()

        # Update new room status
        if new_room_id:
            new_room = Room.query.get(new_room_id)
            if new_room:
                new_room.status = 'occupied'
                new_history = RoomHistory(
                    room_id=new_room_id,
                    tenant_id=tenant_id,
                    move_in_date=datetime.utcnow()
                )
                db.session.add(new_history)

        tenant.current_room_id = new_room_id

    db.session.commit()

    return {'message': 'Tenant updated', 'tenant': tenant.to_dict()}, 200


@tenants_bp.route('/<int:tenant_id>', methods=['DELETE'])
@jwt_required()
def delete_tenant(tenant_id):
    """Delete a tenant"""
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return {'error': 'Tenant not found'}, 404

    # Update room status if tenant has a room
    if tenant.current_room_id:
        room = Room.query.get(tenant.current_room_id)
        if room:
            room.status = 'available'

    db.session.delete(tenant)
    db.session.commit()

    return {'message': 'Tenant deleted'}, 200


# ============== PAYMENT ROUTES ==============

@payments_bp.route('', methods=['GET'])
@jwt_required()
def get_payments():
    """Get all payments"""
    tenant_id = request.args.get('tenant_id', type=int)
    status = request.args.get('status')

    query = Payment.query

    if tenant_id:
        query = query.filter_by(tenant_id=tenant_id)
    if status:
        query = query.filter_by(status=status)

    payments = query.all()
    return {'payments': [payment.to_dict() for payment in payments]}, 200


@payments_bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get a specific payment"""
    payment = Payment.query.get(payment_id)
    if not payment:
        return {'error': 'Payment not found'}, 404
    return {'payment': payment.to_dict()}, 200


@payments_bp.route('', methods=['POST'])
@jwt_required()
def create_payment():
    """Create a new payment"""
    data = request.get_json()

    if not data or not data.get('tenant_id') or not data.get('amount') or not data.get('due_date'):
        return {'error': 'Missing required fields'}, 400

    due_date = datetime.fromisoformat(data['due_date'])

    payment = Payment(
        tenant_id=data['tenant_id'],
        amount=data['amount'],
        due_date=due_date,
        status=data.get('status', 'pending'),
        payment_method=data.get('payment_method'),
        receipt_number=data.get('receipt_number'),
        notes=data.get('notes')
    )

    db.session.add(payment)
    db.session.commit()

    return {'message': 'Payment created', 'payment': payment.to_dict()}, 201


@payments_bp.route('/<int:payment_id>', methods=['PUT'])
@jwt_required()
def update_payment(payment_id):
    """Update a payment"""
    payment = Payment.query.get(payment_id)
    if not payment:
        return {'error': 'Payment not found'}, 404

    data = request.get_json()

    payment.amount = data.get('amount', payment.amount)
    payment.due_date = datetime.fromisoformat(data['due_date']) if data.get('due_date') else payment.due_date
    payment.status = data.get('status', payment.status)
    payment.payment_method = data.get('payment_method', payment.payment_method)
    payment.receipt_number = data.get('receipt_number', payment.receipt_number)
    payment.notes = data.get('notes', payment.notes)

    if data.get('status') == 'paid' and not payment.paid_date:
        payment.paid_date = datetime.utcnow()

    payment.updated_at = datetime.utcnow()

    db.session.commit()

    return {'message': 'Payment updated', 'payment': payment.to_dict()}, 200


@payments_bp.route('/<int:payment_id>/mark-paid', methods=['POST'])
@jwt_required()
def mark_payment_paid(payment_id):
    """Mark a payment as paid"""
    payment = Payment.query.get(payment_id)
    if not payment:
        return {'error': 'Payment not found'}, 404

    data = request.get_json() or {}

    payment.status = 'paid'
    payment.paid_date = datetime.utcnow()
    payment.payment_method = data.get('payment_method', payment.payment_method)
    payment.receipt_number = data.get('receipt_number', payment.receipt_number)
    payment.updated_at = datetime.utcnow()

    db.session.commit()

    return {'message': 'Payment marked as paid', 'payment': payment.to_dict()}, 200


@payments_bp.route('/<int:payment_id>', methods=['DELETE'])
@jwt_required()
def delete_payment(payment_id):
    """Delete a payment"""
    payment = Payment.query.get(payment_id)
    if not payment:
        return {'error': 'Payment not found'}, 404

    db.session.delete(payment)
    db.session.commit()

    return {'message': 'Payment deleted'}, 200


# ============== EXPENSE ROUTES ==============

@expenses_bp.route('', methods=['GET'])
@jwt_required()
def get_expenses():
    """Get all expenses"""
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Expense.query

    if category:
        query = query.filter_by(category=category)
    if start_date:
        query = query.filter(Expense.date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Expense.date <= datetime.fromisoformat(end_date))

    expenses = query.all()
    return {'expenses': [expense.to_dict() for expense in expenses]}, 200


@expenses_bp.route('/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    """Get a specific expense"""
    expense = Expense.query.get(expense_id)
    if not expense:
        return {'error': 'Expense not found'}, 404
    return {'expense': expense.to_dict()}, 200


@expenses_bp.route('', methods=['POST'])
@jwt_required()
def create_expense():
    """Create a new expense"""
    data = request.get_json()

    if not data or not data.get('category') or not data.get('amount') or not data.get('date'):
        return {'error': 'Missing required fields'}, 400

    expense = Expense(
        date=datetime.fromisoformat(data['date']),
        category=data['category'],
        amount=data['amount'],
        description=data.get('description'),
        receipt_url=data.get('receipt_url')
    )

    db.session.add(expense)
    db.session.commit()

    return {'message': 'Expense created', 'expense': expense.to_dict()}, 201


@expenses_bp.route('/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    """Update an expense"""
    expense = Expense.query.get(expense_id)
    if not expense:
        return {'error': 'Expense not found'}, 404

    data = request.get_json()

    expense.date = datetime.fromisoformat(data['date']) if data.get('date') else expense.date
    expense.category = data.get('category', expense.category)
    expense.amount = data.get('amount', expense.amount)
    expense.description = data.get('description', expense.description)
    expense.receipt_url = data.get('receipt_url', expense.receipt_url)
    expense.updated_at = datetime.utcnow()

    db.session.commit()

    return {'message': 'Expense updated', 'expense': expense.to_dict()}, 200


@expenses_bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    """Delete an expense"""
    expense = Expense.query.get(expense_id)
    if not expense:
        return {'error': 'Expense not found'}, 404

    db.session.delete(expense)
    db.session.commit()

    return {'message': 'Expense deleted'}, 200


# ============== DASHBOARD ROUTES ==============

@dashboard_bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    """Get dashboard metrics"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Default to current month
    now = datetime.utcnow()
    if not start_date:
        start_date = datetime(now.year, now.month, 1)
    else:
        start_date = datetime.fromisoformat(start_date)

    if not end_date:
        if now.month == 12:
            end_date = datetime(now.year + 1, 1, 1)
        else:
            end_date = datetime(now.year, now.month + 1, 1)
    else:
        end_date = datetime.fromisoformat(end_date)

    # Calculate metrics
    total_rooms = Room.query.count()
    occupied_rooms = Room.query.filter_by(status='occupied').count()
    available_rooms = Room.query.filter_by(status='available').count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

    # Income
    paid_payments = Payment.query.filter(
        Payment.status == 'paid',
        Payment.paid_date >= start_date,
        Payment.paid_date < end_date
    ).all()
    total_income = sum(p.amount for p in paid_payments)

    # Expenses
    expenses = Expense.query.filter(
        Expense.date >= start_date,
        Expense.date < end_date
    ).all()
    total_expenses = sum(e.amount for e in expenses)

    # Overdue payments
    overdue_payments = Payment.query.filter(
        Payment.status == 'pending',
        Payment.due_date < datetime.utcnow()
    ).all()
    overdue_count = len(overdue_payments)
    overdue_amount = sum(p.amount for p in overdue_payments)

    # Pending payments
    pending_payments = Payment.query.filter_by(status='pending').all()

    net_profit = total_income - total_expenses

    return {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'occupancy_rate': round(occupancy_rate, 2),
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'overdue_count': overdue_count,
        'overdue_amount': overdue_amount,
        'pending_count': len(pending_payments),
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    }, 200


@dashboard_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    """Get summary data for dashboard"""
    # Recent payments
    recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()

    # Recent expenses
    recent_expenses = Expense.query.order_by(Expense.created_at.desc()).limit(5).all()

    # Overdue tenants
    overdue_payments = Payment.query.filter(
        Payment.status == 'pending',
        Payment.due_date < datetime.utcnow()
    ).all()

    overdue_tenants = []
    for payment in overdue_payments:
        tenant = Tenant.query.get(payment.tenant_id)
        if tenant:
            overdue_tenants.append({
                'tenant': tenant.to_dict(),
                'payment': payment.to_dict()
            })

    return {
        'recent_payments': [p.to_dict() for p in recent_payments],
        'recent_expenses': [e.to_dict() for e in recent_expenses],
        'overdue_tenants': overdue_tenants
    }, 200
