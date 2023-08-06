# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
import cgi
import glob
import stat
import logging
import tempfile

__all__ = ['FileUpload', 'ResourceInjection']

log = logging.getLogger('fileupload')

BLOCK_SIZE = 1024*128
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'fileUpload')

BASE_PATH = '/gp.fileupload.'
SESSION_NAME = 'gp.fileupload.id'
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
VALID_FILES = [f for f in os.listdir(STATIC_DIR) if not f.startswith('.')]

CSS_TEMPLATE = \
'<style type="text/css"><!-- @import url(/gp.fileupload.static/%s); --></style>'

JS_TEMPLATE = \
'<script type="text/javascript" src="/gp.fileupload.static/%s"></script>'

class InputWrapper(object):

    def __init__(self, rfile, sfile):
        self._InputWrapper_rfile = rfile
        self._InputWrapper_sfile = sfile
        self._InputWrapper_size = 0
        for k in ('flush', 'write', 'writelines', 'close'):
            if hasattr(rfile, k):
                setattr(self, k, getattr(rfile, k))

    def _flush(self, chunk):
        self._InputWrapper_size += len(chunk)
        log.info('%s', self._InputWrapper_size)
        self._InputWrapper_sfile.seek(0)
        self._InputWrapper_sfile.write(str(self._InputWrapper_size))
        self._InputWrapper_sfile.flush()
        return chunk

    def __iter__(self):
        riter = iter(self._InputWrapper_rfile)
        def wrapper():
            for chunk in riter:
                yield self._flush(chunk)
        return iter(wrapper())

    def read(self, size=-1):
        chunk = self._InputWrapper_rfile.read(size)
        return self._flush(chunk)

    def readline(self):
        chunk = self._InputWrapper_rfile.readline()
        return self._flush(chunk)

    def readlines(self, hint=None):
        chunk = self._InputWrapper_rfile.readlines(hint)
        return self._flush(chunk)

class FileUpload(object):

    def __init__(self, application, tempdir=TEMP_DIR, max_size=None):
        self.application = application
        self.tempdir = tempdir
        if not os.path.isdir(tempdir):
            os.makedirs(tempdir)
        log.info('Temporary directory: %s' % tempdir)

        self.max_size = max_size
        if max_size:
            log.info('Max upload size: %s' % max_size)

    def __call__(self, environ, start_response):
        path_info = environ['PATH_INFO']

        if BASE_PATH in path_info:
            if BASE_PATH+'stat/' in path_info:
                # get stats
                return self.status(environ, start_response)
            elif BASE_PATH+'static/' in path_info:
                # static file
                filename = path_info.split('/')[-1]
                if filename in VALID_FILES:
                    fd = open(os.path.join(STATIC_DIR, filename))
                    data = fd.read()
                    fd.close()
                    ctype = filename.endswith(
                                '.css') and 'text/css' or 'text/javascript'
                    start_response('200 OK', [('Content-Type', ctype)])
                    return [data]

        if SESSION_NAME in environ.get('QUERY_STRING', ''):
            return self.upload(environ, start_response)
        return self.application(environ, start_response)

    def tempfiles(self, session, environ):
        filename = environ.get('REMOTE_USER','') + session
        return (os.path.join(self.tempdir, session),
               os.path.join(self.tempdir, session+'.stats'))

    def upload(self, environ, start_response):
        qs = cgi.parse_qs(environ.get('QUERY_STRING', ''))
        session = qs[SESSION_NAME][0]

        if not session.isdigit():
            log.error('Malformed session id "%s"', session)
            raise RuntimeError('Malformed session id:%s' % session)

        log.debug('Start session "%s"', session)

        tempfile, statfile = self.tempfiles(session, environ)

        length = environ['CONTENT_LENGTH']
        if self.max_size and int(length) > self.max_size:
            log.error('File too big in session "%s"', session)
            sfile = open(statfile, 'w')
            sfile.write('-1')
            sfile.close()
            raise RuntimeError('File is to big')

        sfile = open(statfile, 'w')
        sfile.write(length)
        sfile.close()

        sfile = open(tempfile, 'w')
        environ['wsgi.input'] = InputWrapper(
                                    environ['wsgi.input'],
                                    sfile)
        iterator = self.application(environ, start_response)
        sfile.close()

        # remove temp file
        os.remove(tempfile)

        return iterator

    def status(self, environ, start_response):
        session = environ['PATH_INFO'].split('/')[-1]

        if not session.isdigit():
            log.error('Malformed session id "%s"', session)
            raise RuntimeError('Malformed session id:%s' % session)

        tempfile, statfile = self.tempfiles(session, environ)
        if os.path.isfile(tempfile):
            sfile = open(statfile, 'r')
            length = int(sfile.read())
            sfile.close()

            if length == -1:
                # file is too big
                data = dict(state=0, percent=-1)
                os.remove(statfile)
            else:
                # return progress
                #size = os.stat(tempfile)[stat.ST_SIZE]
                size = int(open(tempfile).read())

                data = dict(state=1,
                            percent=int(float(size)/length*100))
        elif os.path.isfile(statfile):
            # upload finished
            data = dict(state=1, percent=100)
            os.remove(statfile)
        else:
            # bad state
            data = dict(state=0,
                        percent=0)

        start_response('200 OK', [('Content-Type', 'text/javascript')])
        log.debug('%s: %s', session, data)
        return [repr(data)]

