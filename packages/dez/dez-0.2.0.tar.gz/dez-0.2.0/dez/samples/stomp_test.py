from dez.stomp.server.server import STOMPServer, STOMPConnection

class TestServer(object):
    def __init__(self):
        self.groups = {}
        self.names = {}
        self.message_id = 0

    def invalid_auth_data(self, req):
        if req.headers['login'] == 'carn':
            return True
        return False

    def group_message(self, group, message):
        for member in self.groups[group]:
            member.message(group, self.message_id, message)
        self.message_id += 1

    def request_cb(self, req, *args):
        print 'request_cb called'
        print 'args',args
        print 'request:'
        print '----'
        print req
        print '----'
        if req.action == "CONNECT":
            if self.invalid_auth_data(req):
                return req.error("invalid auth data")
            name = req.headers['login']
            print 'new user:',name
            self.names[req.conn] = name
            req.connected(name)
        elif req.action == "DISCONNECT":
            print 'user left:',self.names[req.conn]
            del self.names[req.conn]
            req.conn.close()
        elif req.action == "SEND":
            print "a send request!"
            group = req.headers['destination']
            if group not in self.groups:
                print 'new group:',group
                self.groups[group] = []
            self.group_message(group,'%s says %s'%(self.names[req.conn],req.body))
        elif req.action == "SUBSCRIBE":
            print 'a subscribe request!'
            group = req.headers['destination']
            if group not in self.groups:
                print 'new group:',group
                self.groups[group] = []
            self.groups[group].append(req)
            self.group_message(group,"%s has joined"%self.names[req.conn])
        else:
            print "Don't know how to handle %s action" % req.action
            req.error("This server doesn't support %s action" % req.action)

    def close_cb(self, conn, *args):
        print 'connection %s closed' % conn
        print 'args:',args

    def connect_cb(self, c):
        conn = STOMPConnection(c)
        conn.set_request_cb(self.request_cb, 'print', 'this', 'out')
        conn.set_close_cb(self.close_cb, 'conn', 'closed')

def main(addr='localhost', port=8888):
    test = TestServer()
    server = STOMPServer(addr, port, test.connect_cb)

def main2(addr="localhost", port=8888):
    server = STOMPServer(addr, port)

if __name__ == "__main__":
    main()
