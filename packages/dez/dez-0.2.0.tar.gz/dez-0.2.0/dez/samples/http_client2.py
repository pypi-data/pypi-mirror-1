from dez.http.client import HTTPClientRequest, HTTPClient
import rel as event
import time

def main():
    event.initialize(["pyevent"])
    client = HTTPClient()
    for i in range(20):
#        client.get_url("http://www.google.com/", cb=response_cb)
#        client.get_url("http://www.google.com/", cb=response_cb)
#        client.get_url("http://www.google.com/", cb=response_cb)
#        client.get_url("http://www.google.com/", cb=response_cb)
        client.get_url("http://localhost/", cb=response_cb, cbargs=[i+1])
    event.signal(2, event.abort)
    event.dispatch()
    
def response_cb(response, i):
#    print 'woot
    print i, time.time(), response.status_line
#    print response.headers
#    print "#########"    
#    print "body len:", len(response.body)
#    event.abort()    
