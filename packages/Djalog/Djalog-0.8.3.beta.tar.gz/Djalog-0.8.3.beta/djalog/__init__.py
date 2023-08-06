import logging

from djalog.conf import configure
from djalog.loggers import DjalogLogger

VERSION = (0, 8, 3, 'beta')
__version__ = '.'.join(map(str, VERSION))

__all__ = ['configure', 'DjalogLogger', 'DjalogError']

configure()

