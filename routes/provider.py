from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Provider, Service, Serviceman, Booking

provider_bp = Blueprint('provider', __name__)

@provider_bp.route('/')
def index():
    return render_template('fixit/provider-app/index.html')

@provider_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        provider = Provider.query.filter_by(email=email).first()
        if provider and check_password_hash(provider.password, password):
            login_user(provider)
            return redirect(url_for('provider.home'))
        flash('Invalid credentials')
    return render_template('fixit/provider-app/login.html')

@provider_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')
        new_provider = Provider(name=name, email=email, password=hashed_password)
        db.session.add(new_provider)
        db.session.commit()
        return redirect(url_for('provider.login'))
    return render_template('fixit/provider-app/signup.html')

@provider_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('provider.index'))

@provider_bp.route('/home')
@login_required
def home():
    services = Service.query.filter_by(provider_id=current_user.id).all()
    bookings = Booking.query.join(Service).filter(Service.provider_id == current_user.id).all()
    return render_template('fixit/provider-app/home.html', services=services, bookings=bookings)

@provider_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    provider = Provider.query.filter_by(email=data['email']).first()
    if provider and check_password_hash(provider.password, data['password']):
        login_user(provider)
        return jsonify({'success': True, 'message': 'Logged in successfully'})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@provider_bp.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    if Provider.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_provider = Provider(name=data['name'], email=data['email'], password=hashed_password)
    db.session.add(new_provider)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Provider created successfully'})

@provider_bp.route('/api/services', methods=['GET'])
@login_required
def api_services():
    services = Service.query.filter_by(provider_id=current_user.id).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'price': s.price,
        'category': s.category
    } for s in services])

@provider_bp.route('/api/service', methods=['POST'])
@login_required
def api_create_service():
    data = request.get_json()
    new_service = Service(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        category=data.get('category'),
        provider_id=current_user.id
    )
    db.session.add(new_service)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Service created successfully'})

@provider_bp.route('/api/servicemen', methods=['GET'])
@login_required
def api_servicemen():
    servicemen = Serviceman.query.filter_by(provider_id=current_user.id).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'email': s.email,
        'phone': s.phone
    } for s in servicemen])

@provider_bp.route('/api/serviceman', methods=['POST'])
@login_required
def api_create_serviceman():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_serviceman = Serviceman(
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        phone=data.get('phone'),
        provider_id=current_user.id
    )
    db.session.add(new_serviceman)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Serviceman created successfully'})

@provider_bp.route('/api/bookings', methods=['GET'])
@login_required
def api_bookings():
    bookings = Booking.query.join(Service).filter(Service.provider_id == current_user.id).all()
    return jsonify([{
        'id': b.id,
        'service': b.service.name,
        'user': b.user.username,
        'date': b.booking_date.isoformat(),
        'status': b.status
    } for b in bookings])

@provider_bp.route('/api/booking/<int:booking_id>/status', methods=['PUT'])
@login_required
def api_update_booking_status(booking_id):
    data = request.get_json()
    booking = Booking.query.get_or_404(booking_id)
    # Ensure the booking belongs to this provider
    if booking.service.provider_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    booking.status = data['status']
    db.session.commit()
    return jsonify({'success': True, 'message': 'Booking status updated'})

# Serve manifest.json and other static files for PWA
@provider_bp.route('/manifest.json')
def manifest():
    return send_from_directory('templates/fixit/provider-app', 'manifest.json')

@provider_bp.route('/sw.js')
def service_worker():
    return send_from_directory('templates/fixit/provider-app', 'sw.js')

# Add routes for other HTML pages
@provider_bp.route('/<path:page>')
def serve_page(page):
    if page.endswith('.html'):
        return render_template(f'fixit/provider-app/{page}')
    return render_template('fixit/provider-app/index.html')
