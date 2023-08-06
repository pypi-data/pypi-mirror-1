import logging

from divimon.lib.base import *
from transaction import TransactionController

log = logging.getLogger(__name__)

class PurchaseReceiptController(TransactionController):
    pass
    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())
        self.query = self.query.filter_by(type=5)

    def render_edit(self):
        return render('/purchase_receipt/edit.mako')

    #def _save_custom(self, params):
        ## insert branch here
        #if g.branch_id > 0:
            #params['branch'] = g.branch_id
        #params['type'] = 1
        #entry = model.Session.query(model.Inventory).filter_by(branch=params['branch']).filter_by(item=params['trans_item.item'])
        #entry[0].qty -= int(params['trans_item.qty'])
        #return params

