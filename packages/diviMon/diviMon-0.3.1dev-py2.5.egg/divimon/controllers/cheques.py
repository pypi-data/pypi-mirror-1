import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class ChequesController(ListController):
    table = model.Cheque
    parent = dict(
            dr = dict(
                    table = model.Transaction,
                    column = ('id'),
                ),
            status = dict(
                    table = model.Cheque_status,
                    column = ('name'),
                ),
        )

    def report(self):
        return render('/budget/cheques.mako')

    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())
        #self.query = self.query.filter_by(type=2)
        try:
            area = request.params['area']
        except KeyError:
            return
        if area is not None and area != '':
            self.query = self.query.filter_by(area=area)