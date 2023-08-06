"""\
Query string service
"""

import cgi
import logging

log = logging.getLogger(__name__)

class HTTPQueryService(object):

    @staticmethod
    def create(flow, name, config=None):
        return HTTPQueryService()

    @staticmethod
    def config(flow, name):
        # There is no configuration
        return None

    def start(self, flow, name):
        if not flow.has_key('http'):
            raise Exception('Expected the HTTP service to be present as flow.http')
        if flow.wsgi.environ.get('QUERY_STRING') and flow.wsgi.environ.get('REQUEST_METHOD', '').upper() == "GET":
            flow.http[name] = cgi.FieldStorage(environ=flow.wsgi.environ, keep_blank_values=True)
        else:
            flow.http[name] = None

