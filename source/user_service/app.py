import sys
import os
import psycopg2
import grpc
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import posts_pb2
import posts_pb2_grpc


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
    username = request.headers.get('Login')
    password = request.headers.get('Password')

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
    username = request.headers.get('Login')
    password = request.headers.get('Password')
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


def authorize(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, password FROM users WHERE username = %s', (username,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user and check_password_hash(user[1], password):
        return True
    else:
        return False



@app.route('/login', methods=['POST'])
def login_user():
    username = request.headers.get('Login')
    password = request.headers.get('Password')

    if authorize(username, password):
        return jsonify({'message': 'Login successful'}), 200
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


post_channel = grpc.insecure_channel('post_service:50051')
post_stub = posts_pb2_grpc.PostServiceStub(post_channel)

@app.route('/create_post', methods=['POST'])
def create_post():
    username = request.headers.get('Login')
    password = request.headers.get('Password')
    
    if not authorize(username, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    user_id = int(request.json['user_id'])
    title = request.json['title']
    content = request.json['content']
    response = post_stub.CreatePost(posts_pb2.CreatePostRequest(user_id=user_id, title=title, content=content))
    return jsonify({'id': response.post.id, 'title': response.post.title, 'content': response.post.content})


@app.route('/update_post', methods=['POST'])
def update_post():
    username = request.headers.get('Login')
    password = request.headers.get('Password')
    
    if not authorize(username, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    post_id = int(request.json['post_id'])
    user_id = int(request.json['user_id'])
    title = request.json['title']
    content = request.json['content']
    response = post_stub.UpdatePost(posts_pb2.UpdatePostRequest(id=post_id, user_id=user_id, title=title, content=content))
    return jsonify({'id': response.post.id, 'title': response.post.title, 'content': response.post.content})


@app.route('/delete_post', methods=['DELETE'])
def delete_post():
    username = request.headers.get('Login')
    password = request.headers.get('Password')
    
    if not authorize(username, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    post_id = int(request.json['post_id'])
    user_id = int(request.json['user_id'])
    response = post_stub.DeletePost(posts_pb2.DeletePostRequest(id=post_id, user_id=user_id))
    return jsonify({'success': response.success})


@app.route('/get_post', methods=['GET'])
def get_post():
    username = request.headers.get('Login')
    password = request.headers.get('Password')
    
    if not authorize(username, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    post_id = int(request.json['post_id'])
    response = post_stub.GetPost(posts_pb2.GetPostRequest(id=post_id))
    return jsonify({'id': response.post.id, 'title': response.post.title, 'content': response.post.content})


@app.route('/list_posts', methods=['GET'])
def list_posts():
    username = request.headers.get('Login')
    password = request.headers.get('Password')
    
    if not authorize(username, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    user_id = int(request.json['user_id'])
    response = post_stub.ListPosts(posts_pb2.ListPostsRequest(user_id=user_id))

    page_num = 1
    result = {}
    for post in response.posts:
        result['post_' + str(page_num)] = {'id': post.id, 'title': post.title, 'content': post.content}
        page_num += 1
    return jsonify(result)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
