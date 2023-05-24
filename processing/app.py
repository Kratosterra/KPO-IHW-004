import sqlite3

from flask import Flask
from flask import jsonify, request

from common import utils

app = Flask(__name__)
db = sqlite3.connect('../database/orders.db')
utils.create_database_processing()


# Маршрут для создания заказов
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    # Проверка правильности предоставленных данных
    if 'user_id' not in data or 'dishes' not in data or 'special_requests' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    # Получение данных из запроса
    user_id = data['user_id']
    dishes = data['dishes']
    special_requests = data['special_requests']

    # Дальнейшая обработка заказа...

    # Возвращаем успешный результат
    return jsonify({'message': 'Order created successfully'}), 201


# Маршрут для обработки заказов
@app.route('/orders/process', methods=['POST'])
def process_orders():
    # Извлечение заказов со статусом "в ожидании" из базы данных
    # Обработка заказов с некоторой задержкой
    # Изменение статуса заказов на "выполнен"

    # Возвращаем успешный результат
    return jsonify({'message': 'Orders processed successfully'}), 200


# Маршрут для получения информации о заказе по идентификатору
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    # Получение информации о заказе из базы данных по идентификатору

    # Проверка, что заказ существует

    # Возвращаем информацию о заказе
    return jsonify({'order_id': order_id, 'status': 'completed'}), 200


@app.route('/dishes', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_dishes():
    # Проверка роли пользователя (только менеджеры имеют доступ)

    if request.method == 'GET':
        # Получение информации о блюде

        # Возвращаем информацию о блюдах
        return jsonify({'message': 'Dishes retrieved successfully'}), 200

    elif request.method == 'POST':
        # Создание нового блюда

        # Возвращаем успешный результат
        return jsonify({'message': 'Dish created successfully'}), 201

    elif request.method == 'PUT':
        # Обновление информации о блюде

        # Возвращаем успешный результат
        return jsonify({'message': 'Dish updated successfully'}), 200

    elif request.method == 'DELETE':
        # Удаление блюда

        # Возвращаем успешный результат
        return jsonify({'message': 'Dish deleted successfully'}), 200

@app.route('/dishes', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_dishes():
    # Проверка роли пользователя (только менеджеры имеют доступ)

    if request.method == 'GET':
        # Получение информации о блюде

        # Возвращаем информацию о блюдах
        return jsonify({'message': 'Dishes retrieved successfully'}), 200

    elif request.method == 'POST':
        # Создание нового блюда

        # Возвращаем успешный результат
        return jsonify({'message': 'Dish created successfully'}), 201

    elif request.method == 'PUT':
        # Обновление информации о блюде

        # Возвращаем успешный результат
        return jsonify({'message': 'Dish updated successfully'}), 200

    elif request.method == 'DELETE':
        # Удаление блюда

        # Возвращаем успешный результат
        return jsonify({'message': 'Dish deleted successfully'}), 200


@app.route('/menu', methods=['GET'])
def get_menu():
    # Меню

    return jsonify({'message': 'Menu'}), 200


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port="3000")
