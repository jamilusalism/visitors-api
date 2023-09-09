from sqlalchemy import or_
from app import db
from datetime import datetime
timestamp = datetime.now()

class Visitors(db.Model):
    __tablename__ = 'visitors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    contact_address = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=timestamp)
    updated_at = db.Column(db.DateTime)

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, name=None, phone=None, email=None, contact_address=None):
        self.name = name or self.name
        self.phone = phone or self.phone
        self.email = email or self.email
        self.contact_address = contact_address or self.contact_address
        db.session.commit()
    
    @classmethod
    def get_visitor_by_phone(cls, phone):
        return cls.query.filter_by(phone=phone).first()
    
    @classmethod
    def get_visitor_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_visitor_by_email_or_phone(cls, email=None, phone=None):
        return cls.query.filter(or_(cls.email==email, cls.phone==phone)).first()
    
    @classmethod
    def create(cls, name, phone, email, contact_address):
        user = cls(name=name, phone=phone, email=email, contact_address=contact_address)
        user.save()