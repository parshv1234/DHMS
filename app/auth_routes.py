from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from app import db
from app.models import User, Doctor, PatientRecord, Appointment
from werkzeug.security import generate_password_hash, check_password_hash
from utils.otp import generate_otp, send_otp, verify_otp  # Corrected import for OTP sending
from datetime import datetime, timedelta
from utils.rbac import role_required

auth_bp = Blueprint('auth', __name__, template_folder='templates/auth')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle form data from the frontend
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')

        print(f"Received data: username={username}, email={email}, phone={phone}, password={password}")

        # Check if all fields are filled
        if not username or not email or not phone or not password:
            flash('All fields are required.', 'danger')
            return jsonify({"error": "All fields are required."}), 400

        hashed_password = generate_password_hash(password)

        # Check if user already exists
        existing_user = User.query.filter((User.email == email) | (User.phone == phone)).first()
        if existing_user:
            flash('User with this email or phone already exists.', 'danger')
            return jsonify({"error": "User with this email or phone already exists."}), 400

        # Create new user
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            password=hashed_password,
            role="patient",  # Assign the selected role
            is_verified=False  # OTP will be used for verification
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please verify your email.', 'success')

        # Generate OTP and send email
        otp = generate_otp()
        print(otp)
        if send_otp(email, otp):
            session['email'] = email  # Store email in session for later OTP verification
            return jsonify({"message": "Redirecting to verify otp..."})  # Ensure this route exists
        else:
            flash("Error sending OTP. Please try again.")
            return jsonify({"error": "Error sending OTP."}), 500

    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Check if it's a POST request
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Check if the user exists in User or Doctor tables
        user = User.query.filter_by(email=email).first() or Doctor.query.filter_by(email_id=email).first()

        if user:
            # Check password validity
            valid_password = False
            if isinstance(user, User) and check_password_hash(user.password, password):
                valid_password = True
            elif isinstance(user, Doctor) and user.check_password(password):
                valid_password = True

            if valid_password:
                otp = generate_otp()
                print(f"Generated OTP: {otp}")

                # Send OTP and save session details
                if send_otp(email, otp):
                    # Save user email and role in the session for OTP verification
                    session['email'] = email
                    session['role'] = user.role if hasattr(user, 'role') else 'doctor'

                    return jsonify({
                        "message": "OTP sent to email. Please verify."
                    }), 200
                else:
                    flash("Error sending OTP. Please try again.")
                    return jsonify({"error": "Error sending OTP."}), 400
            else:
                flash("Invalid password.")
                return jsonify({"error": "Invalid password."}), 400
        else:
            flash("Invalid email.")
            return jsonify({"error": "Invalid email."}), 400

    # Handle GET request: render the login template
    return render_template('auth/login.html')


# Updated Verify Login OTP Route
@auth_bp.route('/verify_login_otp', methods=['GET', 'POST'])
def verify_login_otp():
    user = None

    if request.method == 'POST':
        email = session.get('email')
        if not email:
            flash("Session expired. Please login again.")
            return redirect(url_for('auth.login'))

        # Fetch the user from the database
        user = User.query.filter_by(email=email).first() or Doctor.query.filter_by(email_id=email).first()

        user_otp = request.json.get('otp')
        if user_otp:
            is_valid, message = verify_otp(email, user_otp)
            if is_valid:
                flash("OTP verified successfully!")

                if user:
                    user.is_verified = True
                    db.session.commit()

                    # Determine the redirect URL based on role and patient record
                    redirect_url = None
                    if isinstance(user, User):
                        if user.role == 'admin':
                            redirect_url = url_for('auth.admin_dashboard')
                        elif user.role == 'patient':
                            # Check if patient record exists
                            is_patient_record = PatientRecord.query.filter_by(email_id=email).first()
                            if not is_patient_record:
                                redirect_url = url_for('patient.register_patient')
                            else:
                                redirect_url = url_for('auth.patient_dashboard')
                    elif isinstance(user, Doctor):
                        session['authenticated'] = True
                        redirect_url = url_for('auth.doctor_dashboard')

                    if redirect_url:
                        return jsonify({"success": True, "redirect_url": redirect_url})
                    else:
                        flash("Unknown user role.")
                        return jsonify({"success": False, "message": "Unknown user role."})
                else:
                    flash("User not found.")
                    return jsonify({"success": False, "message": "User not found."})

    return render_template('auth/verify_login_otp.html', user_role=user.role if user else None)

# OTP Verification Route for Forgot Password
@auth_bp.route('/verify_reset_otp', methods=['GET', 'POST'])
def verify_reset_otp():
    email = session.get('user_email')
    user = User.query.filter(User.email == email).first()
    if request.method == 'POST':
        # Get email from session
        data = request.get_json()
        user_otp = data.get("otp")

        if email:
            is_valid, message = verify_otp(email, user_otp)
            if is_valid:
                # Retrieve user from the database using the email
                if user:
                    flash("OTP verified successfully! You can now reset your password.")
                    session['usersId'] = user.id  # Store user_id in session for later use
                    return redirect(url_for('auth.reset_password', user_id=user.id))  # Dynamically include user_id
                else:
                    flash("User not found. Please try again.")
                    return redirect(url_for('auth.forgot_password'))
            else:
                flash(message=message)
        else:
            flash("Invalid OTP. Please try again.")

    if not user:
        flash("User not found or session expired. Please login again.")
        return redirect(url_for('auth.forgot_password'))  # Redirect to forgot-password page if user not found

    return render_template('auth/verify_reset_otp.html', user_id=user.id)


