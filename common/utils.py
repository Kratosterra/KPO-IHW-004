import logging
import re
import secrets
import sqlite3

from passlib.hash import pbkdf2_sha256 as sha256


def create_database() -> None:
    """
    Функция создания базы данных. Создаёт таблицы, если их нет.
    :return:
    """
    # Создание подключения к базе данных
    logging.debug("Создание базы данных.")
    conn = sqlite3.connect(r'../database/database.db')
    try:
        cursor = conn.cursor()
        # Создание таблицы "user"
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(10) NOT NULL CHECK (role IN ('customer', 'chef', 'manager')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        # Создание таблицы "session"
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS session (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_token VARCHAR(255),
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user(id)
                )
            ''')
        # Сохранение изменений и закрытие соединения
        conn.commit()
    except Exception as error:
        logging.debug(f"Создание базы данных произошло с ошибкой: {error}.")
    finally:
        conn.close()


def generate_session_token() -> str:
    """
    Функция, которая генерирует токен сессии.
    :return: Токен сессии.
    """
    token = secrets.token_hex(16)
    return token


def generate_password_hash(password: str) -> str:
    """
    Функция, которая генерирует хэш для пароля.
    :return: Хэш пароля.
    """
    return sha256.hash(password)


def check_password_hash(password: str, password_hash: str) -> bool:
    """
    Функция, которая проверяет соответствие пароля и хэша.
    :return: Хэш пароля.
    """
    return sha256.verify(password, password_hash)


def is_valid_email(email: str):
    """
    Функция, которая проверяет правильность адреса электронной почты.
    :return: Действительно ли адрес электронной почты правильный.
    """
    pattern = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"
    if re.match(pattern, email) is not None:
        return True
    else:
        return False
