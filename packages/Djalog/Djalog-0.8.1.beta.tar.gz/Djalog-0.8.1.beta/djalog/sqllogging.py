import logging

from djalog.conf import settings
from djalog.loggers import DjalogLogger

def sql(msg):
    """
    Basic log sql function.
    """
    # Preformat message
    msg = msg.replace('SELECT', '\n\tSELECT')\
        .replace('FROM', '\n\tFROM')\
        .replace('ORDER BY', '\n\tORDER BY')\
        .replace('LIMIT', '\n\tLIMIT')\
        .replace('WHERE', '\n\tWHERE')\
        .replace('AND', '\n\tAND')\
        .replace('LEFT', '\n\tLEFT')\
        .replace('INNER', '\n\tINNER')
        
    DjalogLogger.log(logging.SQL, msg)

def init_sql_logging():
    """
    Initializes SQL logging settings or
    removes it from logging module.
    """
    # Clears SQL level / log_sql method
    def remattr(obj, attr):
        if hasattr(obj, attr):
            delattr(obj, attr)
    #DjalogLogger.debug("settings.LOG_SQL is set to %s" % settings.LOG_SQL)
    if settings.LOG_SQL:
        logging.addLevelName(settings.LOG_SQL_LEVEL, levelName='SQL')
        logging.SQL = settings.LOG_SQL_LEVEL
        logging.sql = sql
        DjalogLogger.sql = sql
    else:
        remattr(logging, 'SQL')
        remattr(logging, 'sql')
        remattr(DjalogLogger, 'sql')

