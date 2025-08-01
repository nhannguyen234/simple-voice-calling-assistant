import logging
import pytz
import traceback
from uuid import uuid4
from datetime import datetime
from contextvars import ContextVar

call_id_var = ContextVar('call_id', default=uuid4())
class ThreadIDFilter(logging.Filter):
    def filter(self, record):
        record.call_id = call_id_var.get()
        return True

def exception_logging(exctype, value, tb):
    """
    Log exception by using the root logger.
    """
    write_val = {'exception_type': exctype.__name__,
                 'message': str(value) + " Traceback: " + str(traceback.format_tb(tb, 10))}
    logger.error(str(write_val))

class CustomFormatter(logging.Formatter):

    green = "\x1b[0;32m"
    grey = "\x1b[38;5;248m"
    yellow = "\x1b[38;5;229m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[38;5;31m"
    white = "\x1b[38;5;255m"
    reset = "\x1b[38;5;15m"
    
    base_format = (f"{grey}%(asctime)s | {{level_color}}%(levelname)-8s{grey} | {blue}%(module)s:%(lineno)d{grey} - {white}%(message)s")
    
    FORMATS = {
        logging.INFO: base_format.format(level_color=green),
        logging.WARNING: base_format.format(level_color=yellow),
        logging.ERROR: base_format.format(level_color=red),
        logging.CRITICAL: base_format.format(level_color=bold_red),
    }

    def format(self, record):
        record.call_id = call_id_var.get()
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def custom_logger(app_name="APP"):
    logger_r = logging.getLogger(name=app_name)
    logger_r.propagate = False  # Prevent propagation to root logger
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.propagate = False
    tz = pytz.timezone("Asia/Ho_Chi_Minh")  # Set the timezone to Ho_Chi_Minh

    logging.Formatter.converter = lambda *args: datetime.now(tz).timetuple()

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(CustomFormatter())
    ch.addFilter(ThreadIDFilter())
    
    logger_r.setLevel(logging.INFO)
    logger_r.addHandler(ch)
    return logger_r

logger = custom_logger(app_name="Synergies Global Simple App")