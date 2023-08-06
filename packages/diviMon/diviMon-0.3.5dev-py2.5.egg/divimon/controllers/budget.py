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
        return render('/budget/report_list.mako')

    def cashflow(self):
        self._dbg('list', request.params)
        self._list_params()
        self._list_query()
        self._list()
        return render('/budget/cash_flow.mako')

    def cashflow_daily(self):
        from datetime import datetime,timedelta
        now = datetime.now()
        redirect_to('/budget/populate?start_day=%s&start_month=%s&end_day=%s&end_month=%s&year=%s' % (now.day,now.month,now.day,now.month,now.year))

    def cashflow_particular_date_range(self):
        if not 'start_day' in request.params:
            return render('/particular_date_range.mako')
        else: 
            self._dbg('list', request.params)
            self._list_params()
            self._list_query()
            self._list()
            return render('/budget/cash_flow_daily.mako')

    def cashflow_print(self):
        self._dbg('list', request.params)
        self._list_params()
        self._list_query()
        self._list()
        return render('/budget/cash_flow_print.mako')

    def income_statement(self):
        self._dbg('list', request.params)
        self._list_params()
        self._list_query()
        self._list()
        return render('/budget/cash_flow.mako')

    def _details(self, id):
        c.id = id
        c.entry = model.Session.query(c.table).get(id)

    def details(self, id):
        self._dbg('details', request.params)
        self._details(request.params['id'])
        return self.render_details()

    def render_details(self):
        return render('/details.mako')

    def render_list(self):
        return render('/budget/list.mako')

    def populate(self):
        if 'start_day' in request.params:
            c.start_day = request.params['start_day']
            c.end_day = request.params['end_day']
            c.start_month = request.params['start_month']
            c.end_month = request.params['end_month']
            c.year = request.params['year']
            return render('/budget/cash_flow_daily.mako')
        else:
            return render('/budget/cash_flow_daily.mako')

    def previous(self):
        from datetime import datetime,timedelta
        now = datetime.now()
        print "!!!!!!"
        print request.params
        print 'previous'
        
        redirect_to(str('/budget/populate?start_day=%s&start_month=%s&end_day=%s&end_month=%s&year=%s' % (int(request.params['start_day'])-1,request.params['start_month'],int(request.params['end_day'])-1,request.params['end_month'],request.params['start_year'])))
