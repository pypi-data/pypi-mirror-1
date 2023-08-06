import rel
rel.override()
rel.initialize(["poll"])
from dez.http.client import HTTPClient
import sys

if len(sys.argv) > 1:
    url = sys.argv[1]
else:
#    print sys.argv
    url = "http://www.google.com:80/search?q=orbited"
    
print 'Getting url "%s"' % (url,)
def main():
    c = HTTPClient()
    c.get_url(url, cb=req_cb)
    rel.signal(2, rel.abort)
    rel.dispatch()

def req_cb(response):
    print response.status_line

if __name__ == "__main__":
    main()
