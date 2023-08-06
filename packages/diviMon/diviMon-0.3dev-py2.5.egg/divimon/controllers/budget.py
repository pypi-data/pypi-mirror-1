import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class BudgetController(ListController):
    table = model.Budget
    #parent = dict(
            #dr = dict(
                    #table = model.Transaction,
                    #column = ('id'),
                #),
            #status = dict(
                    #table = model.Cheque_status,
                    #column = ('name'),
                #),
        #)
    children = dict(
            budget_expense = dict(
                    table = model.BudgetExpense,
                    columns = ('expense', ),
                    parent = dict(
                            expense = dict(
                                    table = model.Expense,
                                    column = 'id',
                                ),
                        ),
                ),
        )
    def _list(self):
        c.entries = self.query

    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())

    def report(self):
        self._dbg('list', request.params)
        self._list_params()
        self._list_query()
        self._list()
        return render('/report_list.mako')

    def _details(self, id):
        c.id = id
        c.entry = model.Session.query(c.table).get(id)

    def details(self, id):
        self._dbg('details', request.params)
        self._details(request.params['id'])
        return self.render_details()

    def render_details(self):
        return render('/details.mako')

    #model.Session.query(model.Inventory).filter_by(item=arg['item'])
