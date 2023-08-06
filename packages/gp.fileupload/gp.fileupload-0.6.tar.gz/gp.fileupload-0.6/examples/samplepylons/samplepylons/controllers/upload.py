# -*- coding: utf-8 -*-
import logging
from samplepylons.lib.base import *

log = logging.getLogger(__name__)

class UploadController(BaseController):

    def index(self):
        return render('/index.mak')


    def save(self):
        log.info('%s', request.POST)

