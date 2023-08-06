import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class ExpenseController(ListController):
    table = model.Expense
    parent = dict(
            #area = dict(
                    #table = model.Area,
                    #column = 'name',
                #),
            type = dict(
                    table = model.ExpenseType,
                    column = 'name',
                ),
            #agent = dict(
                    #table = model.Agent,
                    #column = 'name',
                #),
            #customer = dict(
                    #table = model.Customer,
                    #column = 'name',
                #),

            #pay_type = dict(
                    #table = model.PayType,
                    #column = 'name',
                #),
        )
    children = dict(
            trans_expense = dict(
                    table = model.TransExpense,
                    columns = ('transaction', ),
                    parent = dict(
                            transaction = dict(
                                    table = model.Transaction,
                                    column = 'id',
                                ),
                            #expense = dict(
                                    #table = model.Expense,
                                    #column = 'id',
                                #),
                        ),
                ),
        )
    #prices = dict(
        #)
    #total = 0


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


