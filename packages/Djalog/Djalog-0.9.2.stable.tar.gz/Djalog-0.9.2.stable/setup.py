from setuptools import setup, find_packages

djalog = __import__('djalog')
VERSION = djalog.get_version()

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
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent',
    ],
)
