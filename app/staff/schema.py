from app import db
from app import ma
from app.staff.model import Staff

class StaffSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Staff