from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Department, Doctor, PatientRecord, Appointment
from utils.rbac import admin_required
import uuid

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    doctor_count = Doctor.query.count()
    patient_count = PatientRecord.query.count()
    appointment_count = Appointment.query.count()
    department_count = Department.query.count()
    
    return render_template('auth/admin_dashboard.html',
                         doctor_count=doctor_count,
                         patient_count=patient_count,
                         appointment_count=appointment_count,
                         department_count=department_count)

@admin.route('/admin/departments')
@login_required
@admin_required
def list_departments():
    departments = Department.query.all()
    return render_template('admin/departments/list.html', departments=departments)

@admin.route('/admin/departments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        head_doctor_id = request.form.get('head_doctor_id')
        
        # Validate unique department name
        existing_dept = Department.query.filter_by(name=name).first()
        if existing_dept:
            flash('Department name already exists', 'error')
            return redirect(url_for('admin.add_department'))
        
        # Generate a unique department ID (e.g., DEPT001)
        last_dept = Department.query.order_by(Department.id.desc()).first()
        if last_dept:
            last_num = int(last_dept.id[4:])
            new_id = f"DEPT{str(last_num + 1).zfill(3)}"
        else:
            new_id = "DEPT001"
        
        department = Department(
            id=new_id,
            name=name,
            description=description,
            head_doctor_id=head_doctor_id if head_doctor_id else None
        )
        
        try:
            db.session.add(department)
            db.session.commit()
            flash('Department added successfully', 'success')
            return redirect(url_for('admin.list_departments'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding department', 'error')
            return redirect(url_for('admin.add_department'))
    
    # Get all doctors for the head doctor selection
    doctors = Doctor.query.all()
    return render_template('admin/departments/add.html', doctors=doctors)

@admin.route('/admin/departments/edit/<string:dept_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        head_doctor_id = request.form.get('head_doctor_id')
        
        # Check if another department already has this name
        existing_dept = Department.query.filter(
            Department.name == name,
            Department.id != dept_id
        ).first()
        
        if existing_dept:
            flash('Department name already exists', 'error')
            return redirect(url_for('admin.edit_department', dept_id=dept_id))
        
        try:
            department.name = name
            department.description = description
            department.head_doctor_id = head_doctor_id if head_doctor_id else None
            
            db.session.commit()
            flash('Department updated successfully', 'success')
            return redirect(url_for('admin.list_departments'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating department', 'error')
            return redirect(url_for('admin.edit_department', dept_id=dept_id))
    
    doctors = Doctor.query.all()
    return render_template('admin/departments/edit.html', department=department, doctors=doctors)

@admin.route('/admin/departments/delete/<string:dept_id>', methods=['POST'])
@login_required
@admin_required
def delete_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    
    # Check if there are doctors in this department
    if department.doctors:
        return jsonify({
            'success': False,
            'message': 'Cannot delete department with assigned doctors'
        }), 400
    
    try:
        db.session.delete(department)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Department deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error deleting department'
        }), 500

# API endpoints for AJAX calls
@admin.route('/api/departments', methods=['GET'])
@login_required
def get_departments():
    departments = Department.query.all()
    return jsonify([{
        'id': dept.id,
        'name': dept.name,
        'description': dept.description,
        'head_doctor_id': dept.head_doctor_id,
        'head_doctor_name': dept.head_doctor.name if dept.head_doctor else None
    } for dept in departments])

@admin.route('/api/departments/<string:dept_id>', methods=['GET'])
@login_required
def get_department(dept_id):
    department = Department.query.get_or_404(dept_id)
    return jsonify({
        'id': department.id,
        'name': department.name,
        'description': department.description,
        'head_doctor_id': department.head_doctor_id,
        'head_doctor_name': department.head_doctor.name if department.head_doctor else None,
        'doctors_count': len(department.doctors)
    })