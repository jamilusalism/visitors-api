from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from datetime import datetime
import random

import africastalking

timestamp = datetime.now()

db = SQLAlchemy()
app = Flask(__name__)
migrate = Migrate(app, db)
ma = Marshmallow(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quizGeniusTournament.db"
app.config['SECRET_KEY'] = 'have_fun_with_quizgenius'

# Initialize SDK
username = "TeamZainab"    # use 'sandbox' for development in the test environment
api_key = "ae79602b1cf872f7218e1388756b3bba8d4f146da5a6df5080cf62620e0b098c"      # use your sandbox app API key for development in the test environment
africastalking.initialize(username, api_key)

# Initialize a service e.g. SMS
sms = africastalking.SMS

db.init_app(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    phone = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=timestamp)
    updated_at = db.Column(db.DateTime, nullable=True)

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String, nullable=False)
    option_one = db.Column(db.String, nullable=False)
    option_two = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=timestamp)
    updated_at = db.Column(db.DateTime, nullable=True)

class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User")
    score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=timestamp)
    updated_at = db.Column(db.DateTime, nullable=True)

class Tournament(db.Model):
    __tablename__ = 'tournament'
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_profile = db.relationship("User")
    code = db.Column(db.String, nullable=False, unique=True)
    gift = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=timestamp)
    updated_at = db.Column(db.DateTime, nullable=True)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question

class ScoreSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Score
        include_relationships = True
        include_fk = True
    user = ma.Nested(UserSchema)

class TournamentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tournament
        include_relationships = True
        include_fk = True
    created_profile = ma.Nested(UserSchema)

with app.app_context():
    db.create_all()
    
def send_sms(name, number, score=0):
    if score == 0:
        message = f"Hi {name}, you're invited to QuizGenius Tournament. Your code is: {gen_code}"
    else:
        message = f"Hello {name}, the tournament has ended and your scored is {score} points".format(name, score)

    response = sms.send(message=message, recipients=[number])
    print("R: ", response)
    return {"message": "SMS sent successfully"}, 200

def tornament_code(length):
	min = pow(10, length-1)
	max = pow(10, length) - 1
	return random.randint(min, max)

gen_code = tornament_code(5)

@app.route('/')
def index():
    send_sms("Zainab", "+2348028752833")
    return "Welcome to QuizGenius Tournament v1.0"

@app.post('/register')
def register():
    new_user = User(
        name = request.json['name'],
        username = request.json['username'],
        phone = request.json['phone'],
        password = request.json['password'],
    )

    username_exist = User.query.filter_by(username=new_user.username).first()
    phone_exist = User.query.filter_by(phone=new_user.phone).first()
    if username_exist:
        return {"message": "Username already exist"}, 400
    
    if phone_exist:
        return {"message": "Phone number already exist"}, 400
    
    db.session.add(new_user)
    db.session.commit()
    return {"message": "User created successfully"}, 200

@app.get('/users')
def get_users():
    users = User.query.all()
    users_list = UserSchema().dump(users, many=True)
    return {"users": users_list}, 200

@app.post('/create/question')
def create_questions():
    # difficulty is limited to easy, and hard
    new_question = Question(
        question_text = request.json['question_text'],
        option_one = request.json['option_one'],
        option_two = request.json['option_two'],
        answer = request.json['answer'],
        difficulty = request.json['difficulty'].lower(),
    )
    db.session.add(new_question)
    db.session.commit()
    return {"message": "Question created successfully"}, 200

@app.get('/questions')
def get_questions():
    questions = Question.query.all()
    questions_list = QuestionSchema().dump(questions, many=True)
    return {"questions": questions_list}, 200

#@app.post('/create/score')
def create_score():
    new_score = Score(
        user_id = request.json['user_id'],
        score = request.json['score'],
    )
    verify_user = User.query.filter_by(id=new_score.user_id).first()
    if not verify_user:
        return {"message": "User does not exist"}, 400
    
    db.session.add(new_score)
    db.session.commit()
    return {"message": "Score created successfully"}, 200

@app.get('/leaderboard')
def leaderboard():
    scores = Score.query.all()
    scores_list = ScoreSchema().dump(scores, many=True)
    return {"leaderboard": scores_list}, 200

@app.post('/create/tournament')
def create_tournament():
    new_tournament = Tournament(
        created_by = request.json['created_by'],
        code = gen_code,
        gift = request.json['gift'],
    )
    verify_user = User.query.filter_by(id=new_tournament.created_by).first()
    if not verify_user:
        return {"message": "User does not exist"}, 400
    
    random_user = User.query.filter_by(id=random.randint(3, 4)).first()
    if random_user:
        send_sms(random_user.name, random_user.phone)
    else:
        return {"message": "Fail to assign a player"}, 400
    
    db.session.add(new_tournament)
    db.session.commit()
    return {"message": "Tournament created successfully, and invitation sent to {}".format(random_user.name)}, 200

@app.get('/tournaments')
def get_tournaments():
    tournaments = Tournament.query.all()
    tournaments_list = TournamentSchema().dump(tournaments, many=True)
    return {"tournaments": tournaments_list}, 200

@app.post('/play')
def play_tournament():
    tournament = Tournament.query.filter_by(code=request.json['code']).first()
    if not tournament:
        return {"message": "Invalid code"}, 400
    
    if tournament.status == False:
        return {"message": "Tournament has ended"}, 400
    
    print("Welcome to QuizGenius Tournament")
    question = Question.query.all()
    question_list = QuestionSchema().dump(question, many=True)
    score = 0
    for i in range(2):
        print(question_list[i]['question_text'])
        print(question_list[i]['option_one'])
        print(question_list[i]['option_two'])
        print('Reply with \'true or false\'\n')
        answer = input("Enter your answer: ")
        if answer == question_list[i]['answer']:
            score += 10
        else:
            score -= 5

    # Send score of the invited user to the tournament host
    send_sms(tournament.created_profile.name, tournament.created_profile.phone, score)
    new_score = Score(
        user_id = request.json['user_id'],
        score = score,
    )
    db.session.add(new_score)
    db.session.commit()
    return {"message": "Tonament ended, and thank you for participating"}, 200

def play():
    question = Question.query.all()
    question_list = QuestionSchema().dump(question, many=True)
    score = 0
    for i in range(10):
        print(question_list[i]['question_text'])
        print(question_list[i]['option_one'])
        print(question_list[i]['option_two'])
        answer = input("Enter your answer: ")
        if answer == question_list[i]['answer']:
            score += 1
    print("Your score is: ", score)

def player_choice():
    print("1. Play")
    print("2. View Leaderboard")
    print("3. Exit")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        print("Welcome to QuizGenius Tournament")
        print("You have 10 questions to answer, Goodluck!")
        play()
    elif choice == 2:
        print("Leaderboard")
        leaderboard()
    elif choice == 3:
        print("Bye")
        exit()
    else:
        print("Invalid choice entered")
        player_choice()

if __name__ == '__main__':
    app.run(debug=True)