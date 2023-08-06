# Use rel in place of pyevent
import rel
rel.initialize(["poll"])
rel.override()

import os
import sys

from dez.http.application import HTTPApplication
import django.core.handlers.wsgi

# Set the path where the django wsgi handler can find the "djangochat" module
# alternatively, comment out below line, and just run this script from the
# same path as the django module.
sys.path.insert(0, '/home/mcarter/tmp/orbited0.3demos/python')


def main():
    # the name of the django app is "djangochat"
    os.environ["DJANGO_SETTINGS_MODULE"] = "djangochat.settings"
    application = django.core.handlers.wsgi.WSGIHandler()    
    server = HTTPApplication("", 8888)
    
    # forward any traffic starting with '/' to the application
    # Note: in this case, that means all urls are sent to django
    server.add_wsgi_rule('/', application)
    # go
    server.start()
