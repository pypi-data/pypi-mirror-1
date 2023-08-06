import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class StocksOutController(ListController):
    table = model.StocksOut
    parent = dict(
            area = dict(
                    table = model.Area,
                    column = ('name'),
                ),
            item = dict(
                    table = model.Item,
                    column = ('code'),
                ),
            dr = dict(
                    table = model.Transaction,
                    column = ('id'),
                ),
        )