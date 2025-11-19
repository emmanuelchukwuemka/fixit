from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    return render_template('fixit/user-app/index.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('user.home'))
        flash('Invalid credentials')
    return render_template('fixit/user-app/login.html')

@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user.login'))
    return render_template('fixit/user-app/signup.html')

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.index'))

@user_bp.route('/home')
@login_required
def home():
    return render_template('fixit/user-app/home.html')

# Add more routes for other pages like booking, profile, etc.
@user_bp.route('/booking')
@login_required
def booking():
    return render_template('fixit/user-app/booking.html')

@user_bp.route('/profile')
@login_required
def profile():
    return render_template('fixit/user-app/profile.html')

# Serve manifest.json and other static files for PWA
@user_bp.route('/manifest.json')
def manifest():
    return send_from_directory('templates/fixit/user-app', 'manifest.json')

@user_bp.route('/sw.js')
def service_worker():
    return send_from_directory('templates/fixit/user-app', 'sw.js')

# Add routes for other HTML pages
@user_bp.route('/<path:page>')
def serve_page(page):
    if page.endswith('.html'):
        return render_template(f'fixit/user-app/{page}')
    return render_template('fixit/user-app/index.html')
