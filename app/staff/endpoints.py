from flask import Blueprint, request

from app.staff.model import Staff
from app.staff.schema import StaffSchema


staff = Blueprint('staff', __name__, url_prefix='/staff')

@staff.post('/register')
def staff_register():
    name = request.json.get('name')
    title = request.json.get('title')
    phone = request.json.get('phone')
    email = request.json.get('email')
    avaibility = request.json.get('avaibility')
    password = request.json.get('password')

    data = Staff.get_staff_by_email_or_phone(phone=phone, email=email)
    if not data:
        Staff.create(name, title, phone, email, avaibility, password)
        return 'Account created successfully', 200
    return 'Account creation failed, \'{}\' staff profile already exists'.format(data.name), 400

@staff.post('/login')
def staff_login():
    phone = request.json.get('phone')
    email = request.json.get('email')
    password = request.json.get('password')

    user = Staff.get_staff_by_email_or_phone(phone=phone, email=email)
    if user and user.is_valid_password(password):
        return 'Login succcessful', 200
    return 'Invalid Email or Password', 400

@staff.get('/all')
def get_all_staff():
    request_data = Staff.get_all_staff()
    if request_data:
        data = StaffSchema(many=True).dump(request_data, many=True)
        return {'staffs': data}
    return 'No staff found', 404

@staff.get('/view/<int:staff_id>')
def get_a_staff(staff_id):
    request_data = Staff.get_staff_by_id(id=staff_id)
    if request_data:
        data = StaffSchema().dump(request_data)
        return {'staff': data}
    return 'Staff not found', 404

@staff.patch('/edit/<int:staff_id>')
def edit_staff(staff_id):
    name = request.json.get('name')
    title = request.json.get('title')
    phone = request.json.get('phone')
    email = request.json.get('email')

    request_data = Staff.get_staff_by_id(id=staff_id)
    if request_data:
        Staff.update_staff(request_data, name=name, title=title, phone=phone, email=email)
        return 'Staff updated successfully', 200
    return 'Staff not found', 404