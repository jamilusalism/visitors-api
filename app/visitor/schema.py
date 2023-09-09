from app import ma
from app.visitor.model import Visitors

class VisitorsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Visitors