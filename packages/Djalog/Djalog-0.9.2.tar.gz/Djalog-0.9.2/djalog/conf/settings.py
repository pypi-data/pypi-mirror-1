'''
Concept and most code taken from one
of the snippets at djangosnippets.com
'''
import sys
import logging

DEFAULT_LEVEL = logging.INFO

FORMAT = "%(asctime)s [%(levelname)s] %(message)s" # (File: %(filename)s:%(lineno)d)"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

FILE_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
FILE_DATE_FORMAT = DATE_FORMAT

try:
    from django.conf import settings as django_settings
    if django_settings.configured is False:
        django_settings = object()
except ImportError:
    django_settings = object()

# Default settings or given with settings module
LOG_FORMAT = getattr(django_settings, 'DJALOG_FORMAT', FORMAT)
LOG_FORMAT_LINEO = getattr(django_settings, 'DJALOG_FORMAT_LINEO', False)
LOG_DATE_FORMAT = getattr(django_settings, 'DJALOG_DATE_FORMAT', DATE_FORMAT)
LOG_FILE = getattr(django_settings, 'DJALOG_FILE', None)
LOG_FILE_FORMAT = getattr(django_settings, 'DJALOG_FILE_FORMAT', FILE_FORMAT)
LOG_FILE_DATE_FORMAT = getattr(django_settings, 'DJALOG_FILE_DATE_FORMAT', FILE_DATE_FORMAT)
LOG_SQL = getattr(django_settings, 'DJALOG_SQL', False)
LOG_SQL_LEVEL = getattr(django_settings, 'DJALOG_SQL_LEVEL', 5)
LOG_LEVEL = getattr(django_settings, 'DJALOG_LEVEL', DEFAULT_LEVEL)
LOG_USE_COLORS = getattr(django_settings, 'DJALOG_USE_COLORS', False)
LOG_STREAM = getattr(django_settings, 'DJALOG_STREAM', sys.stdout)

