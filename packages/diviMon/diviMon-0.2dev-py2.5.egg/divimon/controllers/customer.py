import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class CustomerController(ListController):
    table = model.Customer
    parent = dict(
            area = dict(
                    table = model.Area,
                    column = 'name',
                ),
        )
    #children = dict(
            #trans_item = dict(
                    #table = model.TransItem,
                    #columns = ('item', 'qty', 'price'),
                    #parent = dict(
                            #item = dict(
                                    #table = model.Item,
                                    #column = 'code',
                                #),
                        #),
                #),
        #)
    #prices = dict(
        #)
    #total = 0

    #def render_add_child(self):
        #return render('/transaction/add_child.mako')

    #def render_edit(self):
        #return render('/transaction/edit.mako')

    #def show_price(self):
        #item_id = request.params['item']
        #try:
            #qty = float(request.params['qty'])
        #except ValueError:
            #qty = 0
        #item = model.get(model.Item, item_id)
        #try:
            #item_price = item.price
        #except AttributeError:
            #item_price = 0
        #c.cnt = request.params['cnt']
        #c.child = 'trans_item'
        #c.child_details = self.children[c.child]
        #c.table = c.child_details['table']
        #c.columns = c.child_details['columns']
        #c.price = qty * item_price
        #self.prices[c.cnt] = c.price
        #return render('/transaction/show_price.mako')

    #def show_total_price(self):
        #self.total = 0
        #for v in self.prices.values():
            #self.total += v
        #return '<input id="total_price" name="total_price" value="%0.2f" >' % self.total

    #def show_change(self):
        #try:
            #tendered = float(request.params['tendered'])
        #except ValueError:
            #tendered = 0
        #try:
            #total = float(request.params['price'])
        #except ValueError:
            #total = 0
        #change = tendered - total
        #return '<input id="change" name="change" value="%0.2f" >' % change