class IteratorWrapper(object):
    """wrap a wsgi output to inject resources tags at the right place
    """

    def __init__(self, original, js, css):
        if isinstance(original, list):
            self.original = (i for i in original)
        else:
            self.original = original
        self.js = js
        self.css = css

    def __iter__(self):
        return self

    def next(self):
        value = self.original.next()
        if '<head>' in value:
            value = value.replace('<head>', '<head>'+self.css)
        if '</body>' in value:
            value = value.replace('</body>', self.js+'</body>')
        return value

class ResourceInjection(object):
    """This middleware inject some javascript and css to an html page
    """

    def __init__(self, application, include_files=[], static_dir=STATIC_DIR):

        self.application = application

        # existing files
        files = [f for f in os.listdir(static_dir) if not f.startswith('.')]

        valid_files = []
        # analyze patterns and filter valid files
        for pattern in include_files:
            if '*' in pattern:
                filenames = sorted(glob.glob(
                                        os.path.join(static_dir, pattern)),
                                   reverse=True)
                filenames = [os.path.split(f)[1] for f in filenames]
            else:
                filenames = pattern in files and [pattern] or []
            valid_files.extend(filenames)

        # generate tags
        self.js = self.css = ''
        for f in valid_files:
            if f.endswith('.css'):
                self.css += CSS_TEMPLATE % f
            elif f.endswith('.js'):
                self.js += JS_TEMPLATE % f
        log.info('%s will be injected in html', ', '.join(valid_files))

    def __call__(self, environ, start_response):
        # fake start_response to see if we have a html output
        def fu_start_response(status, headers, *args, **kwargs):
            for k, v in headers:
                if k.lower() == 'content-type' and v.startswith('text/html'):
                    environ['gp.fileupload.html'] = True
                    break
            return start_response(status, headers, *args, **kwargs)

        iterable = self.application(environ, fu_start_response)

        if environ.get('gp.fileupload.html'):
            # wrap the output in an iterator for clean injection
            return IteratorWrapper(iterable, self.js, self.css)

        return iterable

def make_app(application, global_conf, tempdir=TEMP_DIR, max_size=None,
             include_files='fileupload.css jquery.fileupload.*'):

    if max_size:
        # use Mo
        max_size = int(max_size)*1024*1024

    if include_files:
        if isinstance(include_files, basestring):
            include_files = [f for f in include_files.split(' ') if f]
        application = ResourceInjection(application, include_files)

    return FileUpload(application, tempdir=tempdir, max_size=max_size)

