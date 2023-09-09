from flask import Flask, request, session, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

timestamp = datetime.now()

db = SQLAlchemy()
app = Flask(__name__)
ma = Marshmallow(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///exchange_wallet.db"
app.config['SECRET_KEY'] = 'swapped_funds'
db.init_app(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=timestamp)
    updated_at = db.Column(db.DateTime, nullable=True)


class USDWallet(db.Model):
    __tablename__ = 'usd_wallet'
    id = db.Column(db.Integer, primary_key=True)
    dollar_balance = db.Column(db.Float(precision=2), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=timestamp)


class NairaWallet(db.Model):
    __tablename__ = 'naira_wallet'
    id = db.Column(db.Integer, primary_key=True)
    naira_balance = db.Column(db.Float(precision=2), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=timestamp)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


class USDWalletSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = USDWallet


class NairaWalletSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NairaWallet


with app.app_context():
    db.create_all()

exchange_rate = float(450)


@app.route("/")
def home():
    return "Exchange running at " + str(timestamp)


@app.post("/register")
def register():
    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']
    password = request.json['password']

    check_phone = User.query.filter_by(phone=phone).first()
    check_email = User.query.filter_by(email=email).first()
    if check_phone or check_email:
        return {"message": "Phone number or email already exists"}, 400

    new_user = User(name=name, email=email, phone=phone, password=password)
    db.session.add(new_user)
    db.session.commit()
    return {"message": "User created successfully"}


@app.get("/users")
def get_users():
    users = User.query.all()
    users = UserSchema().dump(users, many=True)
    return {"users": users}


@app.post('/desposit/usd')
def deposit_usd():
    amount = request.json['amount']
    try:
        amount = float(amount)
        new_deposit = USDWallet(dollar_balance=amount)
        db.session.add(new_deposit)
        db.session.commit()
        return {"message": "Deposit successful"}, 200
    except ValueError:
        return {"message": "Please enter a valid amount"}, 400


@app.post('/desposit/ngn')
def deposit_ngn():
    amount = request.json['amount']
    try:
        amount = float(amount)
        new_deposit = NairaWallet(naira_balance=amount)
        db.session.add(new_deposit)
        db.session.commit()
        return {"message": "Deposit successful"}, 200
    except ValueError:
        return {"message": "Please enter a valid amount"}, 400


@app.get("/balance/usd/<id>")
def get_usd_balance(id):
    usd_balance = USDWallet.query.filter_by(id=id).first()
    if usd_balance:
        usd_balance = USDWalletSchema().dump(usd_balance)
        return {"usd_balance": usd_balance}, 200
    else:
        return {"message": "USD record does not exist"}, 400


@ app.get("/balance/ngn/<id>")
def get_ngn_balance(id):
    ngn_balance = NairaWallet.query.filter_by(id=id).first()
    if ngn_balance:
        ngn_balance = NairaWalletSchema().dump(ngn_balance)
        return {"ngn_balance": ngn_balance}, 200
    else:
        return {"message": "NGN record does not exist"}, 400


@app.get('/history/usd')
def get_usd_history():
    usd_history = USDWallet.query.all()
    usd_history = USDWalletSchema().dump(usd_history, many=True)
    return {"usd_history": usd_history}


@app.get('/history/ngn')
def get_ngn_history():
    ngn_history = NairaWallet.query.all()
    ngn_history = NairaWalletSchema().dump(ngn_history, many=True)
    return {"ngn_history": ngn_history}


@app.patch("/swap")
def swap():
    naira_wallet_id = request.json['naira_wallet_id']
    usd_wallet_id = request.json['usd_wallet_id']
    to_currency = request.json['to_currency']
    amount = request.json['amount']
    try:
        amount = float(amount)
        naira_wallet = NairaWallet.query.filter_by(id=naira_wallet_id).first()
        usd_wallet = USDWallet.query.filter_by(id=usd_wallet_id).first()

        if not naira_wallet:
            return {"message": "NGN wallet could not be found"}, 400

        if not usd_wallet:
            return {"message": "USD wallet could not be found"}, 400

        if to_currency == "USD":
            # check if naira wallet has enough funds
            if naira_wallet.naira_balance < amount:
                return {"message": "Insufficient NGN funds"}, 400

            # deduct exact naira amount and topup to usd wallet
            naira_wallet.naira_balance -= amount
            usd_wallet.dollar_balance += (amount / exchange_rate)
            db.session.commit()
            return {"message": "Swap of NGN{} to USD is successful".format(amount)}

        elif to_currency == "NGN":
            # check if usd wallet has enough funds
            if usd_wallet.dollar_balance < amount:
                return {"message": "Insufficient USD funds"}, 400

            # deduct exact dollar amount and topup to naira wallet
            usd_wallet.dollar_balance -= amount
            naira_wallet.naira_balance += (amount * exchange_rate)
            db.session.commit()
            return {"message": "Swap of USD{} to NGN is successful".format(amount)}

        else:
            return {"message": "Invalid currency"}, 400

    except ValueError:
        return {"message": "Please enter a valid amount"}, 400
