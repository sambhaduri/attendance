from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="employee")  # Can be "admin" or "employee"
    position = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "position": self.position,
            "created_at": self.created_at
        }

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    log_in = db.Column(db.DateTime, default=datetime.utcnow)
    log_out = db.Column(db.DateTime, nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    status = db.Column(db.Enum('Logged In', 'Logged Out', 'Absent', name='attendance_status'))

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "employee_name": self.name,
            "check_in": self.log_in,
            "check_out": self.log_out,
            "date": self.date,
            "status": self.status
        }

class Breaks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    status = db.Column(db.Enum('Break In', 'Break Out', name='break_status'))

    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "employee_name": self.name,
            "date": self.date,
            "status": self.status
        }

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    user = db.relationship('Employee', backref=db.backref('admin', uselist=False))
