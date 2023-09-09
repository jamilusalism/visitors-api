from sqlalchemy import or_
from app import db
from datetime import datetime
from werkzeug.security import check_password_hash as check_passwd, generate_password_hash as gen_passwd
timestamp = datetime.now()

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    avaibility = db.Column(db.Boolean, nullable=False, default=True)
    password = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=timestamp)
    updated_at = db.Column(db.DateTime)

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def update_staff(self, name=None, title=None, phone=None, email=None):
        self.name = name or self.name
        self.title = title or self.title
        self.phone = phone or self.phone
        self.email = email or self.email
        self.updated_at = timestamp
        db.session.commit()

    def update_avaibility(self, avaibility):
        self.avaibility = not avaibility
        db.session.commit()

    def set_password(self, password):
        self.password = gen_passwd(password)
        return True
    
    def is_valid_password(self, password):
        return check_passwd(self.password, password)
    
    @classmethod
    def get_staff_by_phone(cls, phone):
        return cls.query.filter_by(phone=phone).first()
    
    @classmethod
    def get_all_staff(cls):
        return cls.query.all()
    
    @classmethod
    def get_staff_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def get_staff_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_staff_by_email_or_phone(cls, email=None, phone=None):
        return cls.query.filter(or_(cls.email==email, cls.phone==phone)).first()
    
    @classmethod
    def create(cls, name, title, phone, email, avaibility, password):
        user = cls(name=name, title=title, phone=phone, email=email, avaibility=avaibility, password=gen_passwd(password))
        user.save()