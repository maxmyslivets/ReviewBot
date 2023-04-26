import logging
import traceback
from pathlib import Path

import coloredlogs
import inspect

from settings import *


class Logger:
    """
    Объект логгера для записи сообщений в журнал.

    :param name: Имя логгера.
    :type name: str
    :param level: Уровень логирования. По умолчанию `logging.DEBUG`.
    :type level: int
    :param fmt: Форматтер для сообщений. Если не задан, используется формат по умолчанию.
    :type fmt: str

    :return: Объект логгера.
    """
    def __init__(self, name, level=logging.DEBUG, fmt=None, log_file=None):
        """
        Создает новый объект логгера с заданным именем и уровнем логирования, а также форматтером,
        который определяет формат выводимых сообщений.

        :param name: Имя логгера.
        :type name: str
        :param level: Уровень логирования. По умолчанию `logging.DEBUG`.
        :type level: int
        :param fmt: Форматтер для сообщений. Если не задан, используется формат по умолчанию.
        :type fmt: str
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if fmt is None:
            fmt = '%(asctime)s - %(name)s - %(levelname)s - %(funcname)s - %(message)s'
        formatter = logging.Formatter(fmt)

        # создаем обработчик для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # добавляем обработчики к логгеру
        self.logger.addHandler(console_handler)

        # создаем обработчик для записи логов в файл
        if log_file is not None:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # настройка цветов для каждого уровня логирования
        coloredlogs.DEFAULT_LEVEL_STYLES = {
            'debug': {'color': 'white'},
            'info': {'color': 'green'},
            'warning': {'color': 'yellow'},
            'error': {'color': 'red'},
            'critical': {'color': 'red', 'bold': True},
        }

        # настройка формата вывода логов с использованием цветов
        coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(funcname)s - %(message)s'

        # установка логгера
        coloredlogs.install(level='DEBUG' if DEBUG else 'INFO', logger=self.logger, use_chroot=False)

    def debug(self, msg, *args, **kwargs):
        """
        Логирование сообщения уровня DEBUG.

        :param msg: сообщение.
        :type msg: str

        :param args: дополнительные аргументы для форматирования сообщения.
        :type args: Any

        :param kwargs: дополнительные параметры логгера.
        :type kwargs: Any

        :return: None
        """
        if DEBUG:
            frame = inspect.currentframe().f_back
            self.logger.debug(msg, *args, extra={'funcname': frame.f_code.co_name}, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Логирование сообщения уровня INFO.

        :param msg: сообщение.
        :type msg: str

        :param args: дополнительные аргументы для форматирования сообщения.
        :type args: Any

        :param kwargs: дополнительные параметры логгера.
        :type kwargs: Any

        :return: None
        """
        frame = inspect.currentframe().f_back
        self.logger.info(msg, *args, extra={'funcname': frame.f_code.co_name}, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Логирование сообщения уровня WARNING.

        :param msg: сообщение.
        :type msg: str

        :param args: дополнительные аргументы для форматирования сообщения.
        :type args: Any

        :param kwargs: дополнительные параметры логгера.
        :type kwargs: Any

        :return: None
        """
        frame = inspect.currentframe().f_back
        self.logger.warning(msg, *args, extra={'funcname': frame.f_code.co_name}, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Логирование сообщения уровня ERROR.

        :param msg: сообщение.
        :type msg: str

        :param args: дополнительные аргументы для форматирования сообщения.
        :type args: Any

        :param kwargs: дополнительные параметры логгера.
        :type kwargs: Any

        :return: None
        """
        frame = inspect.currentframe().f_back
        self.logger.error(msg + '\n' + traceback.format_exc(), *args, extra={'funcname': frame.f_code.co_name}, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Логирование сообщения уровня CRITICAL.

        :param msg: сообщение.
        :type msg: str

        :param args: дополнительные аргументы для форматирования сообщения.
        :type args: Any

        :param kwargs: дополнительные параметры логгера.
        :type kwargs: Any

        :return: None
        """
        frame = inspect.currentframe().f_back
        self.logger.critical(msg, *args, extra={'funcname': frame.f_code.co_name}, **kwargs)


logger = Logger("ReviewBot", log_file=BASE_DIR/'.log')
