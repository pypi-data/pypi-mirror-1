import os
import cgi
import time
import middleware
from paste.deploy import CONFIG
from paste.deploy.config import ConfigMiddleware

def application(environ, start_response):
    if 'gp.fileupload.id' in environ['QUERY_STRING']:
        # process post here
        block_size = 1024*1024
        length = int(environ['CONTENT_LENGTH'])
        blocks = [block_size for i in range(block_size, length, block_size)]
        blocks.append(length-len(blocks)*block_size)

        # read input and write to temp file
        consumed = 0
        rfile = environ['wsgi.input']
        for size in blocks:
            chunk = rfile.read(size)
            time.sleep(.001)
        start_response('200 OK', [('Content-type', 'text/html')])
        return ['<html><body>Yeah !</body></html>']

    start_response('200 OK', [('Content-type', 'text/html')])
    content = [
        '<html><head><title>File upload</title>\n',
        '<script type="text/javascript" src="/gp.fileupload.static/jquery.js"></script>\n',
        '<script type="text/javascript">\n',
        '   jQuery(document).ready(function() {\n',
        '       jQuery(\'#sample\').fileUpload();\n',
        '   });\n',
        '</script>\n',
        '</head>\n',
        '<body>\n',
        '\n',
        '<h1>File upload demo</h1>\n',
        '\n',
        '<h3>js sample</h3>\n',
        '<div id="sample">\n',
        '</div>\n',
        '\n',
        '<h3>html sample</h3>\n',
        '<form action="/upload" enctype="multipart/form-data">\n',
        '<input type="file" name="my_file" /><br />\n',
        '<input type="file" name="my_file2" /><br />\n',
        '<input type="submit" />\n',
        '</form>\n',
        '\n',
        '</body></html>',
        ]
    return content

def make_app(
    global_conf,
    **kw):
    app = application
    conf = global_conf.copy()
    conf.update(kw)
    app = ConfigMiddleware(app, conf)
    return app

