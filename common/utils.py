import sqlite3

import logging


def create_database() -> None:
    """
    Функция создания базы данных. Создаёт таблицы, если их нет.
    :return:
    """
    # Создание подключения к базе данных
    logging.debug("Создание базы данных.")
    conn = sqlite3.connect(r'database/database.db')
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
