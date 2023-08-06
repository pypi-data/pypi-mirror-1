from dez.http.application import HTTPApplication

def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    start_response(status, response_headers)
    return ['Hello world!\n']
    
def main(port):
    httpd = HTTPApplication("127.0.0.1", port)
    httpd.add_wsgi_rule("/", simple_app)
    httpd.start()
