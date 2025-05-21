import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "bcg_coding_competition_secret")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://koyeb-adm:npg_Ncga5zMUvjx2@ep-damp-mountain-a2kz5yia.eu-central-1.pg.koyeb.app/koyebdb"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure uploads
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB max upload

# Configure login
login_manager.init_app(app)
login_manager.login_view = "admin_login"
login_manager.login_message = "Please log in to access the admin dashboard."

# Initialize the app with the extension
db.init_app(app)

# Create uploads directory if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

with app.app_context():
    # Import models here to avoid circular imports
    import models  # noqa: F401

    # Create database tables
    db.create_all()
    
    # Create admin user if not exists
    from models import Admin
    from werkzeug.security import generate_password_hash
    
    admin = Admin.query.filter_by(username="Vishwa1214").first()
    if not admin:
        admin = Admin(
            username="Vishwa1214",
            password_hash=generate_password_hash("bcgvishwa@1214@")
        )
        db.session.add(admin)
        db.session.commit()
        logging.info("Admin user created")
