from dez.network.server import SocketDaemon
from dez.op.server.connection import OPConnection
from dez.op.server.validator import OPValidator
from dez.op.server.message import OPMessage

cbs = ['signon','signoff','failure','success']

class OPServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.daemon = SocketDaemon(host, port, self.__connect_cb)
        self.connections = []
        self.val = OPValidator()
        self.__app_connect_cb = None
        
    def __connect_cb(self, raw_conn):
        conn = OPConnection(raw_conn, self.val)
        self.connections.append(conn)
        if self.__app_connect_cb:
            cb, args = self.__app_connect_cb
            cb(conn *args)
            
    def set_conn_cb(self, cb, args=[]):
        self.__app_connect_cb = (cb, args)

    def callback(self, function, headers={}, body="", cb=None, cbarg=[]):
        """
        send_cb("signon",{"key":ukey})
        send_cb("signoff",{"key":ukey,"type":dc_type})
        send_cb("success",{"id":msg_id,"recipients":succ_list})
        send_cb("failure",{"id":msg_id,"recipients":fail_list})
        """
        headers["function"] = function
        cbr = CallbackRequest(cb, cbarg, self.connections)
            
class CallbackRequest(object):
  
    def __init__(self,cb, args, connections):
        self.orig_cb = cb
        self.orig_args = args
        self.count = 0
        self.outstanding = 0
        for connection in connections:
            if connection.callback(function, headers, body, self.cb):
                self.outstanding += 1
            
    def cb(self):
        self.count += 1
        self.check()
        
    def check(self):
        if self.count == self.outstanding:
            self.orig_cb(*self.args)