
#
# WSGI
#

class WSGIObject(object):
    def __init__(self, flow, default_status='200 OK', default_headers=[('Content-Type', 'text/html')]):
        self.status = default_status
        self.headers = [x for x in default_headers]
        self.exc_info = None
        self.response = []
        self.environ = None

        # start_response objects
        self.buffer = []
        self.flow = flow
        self.result_returned = False
        self.start_response_called = False
        self.data_written = False
        self.error_handled = False

    def write(self, data):
        if not self.data_written:
            self.data_written = True
        if not self.start_response_called:
            raise Exception('You cannot write unitl start_response() has been called')
        if self.result_returned:
            raise Exception('The result has already been returned, you cannot write more data')
        self.buffer.append((len(self.flow.wsgi.response), data))

    def start_response(self, status, headers, exc_info=None):
        if self.start_response_called and exc_info is None:
            raise Exception('start_response() has already been called and no exc_info is present')
        self.start_response_called = True
        if self.result_returned:
            raise Exception('The result has already been returned')
        self.status = status
        self.headers = headers
        self.exc_info = exc_info
        return self.write

    def get_result(self):
        if self.result_returned:
            raise Exception('The result has already been returned, you cannot get it again')
        self.result_returned = True
        if self.data_written:
            counter = 0
            for pos, data in self.buffer:
                self.flow.wsgi.response.insert(pos+counter, data)
                counter += 1
        return ResultIterator(self.response)

class ResultIterator:
    def __init__(self, response, charset='utf8'):
        self.response = response
        if not isinstance(self.response, list):
            raise TypeError('The response must be a list of strings and iterables, not %r'%type(response))
        self.index = -1
        self.sub_index = None
        self.charset = charset

    def __iter__(self):
        return self

    def main_result(self):
        part = self.response[self.index]
        if isinstance(part, str):
            return part
        elif isinstance(part, unicode):
            return part.encode(self.charset)
        else:
            self.sub_index = 0
            return self.secondary_result()

    def secondary_result(self):
        part = self.response[self.index]
        if isinstance(part, str):
            return part
        elif isinstance(part, unicode):
            return part.encode(self.charset)
        elif hasattr(part, '__iter__'):
            return u''.join([x for x in part]).encode(self.charset)
        else:
            raise TypeError(
                'Expected an iterable, unicode or binary string, not %r in '
                'response[%s][%s]'%(
                    type(self.response), self.index, self.sub_index
                )
            )

    def next(self):
        if self.index+2 > len(self.response):
            raise StopIteration
        elif self.sub_index is None:
            self.index += 1
            return self.main_result()
        else:
            # We are inside a secondary iterable
            if self.sub_index+1 > len(self.response[self.index]):
                # This is the end, return the first part of the next iterable instead
                self.sub_index = None
                self.index += 1
                return self.main_result()
            else:
                self.sub_index += 1
                return self.secondary_result()

class WSGIService(object):

    @staticmethod
    def create(flow, name, config=None):
        return WSGIService()

    @staticmethod
    def config(flow, name):
        # No configuration 
        return None

    def start(self, flow, name):
        flow[name] = WSGIObject(flow)
 

