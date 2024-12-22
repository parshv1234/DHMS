from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.__init__ import db
from app.models import Doctor
from flask_mail import Message
from app import mail
import datetime
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, PrescriptionRecord, PatientRecord, Appointment
from utils.rbac import role_required
import uuid
from app.auth_routes import auth_bp
from PIL import Image
import io
# from pyzxing import BarCodeReader
from pyzbar.pyzbar import decode

# Define the blueprint for doctor-related routes
doctor_bp = Blueprint('doctor_bp', __name__, template_folder='templates/doctors')

@doctor_bp.route('/ihilogin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()  # Strip spaces
        password = request.form['password']

        # Find doctor by email
        doctor = Doctor.query.filter_by(email_id=email).first()

        if doctor:
            print(f"Stored password hash: {doctor.password}")  # Debug print to check the stored password hash
            print(f"Entered password: {password}")  # Debug print to check the entered password

            if doctor.check_password(password):  # Check if password matches
                login_user(doctor)
                flash('Login successful!', 'success')
                return redirect(url_for('doctor_bp.view_doctors'))
            else:   
                flash('Invalid credentials, please try again.', 'danger')
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')


# Logout route
@doctor_bp.route('/logout')
def logout():
    # Clear the session
    session.clear()
    
    # Flash a success message
    flash('You have been logged out successfully.', 'success')
    
    # Redirect to the login page (adjust the endpoint as needed)
    return redirect(url_for('auth.login'))  # Redirect to login page

# Fetch all doctors from the database
def get_all_doctors():
    doctors = Doctor.query.all()  # Get all doctor records from the doctor_record table
    return doctors

# Route for viewing doctors
@doctor_bp.route('/view_doctor')
# @role_required(['admin'])
def view_doctors():
    doctors = get_all_doctors()  # Call the function to fetch all doctors
    if request.method == 'POST':
        pass
    else:
        email = session.get('email')
        user = User.query.filter_by(email=email).first()
        return render_template('view_doctor.html', doctors=doctors)

# Add a new doctor
@doctor_bp.route('/add_doctor', methods=['GET', 'POST'])
# @role_required(['admin'])
def add_doctor():
    if request.method == 'POST':
        # Get data from form
        name = request.form['name']
        gender = request.form['gender']
        dob = request.form['dob']
        blood_group = request.form['blood_group']
        department_id = request.form['department_id']
        department_name = request.form['department_name']
        contact_number_1 = request.form['contact_number_1']
        contact_number_2 = request.form.get('contact_number_2')
        aadhar_or_voter_id = request.form['aadhar_or_voter_id']
        email_id = request.form['email_id']
        qualification = request.form['qualification']
        specialisation = request.form['specialisation']
        years_of_experience = request.form['years_of_experience']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        pin_code = request.form['pin_code']
        password = request.form['password']  # Added password field

        # Generate doctor ID
        doctor_id = f"DR-{datetime.datetime.now().strftime('%S%M%H')}-{datetime.datetime.now().strftime('%Y%m%d')[2:]}"
        
        # Calculate the doctor's age using the method in the Doctor model
        age = Doctor.calculate_age(dob)

        # Create new doctor instance
        new_doctor = Doctor(id=doctor_id, name=name, age=age, gender=gender, date_of_birth=dob,
                            blood_group=blood_group, department_id=department_id, department_name=department_name,
                            contact_number_1=contact_number_1, contact_number_2=contact_number_2,
                            aadhar_or_voter_id=aadhar_or_voter_id, email_id=email_id, qualification=qualification,
                            specialisation=specialisation, years_of_experience=years_of_experience, address=address,
                            city=city, state=state, pin_code=pin_code)
        
        # Hash the password before saving
        new_doctor.set_password(password)

        # Save new doctor to the database
        db.session.add(new_doctor)
        db.session.commit()

        flash('Doctor added successfully!', 'success')
        return redirect(url_for('doctor_bp.view_doctors'))  # Redirect to doctor list page

    return render_template('add_doctor.html')


from datetime import datetime

@doctor_bp.route('/edit_doctor/<doctor_id>', methods=['GET', 'POST'])
# @role_required(['admin'])
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == 'POST':
        # Update doctor's information from the form
        doctor.name = request.form['name']
        doctor.gender = request.form['gender']
        doctor.date_of_birth = request.form['dob']
        doctor.blood_group = request.form['blood_group']
        doctor.department_id = request.form['department_id']
        doctor.department_name = request.form['department_name']
        doctor.contact_number_1 = request.form['contact_number_1']
        doctor.contact_number_2 = request.form.get('contact_number_2')
        doctor.aadhar_or_voter_id = request.form['aadhar_or_voter_id']
        doctor.email_id = request.form['email_id']
        doctor.qualification = request.form['qualification']
        doctor.specialisation = request.form['specialisation']
        doctor.years_of_experience = request.form['years_of_experience']
        doctor.address = request.form['address']
        doctor.city = request.form['city']
        doctor.state = request.form['state']
        doctor.pin_code = request.form['pin_code']

        # Update age based on the date of birth
        dob = datetime.strptime(doctor.date_of_birth, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))  # Calculating age
        doctor.age = age

        # Handle password change
        password = request.form.get('password', '').strip()
        if password:  # Only update if password is provided
            doctor.set_password(password)  # Hash the new password

        # Commit changes to the database
        try:
            db.session.commit()
            flash('Doctor updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {e}', 'danger')

        return redirect(url_for('doctor_bp.view_doctors'))  # Redirect after update

    return render_template('edit_doctor.html', doctor=doctor)


