from dez.http.client import HTTPClient
import sys, event

url = "http://www.google.com:80/search?q=orbited"
if len(sys.argv) > 1:
    url = sys.argv[1]
    
print 'Getting url "%s"' % (url,)
def main(port):
    c = HTTPClient()
    c.get_url(url, cb=req_cb)
    event.signal(2, event.abort)
    event.dispatch()

def req_cb(response):
    print response.status_line

