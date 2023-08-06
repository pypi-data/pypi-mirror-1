import urllib
from dez.buffer import Buffer
from dez.op.server.frame import Frame, SendFrame
from dez.http.client import HTTPClient

DELIM = "^@\r\n"
#DELIM = "\x00"

class OPConnection(object):
    id = 0
    def __init__(self, conn, validator):
        OPConnection.id += 1
        self.id = OPConnection.id
        self.conn = conn
        self.validator = validator
        self.ids = set()
        self.app_cb = self.__default_app_cb
        self.app_args = []
        self.callbacks = {
            "signon":False,
            "signoff":False,
            "failure":False,
            "success":False
        }
        self.http = HTTPClient()
        self.conn.set_rmode_delimiter(DELIM, self.__connect)

    def __default_app_cb(self, req):
        print "no application callback specified"

    def set_request_cb(self, cb, args=[]):
        self.app_cb = cb
        self.app_args = args

    def signon_cb(self, headers, body="", cb=None, cbarg=[]):
        self.callback("signon",headers,body,cb,cbarg)

    def signoff_cb(self, headers, body="", cb=None, cbarg=[]):
        self.callback("signoff",headers,body,cb,cbarg)

    def callback(self, func, headers, body="", cb=None, cbarg=[]):
        url = self.callbacks[func]
        if url:
            headers["function"] = func
            if url == True:
                return self.write("CALLBACK", headers, body, cb, cbarg)
            final_headers = []
            for key in headers:
                if key == 'recipients':
                    for recipient in headers['recipients']:
                        final_headers.append(('recipient', recipient))
                else:
                    final_headers.append((key, headers[key]))
            body = urllib.urlencode(final_headers)
            self.http.get_url(url, "POST", {}, cb, cbarg, body=body)

    def set_close_cb(self, cb, args=[]):
        self.conn.set_close_cb(cb, args)

    def __parse_headers(self, headers):
        s = ""        
        for key, val in headers.items():
            if key == "recipients":
                for r in val:
                    s += "recipient:"+str(r)+"\r\n"
            else:
                s += key+":"+val+"\r\n"
        return s

    def __connect(self, data):
        print 'CONNECT~!!'
        print data
        print
        req = Frame(self, Buffer(data, mode="consume"))
        if self.validator(req):
            if req.action != "CONNECT":
                return req.error("'CONNECT' not sent")
            self.response = req.headers.get("response","none")
            self.__forward(req)
            self.conn.set_rmode_delimiter(DELIM, self.__process)

    def __process(self, data):
        req = Frame(self, Buffer(data, mode="consume"))
        if req.action == "CONNECT":
            return req.error("'CONNECT' already sent")
        if self.validator(req):
            self.__forward(req)

    def __forward(self, req):
        if req.request_id in self.ids:
            return req.error("non-unique 'id':%s"%req.request_id)
        self.ids.add(req.request_id)
        if "response" not in req.headers:
            req.headers["response"] = self.response
        if self.__final_check(req):
            self.app_cb(req)

    def __final_check(self, req):
        if req.action == "SEND":
            req.__class__ = SendFrame
        elif req.action == "CALLBACK":
            f = req.headers['function']
            u = req.headers.get('url',True)
            if f not in self.callbacks:
                req.error("invalid function specified: \"%s\"\r\nlegitimate functions: signon, signoff, failure, success"%f)
                return False
            self.callbacks[f] = u
        return True

    def write(self, action, headers, body, cb, cbarg):
        s = action+"\r\n"
        s += self.__parse_headers(headers)
        s += "\r\n"+body+DELIM
        self.conn.write(s, cb, cbarg)

    def close(self):
        self.conn.close()
