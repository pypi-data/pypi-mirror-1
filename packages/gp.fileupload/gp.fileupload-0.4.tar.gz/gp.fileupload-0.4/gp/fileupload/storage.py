# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
import re
import cgi
import sha
import stat
import shutil
import datetime
from cStringIO import StringIO
from paste.fileapp import FileApp
from gp.fileupload.config import *

__all__ = ['StorageApp']

def make_dir(root, session):
    l = len(session)/3
    path = os.path.join(root,
                        session[:l],
                        session[l:l*2],
                        session[l*2:])
    return path

ERROR = 'gp.fileupload.error'

class StorageApp(object):

    def __init__(self, application, upload_to, tempdir=None,
                 exclude_paths=None):
        self.application = application

        if not os.path.isdir(upload_to):
            os.makedirs(upload_to)
        self.upload_to = upload_to

        if not tempdir:
            tempdir = TEMP_DIR
        self.tempdir = tempdir

        if exclude_paths:
            self.exclude_paths = [re.compile(p) for p in exclude_paths]
        else:
            self.exclude_paths = None

    def __call__(self, environ, start_response):

        if self.exclude_paths and environ['REQUEST_METHOD'] in ('GET', 'HEAD'):

            path = environ['PATH_INFO']
            for p in self.exclude_paths:
                if p.search(path):
                    return self.application(environ, start_response)

            def fake_start_response(status, headers, *args, **kwargs):
                # don't serve if a 4XX or 5XX status is found
                if status[0] in ('4', '5'):
                    environ[ERROR] = True
                    start_response(status, headers, *args, **kwargs)
                else:
                    # determine if we have a non html file
                    for k, v in headers:
                        if k.lower() == 'content-type':
                            if not v.startswith('text/html'):
                                environ[HTTP_SERVE_PATH] = True
                            else:
                                start_response(status, headers, *args, **kwargs)
                            break

            iterable = self.application(environ, fake_start_response)

            if ERROR in environ:
                return iterable

            elif HTTP_SERVE_PATH in environ:
                    rpath = ''.join([i for i in iterable])
                    path = os.path.join(self.upload_to, rpath.strip())
                    log.info('Serving %s' % path)
                    return FileApp(path)(environ, start_response)
            else:
                return iterable

        elif environ.get('REQUEST_METHOD') == 'POST':
            return self.store(environ, start_response)

        return self.application(environ, start_response)

    def store(self, environ, start_response):
        """store file and change wsgi input
        """
        # Don't use the session to generate file path.
        # Use sha instead to get more directories
        session = sha.new(str(datetime.datetime.now())).hexdigest()

        # need to consume so see how many block we have to read
        bsize = 1024
        length = int(environ['CONTENT_LENGTH'])
        blocks = [bsize for i in range(bsize, length, bsize)]
        blocks.append(length-len(blocks)*bsize)

        # read input an write to a temporary file
        dpath = os.path.join(self.tempdir, session+'.dump')
        dfile = open(dpath, 'w')
        rfile = environ['wsgi.input']
        for size in blocks:
            dfile.write(rfile.read(size))
        dfile.close()

        # get form from file
        dfile = open(dpath)
        fields = cgi.FieldStorage(fp=dfile,
                                  environ=environ,
                                  keep_blank_values=1)

        # get directory
        session = session[0:6]
        relative = make_dir('', session)
        dirname = make_dir(self.upload_to, session)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        # store files on fs
        files = []
        for key in fields.keys():
            field = fields[key]
            fd = getattr(field, 'file', None)
            filename = getattr(field, 'filename', None)
            if fd is not None and filename:
                path = os.path.join(dirname, filename)
                tempfile = open(path, 'w')
                shutil.copyfileobj(fd, tempfile)
                tempfile.close()
                rpath = os.path.join(relative, filename)
                files.append((filename, rpath, path))

        # prepare new input by replacing files contents
        rfile = StringIO()
        dfile.seek(0)
        jump = 0
        while dfile.tell() < length:
            line = dfile.readline()
            if line.startswith('Content-Disposition:'):
                for filename, rpath, path in files:
                    if filename in line:
                        jump = os.stat(path)[stat.ST_SIZE]
                        break
            elif not line.strip() and jump:
                dfile.seek(dfile.tell() + jump)
                jump = 0
                rfile.write(line)
                rfile.write('%s\r\n' % rpath)
                continue
            rfile.write(line)

        # update content-length from new input
        environ['CONTENT_LENGTH'] = rfile.tell()

        # replace input
        rfile.seek(0)
        input = environ['wsgi.input']
        environ['wsgi.input'] = rfile

        # add files path to environ
        paths = ':'.join([r for f, r, p in files])
        log.debug('Stored: %s', paths)
        environ[HTTP_STORED_PATHS] = paths

        # get application result
        def fake_start_response(status, headers, *args, **kwargs):
            # delete file if a 4XX and 5XX status is found
            if status[0] in ('4', '5'):
                environ[ERROR] = True
            start_response(status, headers, *args, **kwargs)
        iterable = self.application(environ, fake_start_response)

        # if no status set, the operation failed. (unauthorised, error, etc.)
        # delete the file
        if ERROR in environ:
            for f,n,p in files:
                os.remove(p)

        # restore input
        environ['wsgi.input'] = input

        # remove temp file
        os.remove(dpath)

        return iterable