# Route to delete a doctor
@doctor_bp.route('/delete_doctor/<id>', methods=['GET'])
# @role_required(['admin'])
def delete_doctor(id):
    doctor = Doctor.query.get(id)
    if not doctor:
        flash('Doctor not found!', 'danger')
        return redirect(url_for('doctor_bp.view_doctors'))

    try:
        db.session.delete(doctor)
        db.session.commit()
        flash('Doctor deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('doctor_bp.view_doctors'))

@doctor_bp.route('/create-prescription', methods=['GET', 'POST'])
@role_required(['doctor'])
def create_prescription():
    if request.method == 'POST':
        # Retrieve form data
        patient_id = request.form.get('patient_id')
        prescription_details = request.form.get('details')

        # Validate input fields
        if not patient_id or not prescription_details:
            flash("All fields are required!", "danger")
            return redirect(url_for('doctor.create_prescription'))

        # Check if patient exists in the database
        patient = PatientRecord.query.filter_by(id=patient_id).first()
        if not patient:
            flash("Patient not found!", "danger")
            return redirect(url_for('doctor.create_prescription'))

        try:
            # Create new prescription
            new_prescription = PrescriptionRecord(
                id=str(uuid.uuid4()),  # Ensure unique ID
                patient_id=patient_id,
                patient_name=patient.name,
                doctor_id=session['user_id'],
                doctor_name=session['user_name'],  # Assuming session contains doctor info
                diagnosis=request.form.get('diagnosis'),  # Optional: Add more fields
                comments=request.form.get('comments'),
                details=prescription_details
            )
            
            # Save to database
            db.session.add(new_prescription)
            db.session.commit()
            
            flash("Prescription created successfully.", "success")
            return redirect(url_for('doctor.doctor_dashboard'))

        except Exception as e:
            db.session.rollback()  # Roll back in case of error
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('doctor.create_prescription'))
    
    # Render the prescription creation form
    return render_template('doctors/create_prescription.html')

@doctor_bp.route('/scan_qr', methods=['GET'])
def scan_qr_page():
    """
    Serve the QR code scanning page.
    """
    return render_template('scan_qr.html')

@doctor_bp.route('/view_appointments')
def view_appointments():
    try:
        # Fetch the doctor's email from the session
        doctor_email = session['email']

        # Fetch the doctor based on the email from session
        doctor = Doctor.query.filter_by(email_id=doctor_email).first()

        if not doctor:
            print("Doctor not found!")
            flash("Doctor not found.", "danger")
            return redirect(url_for('auth.doctor_dashboard'))  # Redirect to the dashboard if doctor not found
        
        # Fetch appointments for a specific doctor
        appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
        # appointments1 = Appointment.query.filter_by(patient_id=PatientRecord.id).all()
        # print(appointments1)

        patient_ids = set([appointment.patient_id for appointment in appointments])

        # Fetch patient records for those IDs
        patients = {patient.id: patient.name for patient in PatientRecord.query.filter(PatientRecord.id.in_(patient_ids)).all()}

        # Map patient names to their respective appointments
        for appointment in appointments:
            appointment.patient_name = patients.get(appointment.patient_id, "Unknown")  # Add patient name or "Unknown"

        print(appointments)
        return render_template('doctors/view_appointments.html', appointments=appointments)

    except Exception as e:
        flash(f"An error occurred while fetching appointments: {str(e)}", "danger")
        print(f"An error occurred while fetching appointments: {str(e)}")
        return redirect(url_for('auth.doctor_dashboard'))  # Redirect to dashboard on error
    
