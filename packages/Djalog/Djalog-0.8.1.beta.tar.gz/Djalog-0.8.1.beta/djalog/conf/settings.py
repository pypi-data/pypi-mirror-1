'''
Concept and most code taken from one
of the snippets at djangosnippets.com
'''
import logging

DEFAULT_LEVEL = logging.INFO

FORMAT = "%(asctime)s [%(levelname)s] %(message)s" # (File: %(filename)s:%(lineno)d)"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

FILE_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
FILE_DATE_FORMAT = DATE_FORMAT

try:
    from django.conf import settings
    settings.configure() # Import alone won't raise exception
except ImportError:
    settings = object()
except RuntimeError:
    # Means django settings module is configured already
    pass
    
# Default settings or given with settings module
LOG_FORMAT = getattr(settings, 'DJALOG_FORMAT', FORMAT)
LOG_DATE_FORMAT = getattr(settings, 'DJALOG_DATE_FORMAT', DATE_FORMAT)
LOG_FILE = getattr(settings, 'DJALOG_FILE', None)
LOG_FILE_FORMAT = getattr(settings, 'DJALOG_FILE_FORMAT', FILE_FORMAT)
LOG_FILE_DATE_FORMAT = getattr(settings, 'DJALOG_FILE_DATE_FORMAT', FILE_DATE_FORMAT)
LOG_SQL = getattr(settings, 'DJALOG_SQL', False)
LOG_SQL_LEVEL = getattr(settings, 'DJALOG_SQL_LEVEL', 5)
LOG_LEVEL = getattr(settings, 'DJALOG_LEVEL', DEFAULT_LEVEL)
LOG_USE_COLORS = getattr(settings, 'DJALOG_USE_COLORS', False)
