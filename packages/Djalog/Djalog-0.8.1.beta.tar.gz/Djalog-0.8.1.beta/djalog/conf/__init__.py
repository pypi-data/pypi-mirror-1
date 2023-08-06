import logging
import platform

from djalog import colored
from djalog.conf import settings
from djalog.loggers import DjalogLogger
from djalog.handlers import ConsoleHandler
from djalog.formatters import ColoredFormatter
from djalog.sqllogging import init_sql_logging

streamHandlerEmit = logging.StreamHandler.emit

def configure(**user_settings):
    """
    Configure or reconfigure djalog module.
    DjalogLogger is the name of main logger located
    at djalog.loggers. Additionally, logging.root becomes
    DjalogLogger by default..
    List of parameters with their default values:

    :param LOG_LEVEL=5 - sets level of logging for DjalogLogger

    :param LOG_FORMAT="%(asctime)s [%(levelname)s] %(message)s (File: %(filename)s:%(lineno)d)"
        this is format of the DjalogFileLogger

    :param LOG_DATE_FORMAT="%Y-%m-%d %H:%M:%S"
        this is date format used by %(asctime)s param inside normal format parameter

    :param LOG_FILE=None - a path to a file where
        logs should be stored if needed

    :param LOG_FILE_FORMAT="%(asctime)s [%(levelname)s] %(message)s"
        this if format for the DjalogFileLogger

    :param LOG_USE_COLORS=False - checks if logs (only main
        DjalogLogger) should use ANSI colors

    :param LOG_SQL=True - if True will use sql addtions from djalog.
        See djalog.init_sql_logging for more details

    :param LOG_SQL_LEVEL=5 - if using djalog sql logging additions
        it is the value of SQL logging level
    """
    
    # First we update settings module
    for key, val in user_settings.items():
        if hasattr(settings, key):
            setattr(settings, key, val)

    DjalogLogger.setLevel(settings.LOG_LEVEL)
    # Clean up handlers
    for x in xrange(len(DjalogLogger.handlers)):
        DjalogLogger.handlers.pop(0)
    handler = ConsoleHandler()
    DjalogLogger.addHandler(handler)

    # Setup file handler
    if settings.LOG_FILE:
        if callable(settings.LOG_FILE):
            # For instance, it may be set to tempfile.gettempdir
            settings.LOG_FILE = settings.LOG_FILE()
            DjalogLogger.debug("Setting log file to: %s" % settings.LOG_FILE)
        fileHandler = logging.FileHandler(settings.LOG_FILE)
        fileHandler.setFormatter(logging.Formatter(settings.LOG_FILE_FORMAT,
            settings.LOG_FILE_DATE_FORMAT))
        DjalogLogger.addHandler(fileHandler)

    # Initialize sql logging (or removes if LOG_SQL is False)
    #init_sql_logging(settings.LOG_SQL, level=settings.LOG_SQL_LEVEL)
    init_sql_logging()
    
