from flask import Flask, request, session, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

timestamp = datetime.now()

db = SQLAlchemy()
app = Flask(__name__)
ma = Marshmallow(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///donation.db"
app.config['SECRET_KEY'] = 'help_people_in_need'

db.init_app(app)


class Hospital(db.Model):
    __tablename__ = 'hospitals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False, unique=True)
    address = db.Column(db.String, nullable=False)
    bank_name = db.Column(db.String, nullable=False)
    account_number = db.Column(db.String, nullable=False)
    account_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)


class Donor(db.Model):
    __tablename__ = 'donors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String, nullable=False, unique=True)
    address = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)


class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String, nullable=False, unique=True)
    address = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)


class PatientRecord(db.Model):
    __tablename__ = 'patient_records'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String, db.ForeignKey(
        'patients.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey(
        'hospitals.id'), nullable=False)
    hospital = db.relationship("Hospital")
    sickness = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)


class Donate(db.Model):
    __tablename__ = 'funds_donated'
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey(
        'donors.id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey(
        'patient_records.id'), nullable=False)
    amount_donating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)


class HospitalSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Hospital


class DonorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Donor


class PatientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Patient


class PatientRecordSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PatientRecord
        include_relationships = True
        include_fk = True
    hospital = ma.Nested(HospitalSchema)


class DonateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Donate


with app.app_context():
    db.create_all()


@app.route("/")
def hello_world():
    return "Donation running at " + str(timestamp)

# Create New Endpoints


@app.post("/create/hospital")
def create_hospital():
    hospital = Hospital(
        name=request.json['name'],
        phone=request.json['phone'],
        address=request.json['address'],
        bank_name=request.json['bank_name'],
        account_number=request.json['account_number'],
        account_name=request.json['account_name'],
        created_at=timestamp
    )
    user_phone = Hospital.query.filter_by(phone=hospital.phone).first()
    if user_phone:
        return {"message": "Hospital already exist"}, 400

    db.session.add(hospital)
    db.session.commit()
    return {"message": "Hospital created successfully"}, 200


@app.post("/create/donor")
def create_donor():
    donor = Donor(
        name=request.json['name'],
        email=request.json['email'],
        phone=request.json['phone'],
        address=request.json['address'],
        created_at=timestamp
    )
    user_phone = Donor.query.filter_by(phone=donor.phone).first()
    user_email = Donor.query.filter_by(email=donor.email).first()

    if user_phone or user_email:
        return {"message": "Donor already exists"}, 400

    db.session.add(donor)
    db.session.commit()
    return {"message": "Donor created successfully"}, 200


@app.post("/create/patient")
def create_patient():
    patient = Patient(
        patient_id=request.json['patient_id'],
        name=request.json['name'],
        email=request.json['email'],
        phone=request.json['phone'],
        address=request.json['address'],
        created_at=timestamp
    )
    user_phone = Patient.query.filter_by(phone=patient.phone).first()
    user_email = Patient.query.filter_by(email=patient.email).first()
    user_id = Patient.query.filter_by(patient_id=patient.patient_id).first()

    if user_phone or user_email or user_id:
        return {"message": "Patient already exists"}, 400

    db.session.add(patient)
    db.session.commit()
    return {"message": "Patient created successfully"}, 200


@app.post("/create/record")
def create_record():
    record = PatientRecord(
        patient_id=request.json['patient_id'],
        hospital_id=request.json['hospital_id'],
        sickness=request.json['sickness'],
        amount=request.json['amount'],
        created_at=timestamp
    )

    db.session.add(record)
    db.session.commit()
    return {"message": "Record created successfully"}, 200


@app.post("/create/donate")
def create_donate():
    donate = Donate(
        donor_id=request.json['donor_id'],
        record_id=request.json['record_id'],
        amount_donating=request.json['amount_donating'],
        created_at=timestamp
    )

    db.session.add(donate)
    db.session.commit()
    return {"message": "Donation created successfully"}, 200


# GET Endpoints
@app.get("/list/hospital")
def list_hospital():
    hospitals = Hospital.query.all()
    hospitals = HospitalSchema().dump(hospitals, many=True)
    return {"hospitals": hospitals}


@app.get("/list/donor")
def list_donor():
    donors = Donor.query.all()
    donors = DonorSchema().dump(donors, many=True)
    return {"donors": donors}


@app.get("/list/patient")
def list_patient():
    patients = Patient.query.all()
    patients = PatientSchema().dump(patients, many=True)
    return {"patients": patients}


@app.get("/list/records")
def list_records():
    records = PatientRecord.query.all()
    records = PatientRecordSchema().dump(records, many=True)
    return {"records": records}


@app.get("/list/transactions")
def list_transactions():
    transactions = Donate.query.all()
    transactions = DonateSchema().dump(transactions, many=True)
    return {"transactions": transactions}


@app.get("/view/donate/<record_id>")
def view_donate(record_id):
    donations = Donate.query.filter_by(record_id=record_id).all()
    donations = DonateSchema().dump(donations, many=True)
    return {"donations": donations}


# DELETE Endpoints
@app.delete("/delete/records/<id>")
def delete_record(id):
    record = PatientRecord.query.get(id)
    if not record:
        return {"message": "Record not found"}, 404
    db.session.delete(record)
    db.session.commit()
    return {"message": "Record deleted successfully"}, 200


if __name__ == "__main__":
    app.run()
