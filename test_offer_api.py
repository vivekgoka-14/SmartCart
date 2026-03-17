from flask import Flask
from flask_mail import Mail, Message
from pymongo import MongoClient

app = Flask(__name__)
# Load config from app.py values (as seen in previous view_file)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gokavivek@gmail.com'
app.config['MAIL_PASSWORD'] = 'cihgymlwvvuxsjt'
app.config['MAIL_DEFAULT_SENDER'] = 'gokavivek@gmail.com'
mail = Mail(app)

def test_offer_broadcast():
    with app.app_context():
        try:
            # We'll just try to send a test message to the sender themselves to verify connectivity
            msg = Message(subject="Test Offer", recipients=['gokavivek@gmail.com'], body="This is a test broadcast message.")
            mail.send(msg)
            print("Offer broadcast connection test: SUCCESS")
        except Exception as e:
            print(f"Offer broadcast connection test: FAILED - {e}")

if __name__ == "__main__":
    test_offer_broadcast()
