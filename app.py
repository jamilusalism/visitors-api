from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import generate_password_hash as generate_hash, check_password_hash as check_hash
from flask_mail import Mail, Message
from flask_migrate import Migrate
import os, re, random
from datetime import datetime
from flask_marshmallow import Marshmallow

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
ma = Marshmallow(app)

mail_username = app.config.get('MAIL_USERNAME') 


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    otp = db.Column(db.String, nullable=True)

class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.DateTime, nullable=False)


class UsersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        #include_fk = True

with app.app_context():
    db.create_all()


def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_hash(user.password, password):
        return user


def identity(payload):
    user_id = payload['identity']
    return User.query.filter_by(id=user_id).first()


jwt = JWT(app, authenticate, identity)

@app.get('/')
def index():
    return 'Welcome to MyPal API v1.0.0', 200

@app.post('/register')
def register():
    full_name = request.json.get('full_name')
    #first_name = full_name.split()[0]
    phone = request.json.get('phone')
    email = request.json.get('email')
    password = request.json.get('password')

    if is_valid_email(email):
        # check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            return 'Email already exists', 400
        
        user = User.query.filter_by(phone=phone).first()
        if user:
            return 'Phone number already exists', 400
        
        # create a new user
        #user = User(full_name=full_name, first_name=first_name, phone=phone, email=email, password=generate_hash(password))
        user = User(full_name=full_name, phone=phone, email=email, password=generate_hash(password))
        db.session.add(user)
        db.session.commit()
    else:
        return f'{email} is not a valid email address', 400

    # send a welcome mail along with a verification link
    msg = Message('Hello from MyPal',
                    sender=mail_username,
                    recipients=[email])
    msg.body = f'Hello {full_name}, welcome to MyPal. We are glad to have you on board and we hope you will enjoy our services.' 
    msg.html = render_template('welcome_mail.html', first_name=full_name)
    mail.send(msg)
    return 'Account created successfully', 201

@app.post('/reset-otp')
def reset_password():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        # generate a random 6 digit OTP
        temp_otp = str(random.randint(100000, 999999))
        # save the OTP to the database
        user.otp = temp_otp
        db.session.commit()
        # send the OTP to the user's email
        msg = Message('OTP to reset your MyPal password',
                    sender=mail_username,
                    recipients=[email])
        msg.body = f'Hello {user.first_name}, you have requested for a password reset. Please use the OTP below to reset your password. \n\n{temp_otp}'
        msg.html = render_template('reset_password.html', first_name=user.first_name, temp_otp=temp_otp)
        mail.send(msg)
        return 'OTP has been sent to your email', 200
    return 'User not found', 404

@app.put('/update-password')
def update_password():
    email = request.json.get('email')
    otp = request.json.get('otp')
    new_password = request.json.get('new_password')
    confirm_password = request.json.get('confirm_password')

    if new_password != confirm_password:
        return 'Passwords do not match', 400
    
    user = User.query.filter_by(email=email).first()
    if user and user.otp == otp:
        user.password = generate_hash(new_password)
        user.otp = None
        db.session.commit()
        return 'Password updated successfully', 200
    return 'Invalid OTP, please try again', 400

@app.get('/profile/<int:user_id>')
@jwt_required()
def profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        user = {'id':user.id, 'full_name': user.full_name, 'first_name': user.first_name, 'phone': user.phone, 'email': user.email}
        return {'user': user}
    return 'User not found', 400

@app.put('/update-profile/<int:user_id>')
@jwt_required()
def update_profile(user_id):
    full_name = request.json.get('full_name')
    first_name = full_name.split()[0]
    phone = request.json.get('phone')
    email = request.json.get('email')

    user = User.query.filter_by(email=email).first()
    if user:
        user.full_name = full_name or user.full_name
        user.first_name = first_name or user.first_name
        user.phone = phone or user.phone
        user.email = email or user.email
        db.session.commit()
        return 'Profile updated successfully', 200
    return 'User not found', 400

# @app.get('/users')
# # @jwt_required()
# def users():
#     user = User.query.all()
#     users = [{'id':user.id, 'full_name': user.full_name, 'first_name': user.first_name, 'phone': user.phone, 'email': user.email} for user in user]
#     return {'users': users}, 200

@app.get('/users')
def get_users():
    users = UsersSchema(many=True).dump(User.query.all())
    return {'users': users}, 200


@app.post('/create-space')
@jwt_required()
def create_space():
    host_id = request.json.get('host_id')
    title = request.json.get('title')
    description = request.json.get('description')
    date = datetime.fromisoformat(request.json.get('date'))
    time = datetime.fromisoformat(request.json.get('time'))

    # create a new space
    space = Space(host_id=host_id, title=title, description=description, date=date, time=time)
    db.session.add(space)
    db.session.commit()
    return 'Space created successfully', 200

@app.get('/spaces')
# @jwt_required()
def get_spaces():
    spaces = Space.query.all()
    spaces = [{'id':space.id, 'host_id': space.host_id, 'title': space.title, 'description': space.description, 'date': space.date, 'time': space.time} for space in spaces]
    return {'spaces': spaces}

@app.get('/space/<int:id>')
@jwt_required()
def get_space(id):
    space = Space.query.filter_by(id=id).first()
    if space:
        space =  {'id':space.id, 'host_id': space.host_id, 'title': space.title, 'description': space.description, 'date': space.date, 'time': space.time}
        return {'space': space}
    return 'Space not found', 404

@app.get('/space/host/<int:host_id>')
@jwt_required()
def get_space_by_host(host_id):
    spaces = Space.query.filter_by(host_id=host_id).all()
    if spaces:
        spaces = [{'id':space.id, 'host_id': space.host_id, 'title': space.title, 'description': space.description, 'date': space.date, 'time': space.time} for space in spaces]
        return {'hostspaces': spaces}
    return 'Space not found', 404

def is_valid_email(email):
    #check if a given email address is valid
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    #email = email.trim()
    return re.match(email_regex, email) is not None

if __name__ == '__main__':
    app.run(debug=True)
