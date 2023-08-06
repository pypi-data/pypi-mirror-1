import logging

from divimon.lib.base import *

log = logging.getLogger(__name__)

class IndexController(BaseController):

    def index(self):
        return render('/blank.mako')
