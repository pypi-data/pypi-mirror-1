import logging

from divimon.lib.base import *
from transaction import TransactionController

log = logging.getLogger(__name__)

class DeliveryConfirmController(TransactionController):
    list_functions = ()

    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())
        self.query = self.query.filter_by(type=3)

    def render_edit(self):
        return render('/delivery_confirm/edit.mako')#!!!wala

