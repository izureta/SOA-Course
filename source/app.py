from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

app = Flask('Social network')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://iliakruchinin@localhost/mydatabase'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    surname = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return {'message': 'Registered successfully'}

@app.route('/update', methods=['PUT'])
def update_user():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        user.name = data['name']
        user.surname = data['surname']
        user.birth_date = data['birth_date']
        user.email = data['email']
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
    if user and check_password_hash(user.password, data['password']):
        return {'message': 'Logged in'}
    return {'message': 'Wrong username or password'}

