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
        self._dbg('list', request.params)
        self._list_params()
        self._list_query()
        self._list()
        return render('/report_list.mako')

