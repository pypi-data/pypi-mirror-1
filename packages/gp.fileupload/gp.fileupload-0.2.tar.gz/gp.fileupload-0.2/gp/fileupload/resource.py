# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
import glob
from gp.fileupload.config import *

class IteratorWrapper(object):
    """wrap a wsgi output to inject resources tags at the right place
    """

    def __init__(self, original, js, css):
        if isinstance(original, list) or isinstance(original, tuple):
            self.original = iter(original)
        elif isinstance(original, basestring):
            self.original = iter([original])
        else:
            try:
                self.original = iter(original)
            except TypeError:
                raise TypeError('%r is not iterable' % original)
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

    def __init__(self, application, include_files=[], static_dir=None):

        self.application = application

        if not static_dir:
            static_dir = STATIC_DIR

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


