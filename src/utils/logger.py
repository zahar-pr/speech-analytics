import functools
import logging
import os

class Logger:

    def __init__(self, log_path):
        self.log_path = log_path

    def setup_logger(self, current_log_file):
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

    def __call__(self, *args, **kwargs):
        self._logger = self.setup_logger(self.log_path)
        return self._logger

def use_logging(log_dir = 'logs', log_file = 'logs.log'):
    '''
    DECORATOR
    :param instance: class, which using logs
    :param log_dir: logging directory
    :param log_file: file of log
    :return:
    '''
    def wrapper(class_):
        class DecoratedClass(class_):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                self._logger = self._logger(log_dir + '/' + log_file + '.log')
                self._self._logger = self._logger()
        return DecoratedClass
    return wrapper