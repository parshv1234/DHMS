from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.__init__ import db
from app.models import Department, Doctor, PatientRecord, Appointment, Payment
from utils.rbac import admin_required
import uuid
from datetime import datetime
import logging

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
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

@admin.route('/salaries', methods=['GET'])
def view_salaries():
    # Calculate the salary of all doctors
    doctor_salaries = db.session.query(
        Doctor.id, 
        Doctor.name, 
        db.func.sum(Payment.doctor_share).label('salary')
    ).join(Payment, Payment.doctor_id == Doctor.id).filter(Payment.payment_status == 'Paid')\
    .group_by(Doctor.id).all()

    # Calculate the admin's salary from the 'payments' table
    admin_salary = db.session.query(
        db.func.sum(Payment.admin_share).label('salary')
    ).filter(Payment.payment_status == 'Paid').scalar()  # Use scalar to get the sum value

    # If there's no admin salary, set it to 0
    admin_salary = admin_salary if admin_salary else 0

    return render_template('admin/view_salaries.html', 
                           doctor_salaries=doctor_salaries,
                           admin_salary=admin_salary)


@admin.route('/view_patients', methods=['GET'])
def view_patients():
    # Get all patients with their assigned doctors using the appointment record
    patient_data = db.session.query(
        PatientRecord.id,
        PatientRecord.name,
        PatientRecord.email_id,
        PatientRecord.contact_number_1,
        PatientRecord.age,
        Doctor.name.label('assigned_doctor')
    ).outerjoin(
        Appointment, Appointment.patient_id == PatientRecord.id
    ).outerjoin(
        Doctor, Appointment.doctor_id == Doctor.id
    ).all()

    # Format the data for rendering
    formatted_patient_data = [{
        'id': patient.id,
        'name': patient.name,
        'email': patient.email_id,
        'contact_number': patient.contact_number_1,
        'age': patient.age,
        'total_payment': 0.0,  # Dummy value or calculated value
        'assigned_doctor': patient.assigned_doctor or 'None'
    } for patient in patient_data]

    return render_template('admin/view_patients.html', patients=formatted_patient_data)



# Route to get all appointments
@admin.route('/appointments', methods=['GET'])
def get_appointments():
    if request.method == 'GET':
        try:
            # Query appointments with joins to Patient and Doctor tables
            appointments = db.session.query(Appointment, PatientRecord, Doctor).join(PatientRecord, Appointment.patient_id == PatientRecord.id) \
                .join(Doctor, Appointment.doctor_id == Doctor.id).all()

            appointment_list = []
            for appointment, patient, doctor in appointments:
                # Accessing names directly from the related Patient and Doctor
                patient_name = patient.name if patient else "Unknown Patient"
                doctor_name = doctor.name if doctor else "Unknown Doctor"

                # Creating the appointment data dictionary
                appointment_data = {
                    'id': appointment.id,
                    'patient_name': patient_name,
                    'doctor_name': doctor_name,
                    'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d'),
                    'appointment_time': appointment.appointment_time.strftime('%H:%M:%S'),
                    'status': appointment.status,
                    'reason': appointment.reason,
                }
                appointment_list.append(appointment_data)

            # Render the template and pass appointment data
            return render_template('admin/admin_appointments.html', appointments=appointment_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Route to edit an appointment
@admin.route('/appointments/edit/<uuid:appointment_id>', methods=['POST'])
def edit_appointment(appointment_id):
    try:
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            # Example of editing the status (you can add other fields here)
            appointment.status = request.json['status']
            db.session.commit()
            return jsonify({'message': 'Appointment updated successfully'}), 200
        else:
            return jsonify({'message': 'Appointment not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin.route('/appointments/delete/<uuid:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    if request.method == 'POST' and request.headers.get('X-HTTP-Method-Override') == 'DELETE':
        try:
            appointment = Appointment.query.get(appointment_id)
            if not appointment:
                return jsonify({'message': 'Appointment not found'}), 404

            db.session.delete(appointment)
            db.session.commit()
            return jsonify({'message': 'Appointment deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error deleting appointment: {str(e)}'}), 500



# Route to change appointment status
@admin.route('/appointments/change_status/<uuid:appointment_id>', methods=['POST'])
def change_status(appointment_id):
    try:
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            appointment.status = request.json['status']  # You can modify which status you want to set
            db.session.commit()
            return jsonify({'message': 'Status updated successfully'}), 200
        else:
            return jsonify({'message': 'Appointment not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500