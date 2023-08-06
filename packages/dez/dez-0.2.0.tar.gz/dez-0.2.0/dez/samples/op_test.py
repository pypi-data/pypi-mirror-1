from dez.op.server.server import OPServer
from dez.op.server.message import OPMessage
import random,event

def deliver(d):
    event.timeout(random.random(),random.choice([d.success,d.failure]))

class TestApp(object):
    def __init__(self):
        self.connections = {}

    def connection_opened(self, conn):
        print 'connection_opened'
        conn.set_request_cb(self.request)
        self.connections[conn.id] = conn

    def connection_closed(self, conn):
        del self.connections[conn.id]

    def request(self, req):
        print 'request'
        if getattr(self,req.action.lower())(req):
            req.received()

    def welcome(self, req):
        return True

    def unwelcome(self, req):
        return True

    def callback(self, req):
        return True

    def connect(self, req):
        cid = req.headers["connection_id"]
        if cid in self.connections:
            print 'connection_id in use'
            req.error("'connection_id' %s in use"%cid)
            return False
        return True

    def send(self, req):
        msg = OPMessage(req.body, req.headers["recipients"], self.msg_outcome, [req])
        for r in msg.recipients:
            deliver(msg.single_recipient_event(r))
        return True

    def msg_outcome(self, succeeded, failed, req):
        if succeeded:
            req.success(succeeded)
        if failed:
            req.failure(failed)

def main(addr="localhost", port=9999):
    app = TestApp()
    server = OPServer(addr, port)
    server.set_connect_cb(app.connection_opened)
    server.start()

if __name__ == "__main__":
    main()
