import time
import traceback
from functools import wraps

from src.core.logger import logger

def handle_errors(critical=False, default_return=None):
    yellow = "\x1b[38;5;229m"
    reset = "\x1b[38;5;15m"
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                logger.warning(f"{yellow}{func.__name__}{reset}")
                return await func(*args, **kwargs)
            except Exception as e:
                if critical:
                    logger.critical(f"Error in {func.__name__}: {e}")
                    logger.critical(traceback.format_exc())
                else:
                    logger.error(f"Error in {func.__name__}: {e}")
                    logger.error(traceback.format_exc())
                return default_return
        return wrapper
    return decorator