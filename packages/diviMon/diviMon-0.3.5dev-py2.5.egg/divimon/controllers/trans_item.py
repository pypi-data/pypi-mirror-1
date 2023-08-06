import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class TransItemController(ListController):
    table = model.TransItem
    parent = dict(
            transaction = dict(
                    table = model.Transaction,
                    column = 'id',
                ),
            item = dict(
                    table = model.Item,
                    column = 'name',
                )
        )
