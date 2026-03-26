from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gokavivek@gmail.com'
app.config['MAIL_PASSWORD'] = 'nldhdgdjqxptgpxu'
app.config['MAIL_DEFAULT_SENDER'] = 'gokavivek@gmail.com'
mail = Mail(app)

def test_email():
    with app.app_context():
        try:
            msg = Message('Test Email', recipients=['gokavivek@gmail.com'], body='This is a test of the email credentials.')
            mail.send(msg)
            print("Email sent successfully!")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

if __name__ == "__main__":
    test_email()
