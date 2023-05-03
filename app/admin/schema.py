from app import db
from app.admin.model import Admin
from app import ma

class AdminSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Admin