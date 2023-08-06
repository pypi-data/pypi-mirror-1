# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
import logging

log = logging.getLogger('fileupload')

BASE_PATH = '/gp.fileupload.'
SESSION_NAME = 'gp.fileupload.id'
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
VALID_FILES = [f for f in os.listdir(STATIC_DIR) if not f.startswith('.')]

CSS_TEMPLATE = \
'<style type="text/css"><!-- @import url(/gp.fileupload.static/%s); --></style>'

JS_TEMPLATE = \
'<script type="text/javascript" src="/gp.fileupload.static/%s"></script>'

