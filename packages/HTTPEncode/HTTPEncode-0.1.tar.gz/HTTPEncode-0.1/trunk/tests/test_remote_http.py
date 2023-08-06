import urllib

from paste.urlmap import URLMap
from paste.wsgilib import intercept_output
from paste.recursive import RecursiveMiddleware
from paste.fixture import TestApp

from httpencode import *
from httpencode.http import HTTP

http = HTTP()

json = get_format('json')

def json_app(environ, start_response):
    app = Responder({'test': 1}, 'python', default_format='json')
    return app(environ, start_response)

def json_reader(environ, start_response):
    assert environ.get('CONTENT_TYPE')
    environ['CONTENT_TYPE'] = 'application/json'
    data = parse_request(environ, output_type='python')
    part = data['stuff']
    return simple_res(repr(part), start_response)

def simple_res(content, start_response):
    start_response('200 OK', [('content-type', 'text/plain')])
    return [str(content)]

def make_requester(format, responder, data=None):
    map = URLMap()
    def requester(environ, start_response):
        if data is None:
            res = http.GET('/rpc', wsgi_request=environ,
                           output='python')
        else:
            res = http.POST('/rpc', data, wsgi_request=environ,
                            input='name json',
                            output='name json')
        return simple_res(repr(res), start_response)
    map[''] = requester
    map['/rpc'] = responder
    app = RecursiveMiddleware(map)
    return app

def cap_middleware(app):
    def middleware(environ, start_response):
        status, headers, body = intercept_output(
            environ, app)
        start_response(status, headers)
        return [body.upper()]
    return middleware

def test_simple_request():
    """
    These test getting an unserialized response
    """
    app = TestApp(make_requester(json, json_app))
    res = app.get('/rpc')
    # Plain request:
    assert res.body == '{"test": 1}'
    res = app.get('/')
    assert res.body == "{'test': 1}"
    res = app.get('/')
    assert res.body == "{'test': 1}"

    app = TestApp(make_requester(json, cap_middleware(json_app)))
    # It's actually a good sign we get two values depending on how we
    # get to the application, just like we get different quoting above
    # (though the distinction is subtle; does json or Python prefer '
    # to "?)
    res = app.get('/rpc')
    assert res.body == '{"TEST": 1}'
    res = app.get('/')
    # We get a urlencoded parsing:
    assert res.body == "{'TEST': '1'}"

def test_sending_request():
    """
    These test sending an unserialized request
    """
    app = TestApp(make_requester(json, json_reader,
                                 data={'stuff': [1, 2, 3]}))
    res = app.post('/rpc', params='{"stuff": "foo"}',
                   extra_environ={'CONTENT_TYPE': 'application/x-www-form-urlencoded'})
    assert res.body == "u'foo'"
    res = app.get('/?force')
    assert res.body == '[1, 2, 3]'

