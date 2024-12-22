from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask, jsonify, session
from app.__init__ import db, mail
from app.models import PatientRecord, Appointment  # Import the model for patient record
from flask_mail import Message
import logging
from flask import request, redirect, flash
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from utils.rbac import role_required
import qrcode
from PIL import Image, ImageDraw, ImageFont
import uuid
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError

# Define the blueprint for the routes
patient_bp = Blueprint('patient', __name__, template_folder='templates/patients')  

def generate_qr_code(data, file_path, logo_path=None, name=None, contact_number=None, patients_id=None):
    # Create QR code instance with higher error correction level
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Increased error correction
        box_size=10,
        border=4,
    )
    
    # Prepare the data for QR code, including patient details
    qr_data = f"ID: {patients_id}\nName: {name}\nContact: {contact_number}"
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Set QR code colors
    fill_color = "darkblue"  # Dark blue for better contrast
    back_color = "white"  # White background for a clean look
    img = qr.make_image(fill=fill_color, back_color=back_color).convert("RGBA")
    qr_width, qr_height = img.size

    # Add logo if available and make sure it's not too large
    if logo_path:
        try:
            logo = Image.open(logo_path).convert("RGBA")  # Ensure the logo has an alpha channel (transparency)
            logo = logo.resize((qr_width // 4, qr_height // 4), Image.Resampling.LANCZOS)  # Resize logo to 25% of QR size
            logo_position = ((qr_width - logo.size[0]) // 2, (qr_height - logo.size[1]) // 2)  # Center the logo
            img.paste(logo, logo_position, logo)  # Use the alpha channel to paste with transparency
        except Exception as e:
            print(f"Error adding logo: {e}")

    # Prepare the "Hospital" text to be added below the QR code
    hospital_text = "DHMS  Hospital"
    
    # Add red-colored "Hospital" text below the QR code
    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)

    try:
        # Use a large font for the "Hospital" text below the QR code
        font = ImageFont.truetype("/Users/parshv/Documents/Ticket/Monarda.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    # Calculate the position of the "Hospital" text below the QR code
    text_bbox = draw.textbbox((0, 0), hospital_text, font=font)  # Get bounding box for text
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[-1]
    text_position = ((qr_width - text_width) // 2, qr_height - 35)  # Positioned just below QR code

    # Resize canvas to fit text
    new_img = Image.new("RGBA", (qr_width, qr_height + 75), "white")
    new_img.paste(img, (0, 0))
    draw = ImageDraw.Draw(new_img)
    draw.text(text_position, hospital_text, font=font, fill="red")

    # Save the final image with QR code, logo, and details
    new_img.save(file_path)
    print(f"QR code saved as {file_path}")

def generate_aqr_code(data, file_path, logo_path=None):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="darkblue", back_color="white").convert("RGBA")
    img.save(file_path)

# Register patient route
@patient_bp.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        # Get the form data
        try:
            # Get the form data from the request
            data = request.get_json()

            if not data:
                return jsonify({'error': 'Invalid request. No data provided.'}), 400

            # Extract patient details from the form
            patient_id = str(uuid.uuid4())  # Generate a unique ID for the patient
            name = data.get('name')
            age = data.get('age')
            gender = data.get('gender')
            contact_number_1 = data.get('contact_number_1')
            contact_number_2 = data.get('contact_number_2')
            email_id = data.get('email_id')
            address = data.get('address')
            next_of_kin_name = data.get('next_of_kin_name')
            next_of_kin_relation_to_patient = data.get('next_of_kin_relation_to_patient')
            next_of_kin_contact_number = data.get('next_of_kin_contact_number')

            # Validate required fields
            if not all([name, age, gender, contact_number_1, email_id, address, next_of_kin_name, next_of_kin_contact_number]):
                return jsonify({'error': 'All required fields must be filled.'}), 400

            # Define QR code file path
            qr_code_path = f"app/static/qrcodes/{patient_id}.png"  # Path for QR code
            logo_path = "app/static/logo2.png"  # Path to logo file for QR code

            # Save patient details to the database
            new_patient = PatientRecord(
                id=patient_id,
                name=name,
                age=age,
                gender=gender,
                contact_number_1=contact_number_1,
                contact_number_2=contact_number_2,
                email_id=email_id,
                address=address,
                next_of_kin_name=next_of_kin_name,
                next_of_kin_relation_to_patient=next_of_kin_relation_to_patient,
                next_of_kin_contact_number=next_of_kin_contact_number,
                qr_code_path=qr_code_path
            )

            db.session.add(new_patient)
            db.session.commit()

            # Generate the QR code
            generate_qr_code(
                patient_id,
                qr_code_path,
                logo_path,
                name=name,
                contact_number=contact_number_1,
                patients_id=patient_id
            )

            # Send the QR code via email
            send_email_with_qr(email_id, qr_code_path)

            return jsonify({'message': 'Patient registered successfully.'}), 200

        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    return render_template('register_patient.html')

@patient_bp.route('/create_appointment', methods=['GET', 'POST'])
def create_appointment():
    if request.method == 'POST':
        data = request.form
        # Get patient email from session
        patient_email = session.get("email")
        patient = PatientRecord.query.filter_by(email_id=patient_email).first()
        try:   
            if not patient:
                flash('Patient not found.', 'error')
                return redirect(url_for('patient.create_appointment'))
           
            # Extract form data
            doctor_id = data.get('doctor_id')
            appointment_date = data.get('appointment_date')
            appointment_time = data.get('appointment_time')
            reason = data.get('reason')

            # Validate input
            if not all([doctor_id, appointment_date, appointment_time, reason]):
                flash('All fields are required.', 'error')
                return redirect(url_for('patient.create_appointment'))
                
            # Create a new appointment
            appointment_id = str(uuid.uuid4())
            new_appointment = Appointment(
                id=appointment_id,
                patient_id=patient.id,
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason
            )
            db.session.add(new_appointment)
            db.session.commit()

            # Generate QR code for the appointment
            qr_code_path = f"app/static/qrcodes/appointment_{appointment_id}.png"
            print(f"Appointment ID: {appointment_id}\nPatient Name: {patient.name}\nDoctor ID: {doctor_id}\nDate: {appointment_date}\nTime: {appointment_time}\nReason: {reason}")

            qr_data = f"Appointment ID: {appointment_id}\nPatient Name: {patient.name}\nDoctor ID: {doctor_id}\nDate: {appointment_date}\nTime: {appointment_time}\nReason: {reason}"
            generate_aqr_code(qr_data, qr_code_path)

            # Send the QR code via email
            send_email_with_qr(patient.email_id, qr_code_path)

            flash('Appointment created successfully! The QR code has been sent to your email.', 'success')
            return redirect(url_for('auth.patient_dashboard'))
            
                
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('patient.create_appointment'))
        
    # Fetch doctors for the dropdown
    doctors = db.session.execute(text("SELECT id, name FROM doctor_record")).fetchall()
    # patients= db.session.execute(
    #     text("SELECT name FROM users WHERE email = :email_id_"),
    #     {'email_id_': patient_email}
    # ).fetchall()
    patient_email = session.get("email")
    patient_name_ = db.session.query(PatientRecord.name).filter_by(email_id=patient_email).first()
    return render_template('patients/create_appointment.html', doctors=doctors, patient_name=patient_name_[0])

@patient_bp.route('/view_appointments', methods=['GET'])
def view_appointments():
    try:
        # Get patient email from session
        patient_email = session.get("email")
        patient = PatientRecord.query.filter_by(email_id=patient_email).first()

        if not patient:
            flash('Patient not found.', 'error')
            return redirect(url_for('patient.view_appointments'))
        if patient:
            print(f"Patient Name: {patient.name}")
            
            # Fetch appointments for the logged-in patient
            appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.appointment_date.desc()).all()

            return render_template('patients/view_appointments.html', appointments=appointments, today=datetime.today(),patient_name=patient.name)
        else:
            print("No patient found with the provided email.")
    except Exception as e:
        print(f"Error retrieving appointments: {str(e)}", 'error')
        return redirect(url_for('patient.view_appointments'))


# Function to generate the QR code with patient details and logo

def send_email_with_qr(email, qr_code_path):
    # Set up logging configuration
    logging.basicConfig(
        filename='email_log.txt',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
)
    # Create the email message
    msg = Message(
        subject='Patient Registered Successfully',
        recipients=[email],
        sender='parshv.23bce10807@vitbhopal.ac.in'
    )

    # HTML content for the email body
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #4CAF50; text-align: center;">DHMS Hospital</h2>
                <p>Dear Patient,</p>
                <p>Your QR code has been successfully generated. Please find the QR code attached below. This QR code will be used for accessing your patient records and other services at DHMS Hospital.</p>
                <p>If you have any questions, feel free to contact us.</p>
                <div style="text-align: center; margin-top: 20px;">
                    <img src="cid:qr_code_image" alt="QR Code" style="max-width: 200px; border: 1px solid #ddd; border-radius: 10px;">
                </div>
                <p style="text-align: center; color: #888;">Thank you for choosing DHMS Hospital.</p>
                <hr style="border: none; border-top: 1px solid #eee;">
                <p style="text-align: center; font-size: 12px; color: #888;">&copy; 2024 DHMS Hospital. All rights reserved.</p>
            </div>
        </body>
    </html>
    """

    try:
        # Attach the HTML content to the email
        msg.html = html_body

        # Attach the QR code image with Content-ID for inline display
        with open(qr_code_path, 'rb') as qr_file:
            msg.attach(f"qr_code_{uuid.uuid4()}.png", "image/png", qr_file.read(), headers={'Content-ID': '<qr_code_image>'})

        # Send the email
        mail.send(msg)
        logging.info(f"Email successfully sent to {email}")
        flash("Email sent successfully!", "success")
    except Exception as e:
        logging.error(f"Error sending email to {email}: {e}")
        flash("Failed to send email. Please try again later.", "error")
