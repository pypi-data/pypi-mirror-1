import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class TransactionController(ListController):
    table = model.Transaction
    parent = dict(
            area = dict(
                    table = model.Area,
                    column = 'name',
                ),
            type = dict(
                    table = model.TransType,
                    column = 'name',
                ),
            agent = dict(
                    table = model.Agent,
                    column = 'name',
                ),
            customer = dict(
                    table = model.Customer,
                    column = 'name',
                ),

            pay_type = dict(
                    table = model.PayType,
                    column = 'name',
                ),
            pay_status = dict(
                    table = model.PayStatus,
                    column = 'name',
                ),
        )
    children = dict(
            trans_item = dict(
                    table = model.TransItem,
                    columns = ('item', 'qty', 'price', 'received_qty', ),
                    parent = dict(
                            item = dict(
                                    table = model.Item,
                                    column = 'name',
                                ),
                        ),
                ),
        )
    prices = dict(
        )
    total = 0
    column_hidden = set([
        'pay_status',
    ])


    def show_price(self):
        item_id = request.params['item']
        try:
            qty = float(request.params['qty'])
        except ValueError:
            qty = 0
        item = model.get(model.Item, item_id)
        try:
            item_price = item.price
        except AttributeError:
            item_price = 0
        c.cnt = request.params['cnt']
        c.child = 'trans_item'
        c.child_details = self.children[c.child]
        c.table = c.child_details['table']
        c.columns = c.child_details['columns']
        c.price = qty * item_price
        self.prices[c.cnt] = c.price
        return render('/transaction/show_price.mako')


