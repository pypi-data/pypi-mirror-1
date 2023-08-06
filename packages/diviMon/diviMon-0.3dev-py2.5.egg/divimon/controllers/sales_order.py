import logging

from divimon.lib.base import *
from transaction import TransactionController

log = logging.getLogger(__name__)

class SalesOrderController(TransactionController):

    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())
        self.query = self.query.filter_by(type=1)

    def render_edit(self):
        return render('/sales_order/edit.mako')

    def _save_custom(self, params):
        # insert area here
        if g.area_id > 0:
            params['area'] = g.area_id
        params['type'] = 1
        entry = model.Session.query(model.Inventory).filter_by(area=params['area']).filter_by(item=params['trans_item.item'])
        entry[0].qty -= int(params['trans_item.qty'])
        return params

