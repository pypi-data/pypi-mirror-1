DELIM = "^@\r\n" # telnet (test)
#DELIM = "\0" # null byte (real)

class DefaultValidator(object):
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "DefaultAuthenticator"

    def __call__(self, req):
        if req.problem:
            req.error()
            return False
        return getattr(self,req.action.lower())(req)

    def _error(self, req):
        estring = "AUTHENTICATOR:"+str(self)
        estring += "\nCOMMAND:"+req.action
        estring += "\nHEADERS:"+str(req.headers)
        return estring

    def connect(self, req):
        if "receipt" in req.headers:
            req.error("receipt header in CONNECT",self._error(req))
            return False
        if "login" not in req.headers:
            req.error("login header not in CONNECT",self._error(req))
            return False
        if "passcode" not in req.headers:
            req.error("passcode header not in CONNECT",self._error(req))
            return False
        return True

    def send(self, req):
        if "destination" not in req.headers:
            req.error("destination header not in SEND",self._error(req))
            return False
        return True

    def subscribe(self, req):
        if "destination" not in req.headers:
            req.error("destination header not in SUBSCRIBE",self._error(req))
            return False
        return True

    def unsubscribe(self, req):
        if "destination" not in req.headers and "id" not in req.headers:
            req.error("destination header and id header not in UNSUBSCRIBE (you need at least one)",self._error(req))
            return False
        return True

    def begin(self, req):
        if "transaction" not in req.headers:
            req.error("transaction header not in BEGIN",self._error(req))
            return False
        return True

    def commit(self, req):
        if "transaction" not in req.headers:
            req.error("transaction header not in COMMIT",self._error(req))
            return False
        return True

    def abort(self, req):
        if "transaction" not in req.headers:
            req.error("transaction header not in ABORT",self._error(req))
            return False
        return True

    def ack(self, req):
        if "message-id" not in req.headers:
            req.error("message-id header not in ACK",self._error(req))
            return False
        return True

    def disconnect(self, req):
        return True

class DefaultCommands(object):
    def __init__(self):
        self.session_id = 0

    def __call__(self, req, *args):
        print 'default command handler called'
        print 'args:',args
        getattr(self,req.action.lower())(req)

    def connect(self, req):
        req.connected(self.session_id)
        self.session_id += 1

    def send(self, req):
        print 'this server does not support send'

    def subscribe(self, req):
        print 'this server does not support subscribe'

    def unsubscribe(self, req):
        print 'this server does not support unsubscribe'

    def begin(self, req):
        print 'this server does not support begin'

    def commit(self, req):
        print 'this server does not support commit'

    def abort(self, req):
        print 'this server does not support abort'

    def ack(self, req):
        print 'this server does not support ack'

    def disconnect(self, req):
        print 'default disconnect'
        req.conn.close()