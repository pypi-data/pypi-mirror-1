import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class AreaController(ListController):
    table = model.Area
