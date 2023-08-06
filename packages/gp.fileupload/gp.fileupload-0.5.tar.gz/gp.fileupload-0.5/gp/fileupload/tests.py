# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import cgi
import glob
import shutil
import doctest
from StringIO import StringIO
import gp.fileupload
from gp.fileupload.config import *
from gp.fileupload.upload import FileUpload
from gp.fileupload.storage import Storage
from gp.fileupload.resource import ResourceInjection

try:
    from wsgiref.validate import validator
except ImportError:
    def validator(app): return app

def get_output(output, sep='\n'):
    return sep.join([v for v in output])

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
    if environ['PATH_INFO'] == '/test.txt':
        start_response('200 OK', [('Content-Type', 'text/plain;charset=utf-8')])
        return [environ['test_path']]

    data = [l for l in environ['wsgi.input']]
    if len(data) > 0:
        start_response('200 OK', [('Content-Type', 'text/plain;charset=utf-8')])
        return data

    else:
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        return ['<html><head></head><body>Test Page</body></html>']

BOUNDARY='--testdata'
ASSERT_DATA = '--%s' % BOUNDARY
TEST_DATA = '''--%s
Content-Disposition: form-data; name="my_file"; filename="test.js"
Content-Type: application/x-javascript

var test = null;

--%s
Content-Disposition: form-data; name="my_file2"; filename="text.txt"
Content-Type: text/plain

some text a little bit longer than the minimum

--%s--
''' % (BOUNDARY, BOUNDARY, BOUNDARY)
TEST_LENGTH = str(len(TEST_DATA))

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
    shutil.rmtree(TEMP_DIR)

    app = validator(FileUpload(application))

    # upload a file
    environ = fake_environ()
    environ.update({'PATH_INFO':'/', 'QUERY_STRING':'gp.fileupload.id=1',
                    'CONTENT_LENGTH':TEST_LENGTH,
                    'wsgi.input': StringIO(TEST_DATA)})
    output = get_output(app(environ, fake_start_response))
    assert ASSERT_DATA in output, output

    # get stats
    environ = fake_environ()
    environ.update({'PATH_INFO':'/gp.fileupload.stat/1'})
    output = get_output(app(environ, fake_start_response))
    # FIXME
    #assert output == "{'state': 1, 'percent': 100}", output

    # check temp files
    tempfiles = glob.glob(os.path.join(TEMP_DIR, '*'))
    assert len(tempfiles) == 0, tempfiles

def test_storage():
    shutil.rmtree(TEMP_DIR)

    app = validator(Storage(application, TEMP_DIR, exclude_paths=['/@@']))

    # upload a file
    environ = fake_environ()
    environ.update({'PATH_INFO':'/', 'REQUEST_METHOD':'POST',
                    'CONTENT_TYPE': 'multipart/form-data;boundary="%s"' % BOUNDARY,
                    'CONTENT_LENGTH':TEST_LENGTH,
                    'wsgi.input': StringIO(TEST_DATA)})
    output = get_output(app(environ, fake_start_response), sep='')
    assert ASSERT_DATA in output, output

    # data is reduce
    assert len(output) < int(TEST_LENGTH), 'Bad length: %s' % output

    # content length has change
    assert len(output) == int(environ['CONTENT_LENGTH']), 'Bad length'

    # get fields from output
    fields = cgi.FieldStorage(fp=StringIO(output),
                              environ=environ,
                              keep_blank_values=1)
    # retrieve valid file path
    field = fields['my_file']
    path = os.path.join(TEMP_DIR, field.file.read().strip())
    assert os.path.isfile(path) is True, path

    # check file content
    data = open(path).read()
    assert data.strip() == 'var test = null;', data

    # now check get
    environ = fake_environ()
    environ.update({'PATH_INFO':'/test.txt', 'REQUEST_METHOD':'GET',
                    'test_path':path})
    output = get_output(app(environ, fake_start_response), sep='')

    # check correct output
    assert output.strip() == 'var test = null;', output

    # check temp files
    tempfiles = glob.glob(os.path.join(TEMP_DIR, '*.dump'))
    assert len(tempfiles) == 0, tempfiles

    # rm TEMP_DIR
    shutil.rmtree(TEMP_DIR)

###############
## Doc tests ##
###############

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)

dirname = os.path.join(os.path.dirname(gp.fileupload.__file__), '..', '..', 'docs')


def build_testcase(filename):
    name = os.path.splitext(filename)[0]
    name = name.replace('-', '_')
    path = os.path.join(dirname, filename)

    class Dummy(doctest.DocFileCase):
        def __init__(self, *args, **kwargs):
            # get tests from file
            parser = doctest.DocTestParser()
            doc = open(self.path).read()
            test = parser.get_doctest(doc, globals(), name, self.path, 0)

            # init doc test case
            doctest.DocFileCase.__init__(self, test, optionflags=optionflags)

        def setUp(self):
            """init globals
            """
            test = self._dt_test

        def tearDown(self):
            """cleaning
            """
            test = self._dt_test
            test.globs.clear()

    # generate a new class for the file
    return ("Test%s" % name.title(),
            type('Test%sClass' % name.title(), (Dummy,), dict(path=path)))

for filename in os.listdir(dirname):
    if filename.endswith('.txt'):
        name, klass = build_testcase(filename)
        exec "%s =  klass" % name

# clean namespace to avoid test duplication   
del build_testcase, filename, name, klass


