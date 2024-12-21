from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Patient Record Model
class PatientRecord(db.Model):
    __tablename__ = 'patient_record'

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact_number_1 = db.Column(db.String(20), nullable=False)
    contact_number_2 = db.Column(db.String(20))
    email_id = db.Column(db.String(100), nullable=False)  # Removed unique constraint
    address = db.Column(db.String(250), nullable=True)
    next_of_kin_name = db.Column(db.String(100), nullable=False)
    next_of_kin_relation_to_patient = db.Column(db.String(50), nullable=False)
    next_of_kin_contact_number = db.Column(db.String(20), nullable=False)
    qr_code_path = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<Patient {self.name}>'

class Doctor(db.Model):
    __tablename__ = 'doctor_record'
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.String(10), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    department_id = db.Column(db.String(20), db.ForeignKey('department.id'), nullable=False)
    department_name = db.Column(db.String(100), nullable=False)
    contact_number_1 = db.Column(db.String(15), nullable=False)
    contact_number_2 = db.Column(db.String(15), nullable=True)
    aadhar_or_voter_id = db.Column(db.String(20), nullable=False)
    email_id = db.Column(db.String(100), unique=True, nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    specialisation = db.Column(db.String(100), nullable=False)
    years_of_experience = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Doctor {self.name}>'
    
    def is_active(self):
        return True
    
    def get_id(self):
        return self.id
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    @staticmethod
    def calculate_age(dob):
        today = datetime.today()
        dob_date = datetime.strptime(dob, '%Y-%m-%d')
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        return age

class Department(db.Model):
    __tablename__ = 'department'
    
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500))
    head_doctor_id = db.Column(db.String(20), db.ForeignKey('doctor_record.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctors = db.relationship('Doctor', backref='department', foreign_keys='Doctor.department_id')
    head_doctor = db.relationship('Doctor', backref='headed_department', foreign_keys=[head_doctor_id], post_update=True)
    
    def __repr__(self):
        return f'<Department {self.name}>'
    
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(255), nullable=False)
    otp = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.email}>'
    
class PrescriptionRecord(db.Model):
    __tablename__ = 'prescription_record'

    id = db.Column(db.String, primary_key=True)
    patient_id = db.Column(db.String, db.ForeignKey('patient_record.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    patient_name = db.Column(db.String, nullable=False)
    doctor_id = db.Column(db.String, db.ForeignKey('doctor_record.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    doctor_name = db.Column(db.String, nullable=False)
    diagnosis = db.Column(db.String)
    comments = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Medicine details
    medicine_1_name = db.Column(db.String)
    medicine_1_dosage_description = db.Column(db.String)
    medicine_2_name = db.Column(db.String)
    medicine_2_dosage_description = db.Column(db.String)
    medicine_3_name = db.Column(db.String)
    medicine_3_dosage_description = db.Column(db.String)

    # Define relationships
    patient = db.relationship('PatientRecord', backref='prescriptions')
    doctor = db.relationship('Doctor', backref='prescriptions')

    def __repr__(self):
        return f"<PrescriptionRecord {self.id}, Patient: {self.patient_name}, Doctor: {self.doctor_name}>"
    
class Appointment(db.Model):
    __tablename__ = 'appointment_record'

    id = db.Column(db.String(36), primary_key=True)
    patient_id = db.Column(db.String, db.ForeignKey('patient_record.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    doctor_id = db.Column(db.String, db.ForeignKey('doctor_record.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='Pending', nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    charges = db.Column(db.Float, nullable=True)  # New column to store charges

    # Relationships
    patient = db.relationship('PatientRecord', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

    def __repr__(self):
        return f"<Appointment {self.id}, Patient: {self.patient_id}, Doctor: {self.doctor_id}>"

class MedicalTest(db.Model):
    __tablename__ = 'medical_test'

    id = db.Column(db.String(36), primary_key=True)
    patient_id = db.Column(db.String, db.ForeignKey('patient_record.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    doctor_id = db.Column(db.String, db.ForeignKey('doctor_record.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    test_description = db.Column(db.Text)
    test_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Requested', nullable=False)
    results = db.Column(db.Text)
    result_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = db.relationship('PatientRecord', backref='medical_tests')
    doctor = db.relationship('Doctor', backref='ordered_tests')

    def __repr__(self):
        return f"<MedicalTest {self.id}, Patient: {self.patient_id}, Test: {self.test_name}>"
    
class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True)  # Payment ID from Razorpay/Stripe
    patient_id = db.Column(db.String, db.ForeignKey('patient_record.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    doctor_id = db.Column(db.String, db.ForeignKey('doctor_record.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    admin_share = db.Column(db.Float, nullable=False)
    doctor_share = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='Pending')  # E.g., 'Completed', 'Failed'
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('PatientRecord', backref='payments')
    doctor = db.relationship('Doctor', backref='payments')

    def __repr__(self):
        return f"<Payment {self.id}, Patient: {self.patient_id}, Doctor: {self.doctor_id}>"
