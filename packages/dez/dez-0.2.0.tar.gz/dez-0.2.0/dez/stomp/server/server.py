from dez.buffer import Buffer
from dez.network.server import SocketDaemon
from dez.stomp.server.request import STOMPRequest
from dez.stomp.server.default import DefaultCommands, DefaultValidator, DELIM

defaultcmd = DefaultCommands()
defaultval = DefaultValidator()

class STOMPConnection(object):
    def __init__(self, conn):
        self.conn = conn
        self.val = defaultval
        self.val_args = []
        self.cbs = defaultcmd
        self.cb_args = []
        self.close_cb = None
        self.close_args = []
        self.connected = False
        self.conn.set_rmode_delimiter(DELIM, self.process)

    def set_validator(self, validator, *args):
        self.val = validator
        self.val_args = args

    def set_request_cb(self, request_cb, *args):
        self.cbs = request_cb
        self.cb_args = args

    def set_close_cb(self, close_cb, *args):
        self.close_cb = close_cb
        self.close_args = args

    def process(self, data):
        req = STOMPRequest(self,Buffer(data))
        cmd = req.action.lower()
        if not self.connected and cmd != "connect":
            req.error('CONNECT not sent')
        elif self.connected and cmd == "connect":
            req.error('CONNECT sent twice')
        elif self.val(req, *self.val_args):
            self.check_receipt(req)

    def check_receipt(self, req):
        if 'receipt' in req.headers:
            return req.receipt(req.headers['receipt'],self.cbs,[req]+self.cb_args)
        self.cbs(req, *self.cb_args)

    def respond(self, response):
        self.conn.write(response.render(),response.complete)

    def close(self):
        if self.close_cb:
            self.close_cb(*self.close_args)
        self.conn.close()

class STOMPServer(object):
    def __init__(self, addr, port, cb=STOMPConnection):
        self.server = SocketDaemon(addr, port, cb=cb)
        self.server.start()
