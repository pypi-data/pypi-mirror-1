import threading
from urllib2 import urlopen, URLError, HTTPError
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from contextlib import contextmanager

class StopableHTTPServer(HTTPServer):
    stopped = False
    
    def serve_forever(self):
        while not self.stopped:
            self.handle_request()
    
    def force_shutdown(self):
        self.server_close()
        self.stopped = True
        self._dummy_request()
    
    def _dummy_request(self):
        try:
            urlopen('http://%s:%d/' % self.server_address)
        except HTTPError, e:
            pass
        except URLError, e:
            if e.reason.args[1] != 'Connection refused':
                raise e

class ThreadedStopableHTTPServer(threading.Thread):
    def __init__(self, address, requests_responses):
        threading.Thread.__init__(self, **{'group': None})
        self.httpd = StopableHTTPServer(address, mock_http_handler(requests_responses))
    def run(self):
        self.httpd.serve_forever()
    def force_shutdown(self):
        self.httpd.force_shutdown()

def mock_http_handler(requests_responses):
    class MockHTTPHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                return self.do_mock_request()
            except AssertionError:
                self.server.force_shutdown()
                raise
        def do_mock_request(self):
            assert len(requests_responses) > 0, 'got unexpected request (%s)' % self.path
            req, resp = requests_responses.pop(0)
            if not query_eq(req['path'], self.path):
                print 'got request      ', self.path
                print 'excpected request', req['path']
                assert False, 'got unexpected request (see stdout)'
            self.start_response(resp)
            self.wfile.write(resp['body'])
            if not requests_responses:
                self.server.force_shutdown()
            return
        def start_response(self, resp):
            self.send_response(int(resp.get('status', '200')))
            if 'headers' in resp:
                for key, value in resp['headers'].iteritems():
                    self.send_header(key, value)
            self.end_headers()
        def log_request(self, code, size=None):
            pass
    return MockHTTPHandler

def query_eq(expected, actual):
    """
    >>> query_eq('bAR=baz&foo=bizz', 'foO=bizz&bar=baz')
    True
    >>> query_eq('/service?bar=baz&fOO=bizz', 'foo=bizz&bar=baz')
    False
    >>> query_eq('/1/2/3.png', '/1/2/3.png')
    True
    >>> query_eq('/1/2/3.png', '/1/2/0.png')
    False
    """
    return (query_to_dict(expected) == query_to_dict(actual) and
            path_from_query(expected) == path_from_query(actual))

def path_from_query(query):
    """
    >>> path_from_query('/service?foo=bar')
    '/service'
    >>> path_from_query('/1/2/3.png')
    '/1/2/3.png'
    >>> path_from_query('foo=bar')
    ''
    """
    if not ('&' in query or '=' in query):
        return query
    if '?' in query:
        return query.split('?', 1)[0]
    return ''

def query_to_dict(query):
    """
    >>> sorted(query_to_dict('/service?bar=baz&foo=bizz').items())
    [('bar', 'baz'), ('foo', 'bizz')]
    >>> sorted(query_to_dict('bar=baz&foo=bizz').items())
    [('bar', 'baz'), ('foo', 'bizz')]
    """
    if not ('&' in query or '=' in query):
        return {}
    d = {}
    if '?' in query:
        query = query.split('?', 1)[-1]
    for kv in query.split('&'):
        key, value = kv.split('=')
        d[key.lower()] = value
    return d

@contextmanager
def mock_httpd(address, requests_responses):
    t = ThreadedStopableHTTPServer(address, requests_responses)
    t.start()
    try:
        yield
    finally:
        t.force_shutdown()
    
if __name__ == '__main__':
    requests_responses = [('/foo', 'bar'), ('/baz', 'boo')]
    httpd = StopableHTTPServer(('', 8080), mock_http_handler(requests_responses))
    httpd.serve_forever()