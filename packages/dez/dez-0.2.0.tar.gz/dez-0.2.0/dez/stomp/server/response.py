from dez.stomp.server.default import DELIM

class STOMPResponse(object):
    def __init__(self, msg_type, headers={}, body="", cb=None, args=[], close=False):
        self.msg_type = msg_type
        self.headers = headers
        self.body = body
        self.cb = cb
        self.args = args
        self.close = close

    def complete(self):
        if self.cb:
            self.cb(*self.args)
        if self.close:
            self.close()

    def render(self):
        msg_string = self.msg_type+'\r\n'
        for h in self.headers:
            msg_string+=h+':'+self.headers[h]+'\r\n'
        msg_string += '\r\n'+self.body+DELIM
        return msg_string
