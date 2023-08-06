import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class AgentController(ListController):
    table = model.Agent
    parent = dict(
            area = dict(
                    table = model.Area,
                    column = 'name',
                ),
        )

    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())
        try:
            area = request.params['area']
        except KeyError:
            return
        if area is not None and area != '':
            self.query = self.query.filter_by(area=area)

    def render_list(self):
        if not request.params.has_key('area') or request.params['area'] == '':
            c.list_functions = ('delete')
        return render('/delivery_receipt/list.mako')
