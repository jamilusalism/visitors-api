from flask import Blueprint, request

from app.admin.model import Admin
from app.admin.schema import AdminSchema

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.post('/register')
def admin_register():
    fullname = request.json.get('fullname')
    email = request.json.get('email')
    phone = request.json.get('phone')
    password = request.json.get('password')

    data = Admin.get_admin_by_email_or_phone(email=email, phone=phone)

    if not data:
        Admin.create(fullname, email, phone, password)
        return 'Account created successfully', 200
    return 'Account creation failed, \'{}\' admin profile already exists'.format(data.fullname), 400

@admin.post('/login')
def admin_login():
    email = request.json.get('email')
    phone = request.json.get('phone')
    password = request.json.get('password')

    user = Admin.get_admin_by_email_or_phone(email=email, phone=phone)
    if user and user.is_valid_password(password):
        return 'Login succcessful', 200
    return 'Invalid Email or Password', 400

@admin.get('/all')
def get_all_admin():
    request_data = Admin.get_all_admin()
    if request_data:
        data = AdminSchema(many=True).dump(request_data, many=True)
        return {'admins': data}, 200
    return {'No admin found'}, 404

@admin.get('/view/<int:admin_id>')
def get_an_admin(admin_id):
    request_data = Admin.get_admin_by_id(id=admin_id)
    if request_data:
        data = AdminSchema().dump(request_data)
        return {'admin': data}, 200
    return {'No admin found'}, 404

@admin.patch('/edit/<int:admin_id>')
def edit_an_admin(admin_id):
    fullname = request.json.get('fullname')
    email = request.json.get('email')
    phone = request.json.get('phone')

    request_data = Admin.get_admin_by_id(id=admin_id)
    if request_data:
        Admin.update_admin(request_data, fullname=fullname, email=email, phone=phone)
        return 'Admin profile updated successfully', 200
    return 'No admin found', 404