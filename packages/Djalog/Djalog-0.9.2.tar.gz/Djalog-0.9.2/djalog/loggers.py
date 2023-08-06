import logging
import tempfile

from djalog.conf import settings
from djalog.handlers import ConsoleHandler

# Create loggers
DjalogLogger = logging.getLogger("DjalogLogger")
Logger = DjalogLogger # Temp

# Set level
DjalogLogger.setLevel(settings.LOG_LEVEL)

DjalogLogger.addHandler(ConsoleHandler())

# Set as default logger
if logging.root.name != 'DjalogLogger':
    logging.root = DjalogLogger

#logging.debug("Using logging level %s" % logging.root.level)

