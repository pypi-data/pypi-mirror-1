from dez.stomp.server.response import STOMPResponse

class STOMPRequest(object):
    def __init__(self, conn, buffer):
        self.conn = conn
        self.buffer = buffer.data
        self.action = None
        self.headers = {}
        self.body = None
        try:
            self.problem = "error parsing command"
            tbreak = buffer.find('\r\n')
            self.action = buffer.part(0,tbreak)
            buffer.move(tbreak+2)

            self.problem = "error parsing headers"
            hbreak = buffer.find('\r\n\r\n')
            if hbreak != -1:
                self.get_headers(buffer.part(0,hbreak))
                buffer.move(hbreak+4)

            self.problem = "error parsing body"
            self.body = buffer.part(0,len(buffer))

            self.problem = None
        except:
            print 'STOMPRequest error:',self.problem
        print self

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.buffer

    def get_headers(self, head):
        self.headers = {}
        for header in head.split('\r\n'):
            key, val = header.split(':')
            self.headers[key] = val

    def connected(self, s):
        self.conn.connected = True
        self.respond("CONNECTED",{"session":str(s)})

    def message(self, dest, mid, body=""):
        self.respond("MESSAGE",{"destination":dest,"message-id":str(mid)},body)

    def receipt(self, rid, cb=None, cbarg=[]):
        self.respond("RECEIPT",{"receipt-id":rid},"",cb,cbarg)

    def error(self, problem=None, body=""):
        if not problem:
            problem = self.problem
        self.respond("ERROR",{"message":problem},body,close=self.conn.close)

    def respond(self, action, headers={}, body="", cb=None, args=[], close=False):
        self.conn.respond(STOMPResponse(action,headers,body,cb,args,close))