# Forgot Password route
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email_or_phone = data.get('email_or_phone')

        if not email_or_phone:
            flash('Please enter your email or phone number.', 'danger')
            return redirect(url_for('auth.verify_reset_otp'))

        # Check if the user exists in the database by email or phone
        user = User.query.filter((User.email == email_or_phone) | (User.phone == email_or_phone)).first()
        if user:
            # Generate OTP for password reset
            otp = generate_otp()
            print("OTP:",otp)
            user.otp = otp
            user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)  # Set OTP expiry time
            db.session.commit()

            session['user_email'] = user.email
            print(session['user_email'])
            # Send OTP to the email
            if send_otp(user.email, otp):  
                flash('OTP sent to your email. Please verify to reset your password.', 'info')
                return redirect(url_for('auth.verify_reset_otp', user_id=user.id))  # Redirect to OTP verification for reset
            else:
                flash('Error sending OTP. Please try again.', 'danger')
        else:
            flash('User not found. Please try again with valid email or phone.', 'danger')

    return render_template('auth/forgot-password.html')


# Reset Password Route
@auth_bp.route('/reset-password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        new_password = data.get('password')
        confirm_password = data.get('confirmPassword')

        if new_password != confirm_password:
            return jsonify({"error": "Passwords do not match."}), 400

        hashed_password = generate_password_hash(new_password)
        user.password = hashed_password
        user.otp = None
        db.session.commit()

        return jsonify({"message": "Password reset successfully."}), 200

    return render_template('auth/reset_password.html', user_id=user_id)

# Resend OTP Route
@auth_bp.route('/resend_otp', methods=['GET','POST'])
def resend_otp():
    email = session.get('user_email')  # Retrieve email from session
    print(email)
    if not email:
        flash('Session expired. Please login again.', 'danger')
        return jsonify({"error": "Session expired. Please login again."}), 401

    # Check if the user exists
    user = User.query.filter_by(email=email).first() or Doctor.query.filter_by(email_id=email).first()
    if not user:
        flash('User not found.', 'danger')
        return jsonify({"error": "User not found."}), 404

    # Generate new OTP
    otp = generate_otp()
    print(f"Resending OTP: {otp}")  # For debugging purposes

    # Update OTP and expiry if needed
    if hasattr(user, 'otp'):  # Ensure compatibility with the Doctor model
        user.otp = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()

    # Send OTP to the user's email
    if send_otp(email, otp):
        flash('OTP resent to your email.', 'info')
        return jsonify({"message": "OTP resent to your email."}), 200
    # else:
    #     flash('Error resending OTP. Please try again.', 'danger')
    #     return jsonify({"error": "Error resending OTP."}), 500
    return render_template('auth/resend_otp.html')



# Admin Dashboard Route
@auth_bp.route('/dashboard')
def admin_dashboard():
    doctor_count = Doctor.query.count()
    patient_count = PatientRecord.query.count()
    appointment_count = Appointment.query.filter_by(status='Pending').count()
    
    
    view_doctor_url = url_for('doctor_bp.view_doctors')  # Adjust 'doctor_bp.view_doctor' to match your blueprint and function name
    return render_template('admin/admin_dashboard.html',
                         doctor_count=doctor_count,
                         patient_count=patient_count,
                         appointment_count=appointment_count, view_doctor_url=view_doctor_url)


# Doctor Dashboard Route
@auth_bp.route('/doctor/dashboard', methods=['GET'])
@role_required('doctor')
def doctor_dashboard():
    doctor_email = session['email']
    doctor = Doctor.query.filter_by(email_id=doctor_email).first()
     
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    # Collect unique patient IDs from the appointments
    doctor_ids = set([appointment.doctor_id for appointment in appointments])  # Unique IDs
    doctors = Doctor.query.filter(Doctor.id.in_(doctor_ids)).all()
    # Display patient names
    if doctors:
        print("Patients associated with this doctor:")
        for doctor in doctors:
            print(f"Doctor Name: {doctor.name}, Patient ID: {doctor.id}")
    else:
        print("No patients found in the database.")

    return render_template('auth/doctor_dashboard.html', doctor_name=doctor.name)

# Patient Dashboard Route
@auth_bp.route('/patient/dashboard')
def patient_dashboard():
    patient_email = session['email']
    patient = PatientRecord.query.filter_by(email_id=patient_email).first()

    if patient:
        print(f"Patient Name: {patient.name}")
    else:
        print("No patient found with the provided email.")

    return render_template('auth/patient_dashboard.html',patient_name=patient.name)
