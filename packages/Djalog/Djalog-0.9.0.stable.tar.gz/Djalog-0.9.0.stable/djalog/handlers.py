import logging
import platform

from djalog import colored
from djalog.conf import settings
from djalog.formatters import ColoredFormatter

def ConsoleHandler():
    """
    Factory-method returns StreamHandler with
    dynamically created formatter according to
    djalog.conf.settings module.
    """
    ch = logging.StreamHandler()
    if settings.LOG_USE_COLORS:
        if platform.system().lower() not in colored.SUPPORTED_PLATFORMS:
            logging.warn("Cannot use colored output on this platform. Currently "
                "supported platforms are: %s." % ' '.join(colored.SUPPORTED_PLATFORMS))
        ch.setFormatter(ColoredFormatter(settings.LOG_FORMAT, settings.LOG_DATE_FORMAT))
    else:
        ch.setFormatter(logging.Formatter(settings.LOG_FORMAT, settings.LOG_DATE_FORMAT))
    return ch

