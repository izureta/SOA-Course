import os
import psycopg2
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        birth_day DATE,
        email TEXT,
        phone_number TEXT
    )
    ''')
    conn.commit()
    cur.close()
    conn.close()



@app.route('/register', methods=['POST'])
def register_user():
    username = request.json['username']
    password = request.json['password']

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id', (username, hashed_password))
        user_id = cur.fetchone()[0]
        conn.commit()
        response = jsonify({'id': user_id, 'username': username})
        response.status_code = 201
        return response
    except psycopg2.IntegrityError:
        conn.rollback()
        response = jsonify({'error': 'Username already exists'})
        response.status_code = 409
        return response
    finally:
        cur.close()
        conn.close()


@app.route('/update', methods=['PUT'])
def update_user():
    username = request.json['username']
    password = request.json['password']
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    birth_day = request.json.get('birth_day')
    email = request.json.get('email')
    phone_number = request.json.get('phone_number')

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT password FROM users WHERE username = %s', (username,))
    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return jsonify({'error': 'Invalid username'}), 404

    if not check_password_hash(user[0], password):
        cur.close()
        conn.close()
        return jsonify({'error': 'Invalid password'}), 401

    try:
        cur.execute('''
            UPDATE users
            SET first_name = %s, last_name = %s, birth_day = %s, email = %s, phone_number = %s
            WHERE username = %s
        ''', (first_name, last_name, birth_day, email, phone_number, username))
        conn.commit()

        if cur.rowcount == 0:
            response = jsonify({'error': 'User not found'})
            response.status_code = 404
        else:
            response = jsonify({'message': 'User updated successfully'})
            response.status_code = 200
        return response
    except Exception as e:
        conn.rollback()
        response = jsonify({'error': str(e)})
        response.status_code = 500
        return response
    finally:
        cur.close()
        conn.close()


@app.route('/login', methods=['POST'])
def login_user():
    username = request.json['username']
    password = request.json['password']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, password FROM users WHERE username = %s', (username,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user and check_password_hash(user[1], password):
        return jsonify({'message': 'Login successful', 'user_id': user[0]}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/users', methods=['GET'])
def get_users():
    if request.json['secret_key'] != os.getenv('DEV_SECRET_KEY'):
        return jsonify({'error': 'Invalid secret key'}), 401
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, password, first_name, last_name, birth_day, email, phone_number FROM users')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(users)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
