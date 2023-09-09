from flask import Blueprint, request

from app.visitor.model import Visitors
from app.visitor.schema import VisitorsSchema

visitor = Blueprint('visitor', __name__, url_prefix='/visitor')

@visitor.post('/register')
def register_visitor():
    name = request.json.get('name')
    phone = request.json.get('phone')
    email = request.json.get('email')
    contact_address = request.json.get('contact_address')

    data = Visitors.get_visitor_by_email_or_phone(phone=phone, email=email)
    visitor_data = VisitorsSchema().dump(data)

    if not data:
        Visitors.create(name, phone, email, contact_address)
        return {
            'message': '{}\'s account created successfully'.format(name),
            'visitor': visitor_data
        }, 200

    return {
        'message': '{} account already exists'.format(name),
        'visitor': visitor_data
        }, 200

@visitor.patch('/update')
def update_visitor():
    name = request.json.get('name')
    phone = request.json.get('phone')
    email = request.json.get('email')
    contact_address = request.json.get('contact_address')

    data = Visitors.get_visitor_by_email_or_phone(phone=phone, email=email)

    if data:
        Visitors.update(name, phone, email, contact_address)
        return {'message': '{}\'s account updated successfully'.format(name)}, 200
    
    return {'message': 'Visitor\'s account does not exist'}, 404