from sqlalchemy import or_
from app import db
from datetime import datetime
from werkzeug.security import check_password_hash as check_passwd, generate_password_hash as gen_passwd
timestamp = datetime.now()

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    phone = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=timestamp)
    updated_at = db.Column(db.DateTime, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        self.updated_at = timestamp
        db.session.commit()

    def update_admin(self, fullname=None, email=None, phone=None):
        self.fullname = fullname or self.name
        self.email = email or self.email
        self.phone = phone or self.phone
        self.updated_at = timestamp
        db.session.commit()

    def set_password(self, password):
        self.password = gen_passwd(password)
        return True
    
    def is_valid_password(self, password):
        return check_passwd(self.password, password)
    
    @classmethod
    def get_all_admin(cls):
        return cls.query.all()
    
    @classmethod
    def get_admin_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def get_admin_by_phone(cls, phone):
        return cls.query.filter_by(phone=phone).first()
    
    @classmethod
    def get_admin_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
        
    @classmethod
    def get_admin_by_email_or_phone(cls, email=None, phone=None):
        return cls.query.filter(or_(cls.email==email, cls.phone==phone)).first()
    
    @classmethod
    def create(cls, fullname, email, phone, password):
        user = cls(fullname=fullname, email=email, phone=phone, password=password)
        user.save()