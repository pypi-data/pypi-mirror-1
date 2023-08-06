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
    #parent = dict(
            #branch = dict(
                    #table = model.Branch,
                    #column = 'name',
                #),
            #type = dict(
                    #table = model.TransType,
                    #column = 'name',
                #),
        #)
    #children = dict(
            #trans_item = dict(
                    #table = model.TransItem,
                    #columns = ('item', 'qty', 'price'),
                    #parent = dict(
                            #item = dict(
                                    #table = model.Item,
                                    #column = 'name',
                                #),
                        #),
                #),
        #)

