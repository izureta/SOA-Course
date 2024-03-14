from flask import request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from . import create_app

from .models import User, db

app = create_app()

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

