import os
import logging
import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFProtect
from config import config
from flask_bootstrap import Bootstrap


# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)

# Load configuration based on environment
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Remove or comment out these lines since they're now in config.py
# app.secret_key = os.environ.get("SESSION_SECRET")
# app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static/uploads")
# app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

# Create upload folder
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize the database
db.init_app(app)

# Initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)
# Disable CSRF entirely (not recommended for production)
app.config['WTF_CSRF_ENABLED'] = False


# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Initialize Bootstrap
bootstrap = Bootstrap(app)

# Import models and create tables
with app.app_context():
    from models import User, Attendance, TreeData
    db.create_all()

# Import and register blueprints
from auth import auth_bp
app.register_blueprint(auth_bp)

from api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

# Add template context processor for global variables
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}
