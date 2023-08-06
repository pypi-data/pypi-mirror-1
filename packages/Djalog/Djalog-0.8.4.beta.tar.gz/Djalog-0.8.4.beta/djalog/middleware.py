from django.db import connection
# middleware is supposed to be used within django application
# so we are not afraid to import django settings
from django.conf import settings as django_settings 
from djalog.conf import settings

import logging

class SQLLoggingMiddleware:
    def process_response(self, request, response):
        if not settings.LOG_SQL:
            # Middleware, even if is turned on at settings module, won't do
            # anything if LOG_SQL is set to False
            return response
        if not django_settings.DEBUG:
            return response
        if not connection.queries:
            return response
        total_time = sum([ float(q['time']) for q in connection.queries])
        
        for query in connection.queries:
            msg = "Query : %s\nTime elapsed: %s" % (query['sql'], query['time'])
            logging.sql(msg)
        logging.sql("Total SQL time for request: %s" % total_time)
        
        return response
        
