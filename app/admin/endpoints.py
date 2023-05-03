from flask import Blueprint, request

from app.admin.model import Admin

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.post('/login')
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = Admin.get_by_email(email)
    if user and user.is_valid(password):
        return 'Login succcessful', 200
    return 'Invalid Email or Password', 400

@admin.post('/register')
def register():
    fullname = request.json.get('fullname')
    email = request.json.get('email')
    phone = request.json.get('phone')
    password = request.json.get('password')

    if fullname and email and phone and password:
        Admin.create(fullname, email, phone, password)
        return 'Account created successfully', 200
    return 'Account creation failed, please try again', 400