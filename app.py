from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager
from config import Config
from models import db
from routes.user import user_bp
from routes.provider import provider_bp
from routes.servicemen import servicemen_bp
from routes.api import api_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(provider_bp, url_prefix='/provider')
app.register_blueprint(servicemen_bp, url_prefix='/servicemen')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('static/fixit', filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
