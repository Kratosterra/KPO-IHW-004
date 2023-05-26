import logging
import sqlite3
import time

from flask import Flask
from flask import jsonify, request

from common import utils

app = Flask(__name__)
db = sqlite3.connect('database/orders.db', check_same_thread=False)
cursor = db.cursor()
utils.create_database_processing()


@app.route('/orders', methods=['POST'])
def create_order():
    """
    Создание заказа пользователем.
    :return: Состояние или информацию о создании заказов.
    """
    data = request.get_json()
    logging.debug(f"{create_order.__name__}: Получена информация: {data}")
    if 'user_id' not in data or 'dishes' not in data or 'special_requests' not in data:
        logging.debug(f"{create_order.__name__}: Недостаточно информации!")
        return jsonify({'error': 'Invalid data'}), 400
    user_id = data['user_id']
    db_users = sqlite3.connect('database/database.db', check_same_thread=False)
    cursor_user = db_users.cursor()
    cursor_user.execute('SELECT * FROM user WHERE id = ?', (user_id,))
    user = cursor_user.fetchone()
    db_users.close()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    dishes = data['dishes']
    special_requests = data['special_requests']
    for dish in dishes:
        dish_id = dish['dish_id']
        quantity = dish['quantity']
        cursor.execute("SELECT COUNT(*) FROM dish WHERE id = ?", (dish_id,))
        count = cursor.fetchone()[0]
        if count == 0:
            return jsonify({'error': 'Dish not found'}), 404
        cursor.execute("SELECT quantity FROM dish WHERE id = ?", (dish_id,))
        available_quantity = cursor.fetchone()[0]
        if quantity > available_quantity:
            logging.debug(f"{create_order.__name__}: Заказу недостаточно блюд на складе!")
            return jsonify({'error': 'Insufficient quantity for dish with ID {}'.format(dish_id)}), 400
    cursor.execute("INSERT INTO order_table (user_id, special_requests, status) VALUES (?, ?, ?)",
                   (user_id, special_requests, 'pending'))
    order_id = cursor.lastrowid
    for dish in dishes:
        dish_id = dish['dish_id']
        quantity = dish['quantity']
        price = dish['price']
        cursor.execute("INSERT INTO order_dish (order_id, dish_id, quantity, price) VALUES (?, ?, ?, ?)",
                       (order_id, dish_id, quantity, price))
        cursor.execute("UPDATE dish SET quantity = quantity - ? WHERE id = ?", (quantity, dish_id))
        db.commit()
        cursor.execute("SELECT quantity FROM dish WHERE id = ?", (dish_id,))
        if cursor.fetchone()[0] <= 0:
            cursor.execute("UPDATE dish SET is_available = 'False' WHERE id = ?", (dish_id,))
    db.commit()
    logging.debug(f"{create_order.__name__}: Успешное создание заказа!")
    return jsonify({'message': 'Order created successfully'}), 201


@app.route('/orders/process', methods=['POST'])
def process_orders():
    """
    Выполнение заказов с некторой задержкой.
    :return: Состояние или информацию о выполнении заказов.
    """
    cursor.execute("SELECT * FROM order_table WHERE status = ?", ('pending',))
    orders = cursor.fetchall()
    logging.debug(f"{process_orders.__name__}: Начинаю обработку заказов!")
    for order in orders:
        time.sleep(2)
        order_id = order[0]
        logging.debug(f"{process_orders.__name__}: Выполнил заказ c id {order_id}!")
        cursor.execute("UPDATE order_table SET status = ? WHERE id = ?", ('completed', order_id))
    db.commit()
    logging.debug(f"{process_orders.__name__}: Выполнил заказы!")
    return jsonify({'message': 'Orders processed successfully'}), 200


