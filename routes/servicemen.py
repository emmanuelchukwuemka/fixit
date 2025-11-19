from flask import Blueprint, render_template, send_from_directory

servicemen_bp = Blueprint('servicemen', __name__)

@servicemen_bp.route('/')
def index():
    return render_template('fixit/servicemen-app/index.html')

@servicemen_bp.route('/home')
def home():
    return render_template('fixit/servicemen-app/home.html')

# Serve manifest.json and other static files for PWA
@servicemen_bp.route('/manifest.json')
def manifest():
    return send_from_directory('templates/fixit/servicemen-app', 'manifest.json')

@servicemen_bp.route('/sw.js')
def service_worker():
    return send_from_directory('templates/fixit/servicemen-app', 'sw.js')

# Add routes for other HTML pages
@servicemen_bp.route('/<path:page>')
def serve_page(page):
    if page.endswith('.html'):
        return render_template(f'fixit/servicemen-app/{page}')
    return render_template('fixit/servicemen-app/index.html')

# Add more routes as needed
