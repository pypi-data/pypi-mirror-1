import pprint
from dez.http.application import HTTPApplication
port = 8888

def simple_app(environ, start_response):
    print 'POST DATA:'
    print environ['wsgi.input'].read()
    print '===='
    pprint.pprint(environ)
    
def main():
    httpd = HTTPApplication("127.0.0.1", port)
    httpd.add_wsgi_rule("/", simple_app)
    httpd.start()