@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Возвращает информацию о заказе по его идентификационному номеру.
    :param order_id: Идентификационный номер.
    :return: Информацию о заказе.
    """
    cursor.execute("SELECT * FROM order_table WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify({
        'order_id': order[0],
        'user_id': order[1],
        'status': order[2],
        'special_requests': order[3]})


@app.route('/dishes', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_dishes():
    """
    Управление блюдами. Получать информацию о блюде могут все, но остальные действия выполняются только менеджером.
    :return: Информацию о блюде или статус выполнения запроса.
    """
    data = request.get_json()
    logging.debug(f"{manage_dishes.__name__}: Получена информация: {data}")
    if 'user_id' not in data:
        logging.debug(f"{manage_dishes.__name__}: Нет информации о пользователе!")
        return jsonify({'error': 'Invalid data'}), 400
    user_id = data['user_id']
    db_users = sqlite3.connect('database/database.db', check_same_thread=False)
    cursor_user = db_users.cursor()
    cursor_user.execute('SELECT * FROM user WHERE id = ?', (user_id,))
    user = cursor_user.fetchone()
    user_role = user[4]
    db_users.close()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    if request.method == 'GET':
        dish_id = data['id']
        cursor.execute("SELECT * FROM dish WHERE id = ?", (dish_id,))
        dish = cursor.fetchone()
        if dish is None or not dish[5] or dish[4] <= 0:
            return jsonify({'error': 'Dish not found or not available'}), 404
        return jsonify({'dish': dish}), 200
    elif request.method == 'POST':
        if user_role != 'manager':
            return jsonify({'error': 'Access denied, you are not manager'}), 403
        if 'name' not in data or 'description' not in data or 'price' not in data or 'quantity' not in data or 'is_available' not in data:
            logging.debug(f"{manage_dishes.__name__}: Недостаточно информации!")
            return jsonify({'error': 'Invalid data for dish creation'}), 400
        dish_data = request.json
        cursor.execute("INSERT INTO dish (name, description, price, quantity, is_available) VALUES (?, ?, ?, ?, ?)",
                       (dish_data['name'], dish_data['description'], dish_data['price'], dish_data['quantity'],
                        dish_data['is_available']))
        db.commit()
        return jsonify({'message': 'Dish created successfully'}), 201

    elif request.method == 'PUT':
        if user_role != 'manager':
            return jsonify({'error': 'Access denied, you are not manager'}), 403
        if 'name' not in data or 'description' not in data or 'price' not in data or 'quantity' not in data or 'is_available' not in data:
            logging.debug(f"{manage_dishes.__name__}: Недостаточно информации!")
            return jsonify({'error': 'Invalid data for dish update'}), 400
        dish_id = request.json['id']
        name = request.json['name']
        description = request.json['description']
        price = request.json['price']
        quantity = request.json['quantity']
        is_available = request.json['is_available']
        query = "UPDATE dish SET name=?, description=?, price=?, quantity=?, is_available=? WHERE id=?"
        cursor.execute(query, (name, description, price, quantity, is_available, dish_id))
        db.commit()
        return jsonify({'message': 'Dish updated successfully'}), 200
    elif request.method == 'DELETE':
        if user_role != 'manager':
            return jsonify({'error': 'Access denied, you are not manager'}), 403
        dish_id = request.json['id']
        cursor.execute("SELECT * FROM dish WHERE id = ?", (dish_id,))
        dish = cursor.fetchone()
        if dish is None:
            return jsonify({'error': 'Dish not found!'}), 404
        query = "DELETE FROM dish WHERE id=?"
        cursor.execute(query, (dish_id,))
        db.commit()
        return jsonify({'message': 'Dish deleted successfully'}), 200


@app.route('/menu', methods=['GET'])
def get_menu():
    """
    Возвращает информацию о всех доступных блюдах.
    :return:
    """
    logging.debug(f"{get_menu.__name__}: Получаем информацию о меню!")
    query = "SELECT * FROM dish WHERE is_available = 'True'"
    cursor.execute(query)
    dishes = cursor.fetchall()
    menu = []
    for dish in dishes:
        dish_dict = {
            'id': dish[0],
            'name': dish[1],
            'description': dish[2],
            'price': float(dish[3]),
            'quantity': dish[4],
            'is_available': bool(dish[5]),
            'created_at': str(dish[6]),
            'updated_at': str(dish[7])
        }
        menu.append(dish_dict)

    return jsonify({'menu': menu}), 200
