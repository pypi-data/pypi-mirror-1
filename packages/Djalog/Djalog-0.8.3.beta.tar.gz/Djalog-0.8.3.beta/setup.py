from ez_setup import use_setuptools

use_setuptools()
VERSION = __import__('djalog').__version__

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    def find_packages():
        return ('djalog',)


setup(
    name = 'Djalog',
    version = VERSION,
    url = 'http://code.google.com/p/djalog',
    author = 'Lukasz Balcerzak',
    author_email = 'lukaszbalcerzak@gmail.com',
    description = 'Simple logging module for Django application.',
    packages = find_packages(),
    zip_safe = True,
    include_package_data = True,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent',
    ],
)
