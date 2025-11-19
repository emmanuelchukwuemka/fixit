from flask import Blueprint, jsonify, request
from models import db, Service, Booking, User
from flask_login import login_required, current_user

api_bp = Blueprint('api', __name__)

@api_bp.route('/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'price': s.price,
        'category': s.category,
        'provider': s.provider.name
    } for s in services])

@api_bp.route('/bookings', methods=['GET'])
@login_required
def get_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': b.id,
        'service': b.service.name,
        'date': b.booking_date.isoformat(),
        'status': b.status
    } for b in bookings])

@api_bp.route('/booking', methods=['POST'])
@login_required
def create_booking():
    data = request.get_json()
    new_booking = Booking(
        user_id=current_user.id,
        service_id=data['service_id'],
        booking_date=data['date'],
        notes=data.get('notes')
    )
    db.session.add(new_booking)
    db.session.commit()
    return jsonify({'message': 'Booking created successfully'}), 201
