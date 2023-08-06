import logging

from divimon.lib.base import *
from transaction import TransactionController

log = logging.getLogger(__name__)

class DeliveryConfirmController(TransactionController):
    pass
    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())
        self.query = self.query.filter_by(type=3)

    def render_edit(self):
        return render('/delivery_confirm/edit.mako')

    def _save_custom(self, params):
        # insert branch here
        #if g.branch_id > 0:
            #params['branch'] = g.branch_id
        #params['type'] = 3
        entry = model.Session.query(model.StocksOut).filter_by(area=params['area']).filter_by(item=params['trans_item.item'])
        entry[0].qty -= int(params['trans_item.qty'])
        return params

