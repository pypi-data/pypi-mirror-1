
from bn import AttributeDict

class WSGIProxy(AttributeDict):
    def __init__(self, flow):
        self['flow'] = flow

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __setattr__(self, name, value):
        return self.__setitem__(name, value)

    def __getitem__(self, name):
        if name == 'response':
            return self.flow.wsgi.response
        elif name == 'status':
            return self.flow.wsgi.status
        elif name == 'headers':
            return self.flow.wsgi.headers
        else:
            return AttributeDict.__getitem__(self, name)

    def __setitem__(self, name, value):
        if name == 'response':
            self.flow.wsgi.response = value
        elif name == 'status':
            self.flow.wsgi.status = value
        elif name == 'headers':
            self.flow.wsgi.headers = value
        else:
            return AttributeDict.__setitem__(self, name, value)

class HTTPService(object):

    @staticmethod
    def create(flow, name, config=None):
        return HTTPService()

    @staticmethod
    def config(flow, name):
        # There is no configuration
        return None

    def start(self, flow, name):
        if not flow.has_key('wsgi'):
            raise Exception('Expected the WSGI service to be present as flow.wsgi')
        flow[name] = WSGIProxy(flow)

