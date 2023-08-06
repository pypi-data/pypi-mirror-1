import cgi
import StringIO

class HTTPInputService(object):

    @staticmethod
    def create(flow, name, config=None):
        return HTTPInputService()

    @staticmethod
    def config(flow, name):
        # There is no configuration
        return None

    def start(self, flow, name):
        if not flow.has_key('http'):
            raise Exception(
                'Expected the HTTP service to be present as flow.http'
            )
        if flow.wsgi.environ.get('wsgi.input') and \
           flow.wsgi.environ.get('REQUEST_METHOD', '').upper() == "POST":
            s = StringIO.StringIO()
            try:
                request_body_len = int(flow.wsgi.environ['CONTENT_LENGTH'])
                input = flow.wsgi.environ['wsgi.input'].read(request_body_len)
            except (TypeError, ValueError):
                raise Exception('Invalid HTTP post, no valid CONTENT_LENGTH')
            s.write(input)
            s.seek(0)
            flow.http[name] = cgi.FieldStorage(
                fp=s, 
                environ=flow.wsgi.environ, 
                keep_blank_values=True
            )
            s.seek(0)
            flow.wsgi.environ['wsgi.input'] = s
        else:
            flow.http[name] = None

