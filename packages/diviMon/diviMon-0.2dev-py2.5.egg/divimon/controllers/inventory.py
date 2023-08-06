import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class InventoryController(ListController):
    table = model.Inventory
    parent = dict(
            #area = dict(
                    #table = model.Area,
                    #column = ('name'),
                #),
            item = dict(
                    table = model.Item,
                    column = ('code'),
                )
        )