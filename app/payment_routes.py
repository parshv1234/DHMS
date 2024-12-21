from flask import Blueprint, request, jsonify, render_template, current_app
from app import db
from app.models import Payment, Appointment
import razorpay
import logging
from datetime import datetime

payment_bp = Blueprint('payment_bp', __name__, template_folder='templates/patients')

logging.basicConfig(level=logging.DEBUG, filename='debug.log')
logging.basicConfig(level=logging.ERROR, filename='payment_errors.log')

def get_razorpay_client():
    """Initialize Razorpay client within the app context."""
    return razorpay.Client(
        auth=(
            current_app.config['RAZORPAY_KEY_ID'],
            current_app.config['RAZORPAY_KEY_SECRET']
        )
    )

@payment_bp.route('/get_razorpay_key', methods=['GET'])
def get_razorpay_key():
    print("get_razorpay_key endpoint hit")
    return jsonify({'razorpay_key': current_app.config['RAZORPAY_KEY_ID']})


@payment_bp.route('/get_amount', methods=['GET'])
def get_amount():
    patient_id = request.args.get('patient_id')
    doctor_id = request.args.get('doctor_id')

    if not patient_id or not doctor_id:
        return jsonify({'error': 'Patient ID and Doctor ID are required'}), 400

    appointment = Appointment.query.filter_by(patient_id=patient_id, doctor_id=doctor_id, status='Done').first()

    if not appointment:
        return jsonify({'error': 'Appointment not found or not completed'}), 404

    return jsonify({'amount': appointment.charges}), 200


@payment_bp.route('/create_payment', methods=['GET', 'POST'])
def create_payment():
    if request.method == 'POST':
        try:
            # Get the patient ID and doctor ID from the request
            data = request.get_json()
            patient_id = data.get('patient_id')
            doctor_id = data.get('doctor_id')

            if not doctor_id:
                return jsonify({'error': 'Doctor ID is required'}), 400

            # Fetch the appointment using the patient_id and doctor_id (or other identifiers)
            appointment = Appointment.query.filter_by(patient_id=patient_id, doctor_id=doctor_id, status="Done").first()

            if not appointment:
                return jsonify({'error': 'No appointment found for the provided patient and doctor'}), 404

            # Get the amount (charges) directly from the appointment
            amount = appointment.charges

            if not amount:
                return jsonify({'error': 'No charges found for the appointment'}), 400

            try:
                # Initialize Razorpay client
                razorpay_client = get_razorpay_client()
                razorpay_order = razorpay_client.order.create({
                    "amount": int(amount * 100),  # Convert amount to paise
                    "currency": "INR",
                    "payment_capture": 1
                })

                # Create a payment record
                payment = Payment(
                    id=razorpay_order['id'],
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    amount=amount,
                    admin_share=amount * 0.3,
                    doctor_share=amount * 0.7,
                    payment_status='Pending'
                )
                db.session.add(payment)
                db.session.commit()

                # Return the payment URL
                return jsonify({
                    'payment_url': f"https://rzp.io/l/{razorpay_order['id']}",
                    'payment_id': razorpay_order['id']
                }), 200

            except Exception as e:
                db.session.rollback()
                logging.error(f"Error creating payment: {str(e)}")
                return jsonify({'error': 'Payment creation failed'}), 500

        except Exception as e:
            logging.error(f"Error in payment creation: {str(e)}")
            return jsonify({'error': 'Missing or invalid data'}), 400
    else:
        return render_template('payment.html')



@payment_bp.route('/payment_callback', methods=['POST'])
def payment_callback():
    if request.method == 'POST':
        try:
            # Fetch parameters from the Razorpay response
            payment_id = request.form.get('razorpay_payment_id')
            razorpay_order_id = request.form.get('razorpay_order_id')
            signature = request.form.get('razorpay_signature')

            # Log the received parameters for debugging
            logging.debug(f"Received Callback: payment_id={payment_id}, order_id={razorpay_order_id}, signature={signature}")

            # Prepare a dictionary for signature verification
            params = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify the signature with Razorpay
            razorpay_client = get_razorpay_client()
            razorpay_client.utility.verify_payment_signature(params)

            # Fetch the payment record from your database
            payment = Payment.query.filter_by(id=razorpay_order_id).first()
            if not payment:
                logging.error(f"Payment record not found for order_id={razorpay_order_id}")
                return jsonify({"error": "Payment record not found!"}), 404

            # Check if the payment status is already updated to 'Paid'
            if payment.payment_status == 'Paid':
                logging.info(f"Payment with order_id={razorpay_order_id} already marked as paid.")
                return jsonify({"status": "success", "message": "Payment already processed."})

            # Update payment status after successful verification
            payment.payment_status = "Paid"
            payment.payment_date = datetime.utcnow()
            db.session.commit()
            logging.info(f"Payment status updated to 'Paid' for order_id={razorpay_order_id}")

            # Respond to Razorpay with a success message
            return jsonify({"status": "success", "message": "Payment successful!"})

        except razorpay.errors.SignatureVerificationError:
            logging.error(f"Signature verification failed for order_id={razorpay_order_id}")
            return jsonify({"error": "Signature verification failed!"}), 400
        except Exception as e:
            logging.error(f"Error processing payment callback: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500



@payment_bp.route('/patient_payments', methods=['GET'])
def patient_payments():
    patient_id = request.args.get('patient_id')

    if not patient_id:
        return jsonify({'error': 'Patient ID is required. Ensure it is included in the URL query parameters.'}), 400

    payments = Payment.query.filter_by(patient_id=patient_id).all()
    payment_history = [{
        'payment_id': p.id,
        'doctor_id': p.doctor_id,
        'amount': p.amount,
        'status': p.payment_status,
        'date': p.payment_date
    } for p in payments]

    return jsonify(payment_history), 200
