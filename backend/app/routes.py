from flask import Blueprint, request, jsonify, current_app
from app import db, create_app
from app.models import Breaks, Employee, Attendance, Admin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

employee_bp = Blueprint("employee", __name__)
attendance_bp = Blueprint('attendance', __name__)
admin_bp = Blueprint('admin', __name__)
breaks_bp = Blueprint('breaks', __name__)

@employee_bp.route('/')
def home():
    # Step 1: Check if admin user exists
    admin_user = Employee.query.filter_by(email="admin@example.com").first()
    
    # Step 2: If user does not exist, create one
    if not admin_user:
        admin_user = Employee(
            name="Admin User",
            email="admin@example.com",
            password=generate_password_hash("admin123", method='pbkdf2:sha256', salt_length=16),
            role="admin",
            created_at=datetime.utcnow()
        )
        db.session.add(admin_user)
        db.session.commit()  # Commit to generate user ID

    # Step 3: Fetch user ID
    user_id = admin_user.id

    # Step 4: Check if admin entry already exists in Admin table
    admin_entry = Admin.query.filter_by(user_id=user_id).first()

    if not admin_entry:
        new_admin = Admin(user_id=user_id)  # Assuming Admin table has a user_id column
        db.session.add(new_admin)
        db.session.commit()

    return jsonify({"message": "Admin user setup complete", "user_id": user_id})
# Create a new employee
@employee_bp.route("/employees", methods=["POST"])
def create_employee():
    data = request.json
    if not all(k in data for k in ("name", "email", "position", "password")):  # Changed from department to position
        return jsonify({"error": "Missing required fields"}), 400

    new_employee = Employee(
        name=data["name"],
        email=data["email"],
        position=data["position"],
        password=data["password"]
    )

    db.session.add(new_employee)
    db.session.commit()
    
    return jsonify({"message": "Employee created successfully", "employee": new_employee.to_dict()}), 201

# Get all employees
@employee_bp.route("/employees", methods=["GET"])
def get_employees():
    employees = Employee.query.all()
    return jsonify([emp.to_dict() for emp in employees]), 200

# Get employee by ID
@employee_bp.route("/employees/<int:employee_id>", methods=["GET"])
def get_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(employee.to_dict()), 200

