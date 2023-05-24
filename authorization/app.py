import logging
import sqlite3
from datetime import datetime, timedelta

from flask import Flask
from flask import jsonify, request

from common import utils

# Создаём экземпляр приложения.
app = Flask(__name__)
conn = sqlite3.connect('../database/database.db', check_same_thread=False)
cursor = conn.cursor()


@app.route('/', methods=['GET', 'POST'])
def hello():
    """
    Скажи привет!
    :return: Сообщение с приветствием!
    """
    return jsonify({'message': 'Hello!'}), 200


@app.route('/register', methods=['POST'])
def register():
    """
    Регистрация нового пользователя
    :return: Ответ на данные, предоставленные пользователем.
    """
    data = request.get_json()
    logging.debug(f"{register.__name__}: Получена информация: {data}")
    try:
        username = data['username']
        email = data['email']
        password = data['password']
        role = data['role']
    except Exception as e:
        logging.debug(f"{register.__name__}: Недостаточно информации: {data}")
        return jsonify(message='Not enough information in request!'), 400
    if not utils.is_valid_email(email):
        return jsonify(message='Not valid email address!'), 400
    password_hash = utils.generate_password_hash(password)
    try:
        cursor.execute('INSERT INTO user (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                       (username, email, password_hash, role))
        conn.commit()
        logging.debug(f"{register.__name__}: Успешная регистрация: {data}")
        return jsonify(message='Successful registration'), 200
    except sqlite3.IntegrityError:
        return jsonify(message='Name or email already exists!'), 400


@app.route('/login', methods=['POST'])
def login():
    """
    Авторизация пользователя.
    :return: Сообщение о состоянии авторизации.
    """
    logging.debug(f"{login.__name__}: Авторизация!")
    data = request.get_json()
    try:
        email = data['email']
        password = data['password']
    except Exception as e:
        logging.debug(f"{login.__name__}: Недостаточно информации: {data}")
        return jsonify(message='Not enough information in request!'), 400

    cursor.execute('SELECT * FROM user WHERE email = ?', (email,))
    user = cursor.fetchone()
    if user and utils.check_password_hash(password, user[3]):
        session_token = utils.generate_session_token()
        expires_at = datetime.now() + timedelta(days=7)  # Продление сессии на 7 дней
        cursor.execute('INSERT INTO session (user_id, session_token, expires_at) VALUES (?, ?, ?)',
                       (user[0], session_token, expires_at))
        conn.commit()
        logging.debug(f"{login.__name__}: Успешная авторизация: {data}")
        return jsonify(message='Login successful', session_token=session_token), 200
    else:
        return jsonify(message='Invalid email or password'), 401


@app.route('/user', methods=['GET'])
def get_user_info():
    """
    Получает инормации о сессии на основе заголовка, содержащего токен сессии.
    :return Состояние или информацию о пользователе:
    """
    logging.debug(f"{get_user_info.__name__}: Получение информации о пользователе!")
    token = request.headers.get('Authorization')
    user_info = get_user_info_from_token(token)
    if user_info is None:
        return jsonify({'error': 'Invalid token'}), 401

    return jsonify(user_info), 200


def get_user_info_from_token(token: str) -> dict or None:
    """
    Возвращает информацию о пользователе по токену.
    :param token: Токен пользователя.
    :return: Информацию о пользователе.
    """
    cursor.execute('''
        SELECT u.id, u.username, u.email, u.role
        FROM user u
        INNER JOIN session s ON u.id = s.user_id
        WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
    ''', (token,))
    result = cursor.fetchone()
    if result is None:
        return None
    user_info = {
        'id': result[0],
        'username': result[1],
        'email': result[2],
        'role': result[3]
    }
    return user_info


def extend_session(session_token) -> None:
    """
    Продление сессии
    :param session_token: Токен сессии
    """
    expires_at = datetime.now() + timedelta(days=7)  # Продление сессии на 7 дней
    cursor.execute('UPDATE session SET expires_at = ? WHERE session_token = ?', (expires_at, session_token))
    conn.commit()


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
