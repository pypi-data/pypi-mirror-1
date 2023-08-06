===============================================
Djalog - Simplest Django-ready logger out there
===============================================

------------
Introduction
------------

Djalog provides ready-to-use logger. This is very simple logging_ wrapper,
if you are looking for something more decent try django-logging_.
 
------------
Installation
------------

In order to install Djalog you may use setuptools:

.. code-block:: sh
   
    easy_install Djalog

Note that Djalog requires logging module which is available from Python 2.3.

-----
Usage
-----

If you want to quickly check how djalog works, go into your favorite python
shell and type:

.. code-block:: python

    import djalog
    import logging

    logging.debug("Log some debug information.")
    logging.info("Log some information.")
    logging.warn("Log some warning.")
    logging.error("Log some error.")
    logging.critical("Log some critical information.")

    from djalog import configure
    configure(LOG_USE_COLORS=True, LOG_SQL=True, LOG_LEVEL=5)

    logging.debug("Log some debug information.")
    logging.info("Log some information.")
    logging.warn("Log some warning.")
    logging.error("Log some error.")
    logging.critical("Log some critical information.")

    # Log sql query
    logging.sql("SELECT * FROM users WHERE username = 'admin'")

From this example you can see that changing settings for djalog utility can be
done with `djalog.configure` method.

----------------
How does it work
----------------

Djalog is simplest possible approach for Django logging_. In fact, it can be
easily used outside of the Django context (see example at the `Usage`_
section).

*WARNING*: Djalog is simple but in some cases it uses internal mechanisms of
the logging_ module which may not always be desirable. For example it switches
`logging.root` logger with `djalog.loggers.DjalogLogger` or if `LOG_SQL` is set
to `True` (see DjalogSql) there will be added simple `sql` method to the
logging_ module. 

----------
References
----------

.. _logging: http://docs.python.org/library/logging.html
.. _django-logging: http://code.google.com/p/django-logging/