# Update employee details
@employee_bp.route("/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    data = request.json
    if "name" in data:
        employee.name = data["name"]
    if "email" in data:
        employee.email = data["email"]
    if "position" in data:  # Changed from department to position
        employee.position = data["position"]

    db.session.commit()
    return jsonify({"message": "Employee updated successfully", "employee": employee.to_dict()}), 200

# Delete an employee
@employee_bp.route("/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    db.session.delete(employee)
    db.session.commit()
    return jsonify({"message": "Employee deleted successfully"}), 200

@attendance_bp.route('/login', methods=['POST'])
def log_in():
    data = request.json
    employee_id = data.get('employee_id')
    employee = Employee.query.get(employee_id)

    if not employee_id:
        return jsonify({"error": "Employee ID is required"}), 400

    today = datetime.utcnow().date()
    existing_record = Attendance.query.filter_by(employee_id=employee_id, date=today).first()

    if existing_record:
        return jsonify({"message": "Already Logged in"}), 400

    new_attendance = Attendance(employee_id=employee_id, name=employee.name, log_in=datetime.utcnow(), status='Logged In')
    db.session.add(new_attendance)
    db.session.commit()

    return jsonify({"message": "Log-in successful", "data": new_attendance.to_dict()}), 201

@attendance_bp.route('/logout', methods=['POST'])
def log_out():
    data = request.json
    employee_id = data.get('employee_id')
    employee = Employee.query.get(employee_id)

    if not employee_id:
        return jsonify({"error": "Employee ID is required"}), 400

    today = datetime.utcnow().date()
    attendance_record = Attendance.query.filter_by(employee_id=employee_id, date=today).first()

    if not attendance_record:
        return jsonify({"error": "No Log in record found"}), 404

    if attendance_record.log_out:
        return jsonify({"message": "Already Logged out"}), 400

    attendance_record.log_out = datetime.utcnow()
    attendance_record.status = 'Logged Out'
    attendance_record.name = employee.name
    db.session.commit()

    return jsonify({"message": "Check-out successful", "data": attendance_record.to_dict()}), 200

@attendance_bp.route('/logs', methods=['GET'])
def get_attendance_logs():
    logs = Attendance.query.all()
    return jsonify([log.to_dict() for log in logs]), 200

@breaks_bp.route('/breakin', methods=['POST'])
def breakin():
    data = request.json
    employee_id = data.get('employee_id')

    if not employee_id:
        return jsonify({"error": "Employee ID is required"}), 400

    today = datetime.utcnow().date()

    # Check if employee has logged in today
    attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
    if not attendance or not attendance.log_in:
        return jsonify({"error": "Employee has not logged in today"}), 400

    # Prevent break-in if already logged out
    if attendance.log_out:
        return jsonify({"error": "Employee has already logged out today"}), 400

    # Check if the last break entry was a break-in without a break-out
    last_break = Breaks.query.filter_by(employee_id=employee_id, date=today).order_by(Breaks.id.desc()).first()
    if last_break and last_break.status == "Break In":
        return jsonify({"error": "Cannot break in again before breaking out"}), 400

    # Create a new break-in record
    new_break = Breaks(employee_id=employee_id, date=today, status="Break In")

    db.session.add(new_break)
    db.session.commit()

    return jsonify({"message": "Break-in recorded successfully", "data": new_break.to_dict()}), 201


@breaks_bp.route('/breakout', methods=['POST'])
def breakout():
    data = request.json
    employee_id = data.get('employee_id')

    if not employee_id:
        return jsonify({"error": "Employee ID is required"}), 400

    today = datetime.utcnow().date()

    # Check if employee has logged in today
    attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
    if not attendance or not attendance.log_in:
        return jsonify({"error": "Employee has not logged in today"}), 400

    # Prevent break-out if already logged out
    if attendance.log_out:
        return jsonify({"error": "Employee has already logged out today"}), 400

    # Check if the last break entry was a break-in
    last_break = Breaks.query.filter_by(employee_id=employee_id, date=today).order_by(Breaks.id.desc()).first()
    if not last_break or last_break.status != "Break In":
        return jsonify({"error": "Cannot break out without breaking in first"}), 400

    # Create a new break-out record
    new_break = Breaks(employee_id=employee_id, date=today, status="Break Out")

    db.session.add(new_break)
    db.session.commit()

    return jsonify({"message": "Break-out recorded successfully", "data": new_break.to_dict()}), 201

# Create a new user (Admin or Employee)
@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    current_user = get_jwt_identity()
    admin_user = Employee.query.filter_by(id=current_user['id']).first()
    
    if not admin_user or admin_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    hashed_password = generate_password_hash("admin123", method='pbkdf2:sha256', salt_length=16),  # Secure hashed password
    
    # Create new user
    new_user = Employee(
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        role=data.get('role', 'employee')
    )
    
    db.session.add(new_user)
    db.session.commit()

    # Generate access token for the new user
    access_token = create_access_token(identity={"id": new_user.id, "email": new_user.email, "role": new_user.role})
    
    response = jsonify({
        'message': 'User created successfully',
        'access_token': access_token
    })
    
    return response, 201

# 🔹 Promote user to admin

@admin_bp.route('/users/<int:user_id>/promote', methods=['PUT'])
@jwt_required()
def promote_user(user_id):
    current_user = get_jwt_identity()

    # Ensure current user is admin
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = Employee.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.role = 'admin'
    db.session.commit()
    return jsonify({'message': f'User {user.name} promoted to admin'}), 200

# 🔹 View dashboard stats

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    current_user = get_jwt_identity()
    role = get_jwt()

    # Ensure current user is admin
    if role.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    # Fetch dashboard statistics
    total_employees = Employee.query.count()
    today_check_ins = Attendance.query.filter(
        Attendance.date == db.func.current_date(), 
        Attendance.status == 'Logged In'
    ).count()
    
    pending_check_outs = Attendance.query.filter(
        Attendance.date == db.func.current_date(),
        Attendance.check_out.is_(None)
    ).count()

    total_attendance = Attendance.query.count()

    return jsonify({
        'total_employees': total_employees,
        'today_check_ins': today_check_ins,
        'pending_check_outs': pending_check_outs,
        'total_attendance': total_attendance
    }), 200

@admin_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = Employee.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Generate JWT token
    access_token = create_access_token(identity=str(user.id), additional_claims={ "role": str(user.role)})

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
    }), 200
