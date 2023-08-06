# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
import cgi
import tempfile
from gp.fileupload.config import *
from gp.fileupload.resource import *

__all__ = ['FileUpload', 'make_app']


TEMP_DIR = os.path.join(tempfile.gettempdir(), 'fileUpload')

class InputWrapper(object):

    def __init__(self, rfile, sfile):
        log.debug('InputWrapper init: %s, %s', rfile, sfile)
        self._InputWrapper_rfile = rfile
        self._InputWrapper_sfile = sfile
        self._InputWrapper_size = 0
        for k in ('flush', 'write', 'writelines', 'close'):
            if hasattr(rfile, k):
                setattr(self, k, getattr(rfile, k))

    def _flush(self, chunk):
        length = len(chunk)
        if length > 0:
            self._InputWrapper_size += length
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
        if not tempdir:
            self.tempdir = TEMP_DIR
        else:
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
                    length = str(len(data))
                    start_response('200 OK',
                                   [('Content-Type', ctype),
                                    ('Content-Length', length)])
                    return [data]

        elif SESSION_NAME in environ.get('QUERY_STRING', ''):
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

        tempfile, statfile = self.tempfiles(session, environ)

        length = environ['CONTENT_LENGTH']
        if self.max_size and int(length) > self.max_size:
            log.error('File too big in session "%s"', session)
            sfile = open(statfile, 'w')
            sfile.write('-1')
            sfile.close()
            raise RuntimeError('File is to big')

        log.debug('Start session "%s", length: %s', session, length)


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
                try:
                    size = int(open(tempfile).read())
                except ValueError:
                    # file is not write yet
                    data = dict(state=0, percent=0)
                else:
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

def make_app(application, global_conf, tempdir=None, max_size=None,
             include_files=None):

    if not tempdir:
        tempdir = TEMP_DIR

    if max_size:
        # use Mo
        max_size = int(max_size)*1024*1024

    if include_files:
        if isinstance(include_files, basestring):
            include_files = [f for f in include_files.split(' ') if f]
        application = ResourceInjection(application, include_files)

    return FileUpload(application, tempdir=tempdir, max_size=max_size)