import os
from werkzeug.utils import secure_filename

@doctor_bp.route('/scan_appointment', methods=['POST'])
def scan_appointment():
    print("In scan_appointment")

    # Check if the file is present
    if 'qr_code' in request.files:
        file = request.files['qr_code']
        if file.filename == '':
            flash('No file selected.', 'danger')
            print("No file selected.")
            return redirect(url_for('doctor_bp.scan_qr_page'))

        if file:
            try:
                # Ensure uploads directory exists
                uploads_dir = os.path.join('app', 'static', 'uploads')
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)

                # Save the file temporarily
                filename = secure_filename(file.filename)
                temp_path = os.path.join(uploads_dir, filename)
                file.save(temp_path)
                print(f"File saved temporarily at: {temp_path}")

                # Load the image and decode the QR code using pyzbar
                image = Image.open(temp_path)
                qr_code_data = decode(image)

                if not qr_code_data:
                    flash('Invalid or unreadable QR code.', 'danger')
                    print("QR code not readable.")
                    return redirect(url_for('doctor_bp.scan_qr_page'))

                # Extract the data from the QR code
                parsed_data = qr_code_data[0].data.decode('utf-8').strip()
                print(f"Parsed data from QR code: {parsed_data}")
                lines = parsed_data.split('\n')
                appointment_id = lines[0].split(': ')[1]
                print(f"Appointment ID extracted: {appointment_id}")

                # Fetch the appointment from the database
                appointment = Appointment.query.filter_by(id=appointment_id).first()
                print(f"Appointment fetched from DB: {appointment}")

                if not appointment:
                    flash('No appointment found for the provided QR code.', 'danger')
                    print("No appointment found for the given ID.")
                    return redirect(url_for('doctor_bp.scan_qr_page'))

                if appointment.status == "Done":
                    flash('This appointment is already marked as done. No further scanning is required.', 'info')
                    print("Appointment already marked as 'Done'.")
                    return redirect(url_for('doctor_bp.scan_qr_page'))

                # If no charges are provided yet, display appointment details page
                return render_template('appointment_details.html', appointment=appointment)

            except Exception as e:
                print(f"Error processing QR code: {e}")
                flash(f"An error occurred while processing the QR code: {str(e)}", 'danger')
                return redirect(url_for('doctor_bp.scan_qr_page'))

    # If charges are provided in the form, update the appointment
    charges = request.form.get('charges')
    if charges:
        try:
            charges = float(charges)
            print(f"Charges input by doctor: {charges}")

            # Fetch the appointment again (by ID from the hidden field)
            appointment_id = request.form.get('appointment_id')
            appointment = Appointment.query.filter_by(id=appointment_id).first()

            if not appointment:
                flash('No appointment found.', 'danger')
                return redirect(url_for('doctor_bp.scan_qr_page'))

            # Update the charges and mark the appointment as 'Done'
            appointment.charges = charges
            appointment.status = 'Done'
            db.session.commit()  # Commit the changes to the database
            flash('Charges saved successfully and appointment marked as done.', 'success')
            print("Charges saved and appointment status updated.")
            
            # Redirect to the list of appointments
            return redirect(url_for('doctor_bp.view_appointments'))  # Redirect to the list of appointments

        except ValueError:
            flash('Invalid charge amount entered. Please enter a valid number.', 'danger')
            print("Invalid charge amount entered.")

    # If no charges are provided, show the appointment details page again
    flash('Unexpected error occurred. Please try again.', 'danger')
    return redirect(url_for('doctor_bp.scan_qr_page'))





@doctor_bp.route('/view_appointment/<int:appointment_id>', methods=['GET'])
def view_appointment(appointment_id):
    """
    Fetch and display appointment details.
    """
    try:
        # Fetch appointment details from the database
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        # Example: Update the appointment status
        appointment.status = "Viewed"  # Mark the appointment as viewed
        db.session.commit()

        # Render the appointment details
        return render_template('view_appointment.html', appointment=appointment)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

