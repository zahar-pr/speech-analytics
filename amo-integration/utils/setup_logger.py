import logging
import os

log_dir = 'logs'
log_file = 'logs.log'

# Проверяем, существует ли директория
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Создаем файл для логов
log_path = os.path.join(log_dir, log_file)


def setup_logger(current_log_file):
    # Создание логгера
    logger_instance = logging.getLogger()
    logger_instance.setLevel(logging.DEBUG)

    # Создание обработчика для записи логов в файл
    file_handler = logging.FileHandler(current_log_file)

    # Форматирование для файлового обработчика
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Добавление обработчика к логгеру
    logger_instance.addHandler(file_handler)

    # Создание обработчика для вывода логов на консоль
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger_instance.addHandler(console_handler)

    return logger_instance


logger = setup_logger(log_path)
