from dez.http.client import HTTPClientRequest, HTTPClient
import rel as event
import time

def main():
    event.initialize(["epoll"])
    l = LoadTester(600, 20)
#    event.signal(2, event.abort)
    event.timeout(20, event.abort)
    event.dispatch()
    
class LoadTester(object):
  
    def __init__(self, total=1000, concurrency=500):
        self.client = HTTPClient()
        self.client.client.start_connections('localhost', 80, concurrency, self.connections_open)
        self.time_start = time.time()
        self.responses = 0
        self.total = total
        
    def connections_open(self):
        print 'connections open'
        self.time_request_start = time.time()
        for i in range(self.total):
            self.client.get_url("http://localhost:80/index", cb=self.response_cb, cbargs=[i+1])
    
    def response_cb(self, response, i):
        self.responses += 1
#        print self.responses
        if self.responses == self.total:
            now = time.time()
            print 'time open conn:', self.time_request_start - self.time_start
            print 'time %s requests' % self.total, now - self.time_start
            print "Req/sec:", self.total / (now - self.time_start)
#            print 'completed'
            event.abort()
      
    
if __name__ == "__main__":
    main()