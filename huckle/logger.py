import logging
import traceback
import os
import io
import datetime
import threading
import collections
from logging.handlers import RotatingFileHandler

from huckle import config

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


# custom logger implementation that allows for streaming to file.
class Logger:
    instance = None
    streamHandler = None
    initialized = False
    lock = None

    def __new__(cls, *args, **kwargs):
        cls.lock = threading.RLock()
        with cls.lock:
            if cls.instance is None:
                cls.instance = super(Logger, cls).__new__(cls)
            return cls.instance

    def __init__(self, log=None, max_bytes=10485760, backup_count=5, *args, **kwargs):
        with self.lock:
            if not self.initialized:
                self.instance = logging.getLogger("huckle")

                date_format = "%Y-%m-%d %H:%M:%S %z"
                message_format = "[%(asctime)s] [%(levelname)-5s] [%(filename)13s:%(lineno)-3s] %(message)s"
                formatter = logging.Formatter(fmt=message_format, datefmt=date_format)

                # File handler (if log_file is provided)
                # NullHandler otherwise to prevent any output
                if log == 'log':
                    log_file = config.log_file_path
                    self.fileHandler = RotatingFileHandler(
                        log_file,
                        maxBytes=max_bytes,
                        backupCount=backup_count,
                        encoding='utf-8'
                    )
                    self.fileHandler.setFormatter(formatter)
                    self.instance.addHandler(self.fileHandler)
                else:
                    self.instance.addHandler(logging.NullHandler())

                self.initialized = True

    def setLevel(self, level):
        logging.getLogger("huckle").setLevel(level)
        return

    def info(self, msg, *args, **kwargs):
        self.instance.info(msg, *args, stacklevel=2, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.instance.debug(msg, *args, stacklevel=2, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.instance.warning(msg, *args, stacklevel=2, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.instance.error(msg, *args, stacklevel=2, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.instance.critical(msg, *args, stacklevel=2, **kwargs)
