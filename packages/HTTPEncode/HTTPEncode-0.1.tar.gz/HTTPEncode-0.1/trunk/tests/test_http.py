import threading
import os
from paste import httpserver
from httpencode import *
from httpencode.json import json
from paste.fixture import TestApp
from test_remote_http import json_reader
import atexit

http = HTTP()

def make_remote_reader(url, data):
    def app(environ, start_response):
        res = http.POST(url, data, input='name json', wsgi_request=environ)
        start_response('200 OK', [('content-type', 'text/plain')])
        return [repr(res)]
    return app

def test_real_http():
    atexit.register(force_exit)
    server = httpserver.serve(
        json_reader, host='localhost', port='10199', start_loop=False)
    t = threading.Thread(target=server.handle_request)
    # Should accept one request and then die
    t.start()
    try:
        wsgi_app = make_remote_reader('http://localhost:10199', data={'stuff': [1, 'f', 0.5]})
        app = TestApp(wsgi_app)
        res = app.get('/?force')
        assert res.body == '"[1, u\'f\', 0.5]"'
    finally:
        # In case something went wrong, try to unfreeze the subthread:
        server.server_close()
        try:
            print 'Trying to open/terminate subthread'
            urllib.urlopen('http://localhost:10199')
            print 'terminated?'
        except:
            pass

def force_exit():
    print 'forcing process to die'
    import os
    os._exit(0)

if not os.environ.get('HTTP') and 0:
    del test_real_http
