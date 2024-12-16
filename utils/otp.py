import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import time

# Email configuration (You can use Gmail's SMTP server for example)
EMAIL_HOST = 'smtp.gmail.com'  # For Gmail
EMAIL_PORT = 587  # For Gmail
SENDER_EMAIL = 'parshv.23bce10807@vitbhopal.ac.in'  # Replace with your email
SENDER_PASSWORD = 'fmqs jhlk njnt ienw'  # Replace with your email password

# OTP expiry time (30 seconds)
OTP_EXPIRY_TIME = 30

# Global dictionary to store OTP data
otp_data = {}

def generate_otp(length=6):
    """Generate a random OTP."""
    otp = ''.join(random.choices(string.digits, k=length))
    return otp

def send_otp(email, otp):
    """Send OTP via email."""
    try:
        # Set up the MIME
        message = MIMEMultipart()
        message['From'] = SENDER_EMAIL
        message['To'] = email
        message['Subject'] = 'Your OTP for DHMS Login'

        # OTP creation time
        otp_data[email] = {
            "otp": otp,
            "time_created": time.time()
        }

        # Email body content with HTML styling
        body = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f7fc;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #ffffff;
                        border-radius: 8px;
                        padding: 20px;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                        width: 80%;
                        max-width: 400px;
                        margin: 0 auto;
                    }}
                    h2 {{
                        color: #6a11cb;
                    }}
                    p {{
                        font-size: 16px;
                        color: #333333;
                    }}
                    .otp {{
                        background-color: #6a11cb;
                        color: #ffffff;
                        padding: 10px;
                        border-radius: 5px;
                        font-size: 20px;
                        text-align: center;
                        font-weight: bold;
                    }}
                    .footer {{
                        font-size: 12px;
                        color: #777777;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Your OTP for DHMS Login</h2>
                    <p>Hi there,</p>
                    <p>We received a request to log into the DHMS system. Use the OTP below to continue:</p>
                    <div class="otp">{otp}</div>
                    <p>This OTP is valid for 30 seconds. Please use it before it expires.</p>
                    <p>If you didn't request this, you can ignore this email.</p>
                    <p class="footer">If you have any questions, feel free to reach out to our support team.</p>
                </div>
            </body>
        </html>
        """

        # Attach the HTML body to the message
        message.attach(MIMEText(body, 'html'))

        # Connect to Gmail's SMTP server
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Send email
        text = message.as_string()
        server.sendmail(SENDER_EMAIL, email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def verify_otp(email, user_otp):
    """Verify if the OTP is correct and still valid."""
    if email not in otp_data:
        return False, "OTP has not been generated."
    
    otp_info = otp_data[email]
    otp = otp_info["otp"]
    time_created = otp_info["time_created"]
    
    # Check if OTP is expired
    if time.time() - time_created > OTP_EXPIRY_TIME:
        return False, "OTP expired. Please request a new one."
    
    # Check if OTP matches
    if user_otp == otp:
        return True, "OTP verified successfully!"
    else:
        return False, "Invalid OTP. Please try again."
