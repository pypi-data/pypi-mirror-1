import logging

from djalog.conf import configure
from djalog.loggers import DjalogLogger

VERSION = (0, 9, 0, 'stable')
__version__ = '.'.join(map(str, VERSION))

__all__ = ['configure', 'DjalogLogger', 'DjalogError']

configure()

def get_version():
    return __version__

