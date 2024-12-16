from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_migrate import Migrate


# Initialize global extensions
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()  # Flask-Login instance

def create_app():
    app = Flask(__name__)

    # Database and app configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dhms_user:dhms_05@localhost/dhms_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'parshv@123'

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'parshv.23bce10807@vitbhopal.ac.in'
    app.config['MAIL_PASSWORD'] = 'fmqs jhlk njnt ienw'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_DEFAULT_SENDER'] = 'parshv.23bce10807@vitbhopal.ac.in'
    
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
    from app.department_routes import department

    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(department, url_prefix='/admin/departments')

    return app