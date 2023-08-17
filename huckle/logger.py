import logging
import traceback
import os
import io
import datetime
import threading
import collections

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# custom deque implementation to have log line limits as a sliding window that behaves like a stream being consumed when read.
class DequeHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deque = collections.deque(maxlen=100)

    def emit(self, record):
        log_entry = self.format(record)
        self.deque.append(log_entry)

    def read_and_clear(self):
        logs = list(self.deque)
        self.deque.clear()
        return logs

# custom logger implementation that allows for streaming to stdout and tailing of logs per a deque sliding window.
class Logger:
    instance = None
    streamHandler = None
    clientHandler = None
    initialized = False
    lock = None

    def __new__(self, *args, **kwargs):
        self.lock = threading.Lock()
        with self.lock:
            if self.instance is None:
                self.instance = super().__new__(self, *args, **kwargs)
            return self.instance

    def __init__(self, *args, **kwargs):
        with self.lock:
            if not self.initialized:
                self.instance = logging.getLogger("crumbs")

                date_format = "%Y-%m-%d %H:%M:%S %z"
                message_format = "[%(asctime)s] [%(levelname)-5s] [%(filename)13s:%(lineno)-3s] %(message)s"

                formatter = logging.Formatter(fmt=message_format, datefmt=date_format)

                self.streamHandler = logging.StreamHandler()
                self.streamHandler.setFormatter(formatter)
                self.instance.addHandler(self.streamHandler)

                self.clientHandler = DequeHandler()
                self.clientHandler.setFormatter(formatter)
                self.instance.addHandler(self.clientHandler)

                self.initialized = True

    def setLevel(self, level):
        logging.getLogger("crumbs").setLevel(level)
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

    def tail(self):
        log_entries = self.clientHandler.read_and_clear()
        log_text = '\n'.join(log_entries)

        if log_text:
            log_text += '\n'  # Adds newline character at the end if there is some log_text

        return log_text.encode('utf-8')
