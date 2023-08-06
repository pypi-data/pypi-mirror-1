# -*- coding: utf-8 -*-
from gp.fileupload.middleware import FileUpload
from gp.fileupload.middleware import ResourceInjection
from StringIO import StringIO

try:
    from wsgiref.validate import validator
except ImportError:
    def validator(app): return app

def get_output(output):
    return '\n'.join([v for v in output])

def fake_start_response(*args, **kwargs):
    pass

def fake_environ():
    return {'REQUEST_METHOD':       'GET',
            'SERVER_NAME':          'localhost',
            'SERVER_PORT':          '8080',
            'PATH_INFO':            '/',
            'SCRIPT_NAME':          '',
            'QUERY_STRING':         '',
            'wsgi.version':         ('1.0',),
            'wsgi.url_scheme':      'http',
            'wsgi.errors':          StringIO(),
            'wsgi.input':           StringIO(),
            'wsgi.multithread':     False,
            'wsgi.multiprocess':    False,
            'wsgi.run_once':        False,
           }

def application(environ, start_response):
    data = [l for l in environ['wsgi.input']]
    if len(data) > 0:
        start_response('200 OK', [('Content-Type', 'text/plain;charset=utf-8')])
        return data
    else:
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        return ['<html><head></head><body>Test Page</body></html>']

def test_injection():
    app = validator(ResourceInjection(application,
                                      ['fileupload.css',
                                        'jquery.fileupload.js']))
    output = get_output(app(fake_environ(), fake_start_response))
    assert '/gp.fileupload.static/jquery.fileupload.js' in output, output
    assert '/gp.fileupload.static/fileupload.css' in output, output

def test_static_content():
    app = validator(FileUpload(application))
    environ = fake_environ()
    environ.update({'PATH_INFO':'/gp.fileupload.static/fileupload.css'})
    output = get_output(app(environ, fake_start_response))
    assert output.startswith('.fuProgress'), output

def test_stat():
    app = validator(FileUpload(application))
    environ = fake_environ()
    environ['PATH_INFO'] = '/gp.fileupload.stat/1'
    output = get_output(app(environ, fake_start_response))
    assert output == "{'state': 0, 'percent': 0}", output

def test_upload():
    app = validator(FileUpload(application))

    filename = __file__.replace('.pyc', '.py')
    data = open(filename).read()
    length = str(len(data))

    # upload a file
    environ = fake_environ()
    environ.update({'PATH_INFO':'/', 'QUERY_STRING':'gp.fileupload.id=1',
                    'CONTENT_LENGTH':length, 'wsgi.input': StringIO(data)})
    output = get_output(app(environ, fake_start_response))
    assert 'from gp.fileupload.middleware' in output, output

    # get stats
    environ = fake_environ()
    environ.update({'PATH_INFO':'/gp.fileupload.stat/1'})
    output = get_output(app(environ, fake_start_response))
    assert output == "{'state': 1, 'percent': 100}", output

