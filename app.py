from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
db = SQLAlchemy(app)
mail = Mail(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], password_hash=hashed_password)
    
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()
    
    verification_link = f"http://your-domain.com/verify/{new_user.id}"
    send_verification_email(new_user.email, verification_link)
    
    return jsonify({'message': 'User registered successfully! Please check your email to verify your account.'})

def send_verification_email(to_email, link):
    with app.app_context():
        msg = Message('Email Verification', sender='your-email@gmail.com', recipients=[to_email])
        msg.body = f'Please click the following link to verify your account: {link}'
        mail.send(msg)

@app.route('/verify/<int:user_id>', methods=['GET'])
def verify_email(user_id):
    with app.app_context():
        user = User.query.get(user_id)
        if user:
            user.is_verified = True
            db.session.commit()
            return jsonify({'message': 'Email verified successfully!'})
        return jsonify({'message': 'User not found!'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
