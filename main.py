import logging

import coloredlogs

from common import utils

# Оформляем логирование.
coloredlogs.install(level='DEBUG')
logger = logging.getLogger(__name__)
coloredlogs.install(
    level='DEBUG', logger=logger,
    fmt='%(asctime)s.%(msecs)03d %(filename)s:%(lineno)d %(levelname)s %(message)s'
)

# Создаём базы данных!
utils.create_database()
utils.create_database_processing()

# Получаем микросервисы
from authorization.app import app_auth
from processing.app import app


# Чтобы запустить какой-то из микросервисов, закоментируйте другой.
if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port="3000")  # Запуск основного микросервиса
    # app_auth.run(debug=True, host="127.0.0.1", port="5000")  # Запуск микросервиса аутентификации.

