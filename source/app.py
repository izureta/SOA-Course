from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from flask import session

app = Flask('Social network')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/mydatabase'
app.secret_key = "any_random_string"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(1050), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    surname = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(1050), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    surname = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return {'message': 'Registered successfully'}

@app.route('/update', methods=['PUT'])
def update_user():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        if 'name' in data:
            user.name = data['name']
        if 'surname' in data:
            user.surname = data['surname']
        if 'birth_date' in data:
            user.birth_date = data['birth_date']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        db.session.commit()
        return {'message': 'User dsata updated'}
    else:
        return {'message': 'User not found'}

from werkzeug.security import check_password_hash

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        session[user.username] = user.id
        return {'message': 'Logged in'}
    return {'message': 'Wrong username or password'}

