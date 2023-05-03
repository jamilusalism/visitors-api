from app import db
from datetime import datetime
from werkzeug.security import check_password_hash as check_passwd, generate_password_hash as gen_passwd
timestamp = datetime.now()

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=timestamp)
    updated_at = db.Column(db.DateTime, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def set_password(self, password):
        self.password = gen_passwd(password)
        return True
    
    def is_valid(self, password):
        return check_passwd(self.password, password)
    
    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def create(cls, fullname, email, phone, password):
        user = cls(fullname=fullname, email=email, phone=phone)
        user.set_password(password)
        user.save()
        user.update()