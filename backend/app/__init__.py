from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:3000"])

    # Load config from .env or set manually
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://root:{os.getenv('MYSQL_PASSWORD')}@localhost/attendance"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback_secret_key') # Change this to a secure random key
    app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Default location for JWT tokens
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
  

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    with app.app_context():
        db.create_all()

    # Register blueprints
    from app.models import Breaks
    from app.models import Attendance
    from app.models import Employee
    from app.models import Admin
    from app.routes import employee_bp
    from app.routes import attendance_bp
    from app.routes import admin_bp
    from app.routes import breaks_bp
    app.register_blueprint(employee_bp)
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(breaks_bp, url_prefix='/attendance')


    return app