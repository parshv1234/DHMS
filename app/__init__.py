from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

# Initialize global extensions
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()  # Flask-Login instance

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    logging.basicConfig(level=logging.DEBUG)
    # Database and app configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dhms_user:dhms_05@localhost/dhms_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')  # Use a default if not provided

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'parshv.23bce10807@vitbhopal.ac.in'
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Securely load from .env
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_DEFAULT_SENDER'] = 'parshv.23bce10807@vitbhopal.ac.in'

    # Razorpay configuration
    app.config['RAZORPAY_KEY_ID'] = os.getenv('RAZORPAY_KEY_ID')
    app.config['RAZORPAY_KEY_SECRET'] = os.getenv('RAZORPAY_KEY_SECRET')


    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    # Define the user_loader function
    @login_manager.user_loader
    def load_user(id):
        from .models import Doctor
        return Doctor.query.get(id)  # Assuming the user model is 'Doctor' with primary key 'id'

    # Register blueprints
    from app.doctor_routes import doctor_bp
    from app.patient_routes import patient_bp
    from app.auth_routes import auth_bp
    from app.admin_routes import admin
    # from app.department_routes import department
    from app.payment_routes import payment_bp

    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin, url_prefix='/admin')
    # app.register_blueprint(department, url_prefix='/admin/departments')
    app.register_blueprint(payment_bp, url_prefix='/payments')

    return app
