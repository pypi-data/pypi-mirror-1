import logging

from divimon.lib.base import *
from divimon import model

#from budget_expense import BudgetExpenseController

log = logging.getLogger(__name__)

class ExpenseController(ListController):
    table = model.Expense
    parent = dict(
            area = dict(
                    table = model.Area,
                    column = 'name',
                ),
        )
    children = dict(
            expense_breakdown = dict(
                    table = model.ExpenseBreakdown,
                    columns = ('fuel', 'miscellaneous', 'toll_fee', 'meal', ),
                    parent = dict(
                            expense = dict(
                                    table = model.Expense,
                                    column = 'id',
                                ),
                        ),
                ),
        )


    def report(self):
        self._dbg('list', request.params)
        self._list_params()
        self._list_query()
        self._list()
        return render('/expense/report_list.mako')

    def render_list(self):
        return render('/expense/list.mako')

    def _save_for_budget(self, id, params):
        for a in model.list(model.Budget).order_by(model.Budget.c.id.desc()):
            last_budget = a
            #break

        print id #recently saved Expense

        entry_args = dict(
                budget = last_budget.id,
                expense = id,
            )

        for a in model.list(model.BudgetExpense):
            if int(id) == int(a.expense):
                return params
        c.id = None
        c.entry = entry_args

        id = None
        self.table = model.BudgetExpense
        entry = self._save_entry(id, entry_args)
        self._dbg('_save', '%s Successfully saved' % entry)
        model.Session.save_or_update(entry)
        model.Session.commit()

    def _save_entry(self, id, entry_args):
        # Saving of entry
        if id is not None:
            entry = model.get(self.table, id)
            for k,v in entry_args.iteritems():
                setattr(entry, k, v)
        else:
            entry = self.table(**entry_args)
        return entry

    def invalid(self):
        return 'Invalid!'


    def save(self):
        self._dbg('save')
        try:
            id = request.params['id']
        except KeyError:
            id = None
        entry = self._save(id, request.params)
        self._save_for_budget(entry.id, request.params)
        self._dbg('save', entry.id)

        redirect_to('list')#
        return 'Saved'

