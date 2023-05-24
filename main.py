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

utils.create_database()

