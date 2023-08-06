import mimetypes, os

class NaiveCache(object):
    def __init__(self):
        self.cache = {}

    def get(self, req, path, write_back, stream_back, err_back):
        if path in self.cache and self.cache[path]['mtime'] == os.path.getmtime(path):
            return write_back(req, path)
        if os.path.isfile(path):
            mimetype = mimetypes.guess_type(req.url)[0]
            if not mimetype:
                mimetype = "application/octet-stream"
            self.cache[path] = {'mtime':os.path.getmtime(path),'type':mimetype,'content':''}
            stream_back(req, path)
        else:
            err_back(req)

class INotifyCache(object):
    def __init__(self):
        # you will probably populate self.cache right here to begin with
        # self.cache[path] = {'content':whatever,'type':mimetype}
        # set up inotification with callback self.__update
        raise Exception, "not implemented"

    def __update(self, path):
        #self.cache[path] = {'content':whatever,'type':mimetype}
        pass

    def get(self, req, path, write_back, stream_back, err_back):
        # if path in self.cache:
        #    return write_back(req, path)
        # else:
        #    err_back(req)
        pass
