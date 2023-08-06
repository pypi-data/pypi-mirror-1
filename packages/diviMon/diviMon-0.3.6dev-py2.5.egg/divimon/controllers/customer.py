import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class CustomerController(ListController):
    table = model.Customer
    parent = dict(
            area = dict(
                    table = model.Area,
                    column = 'name',
                ),
        )


    def _list_query(self):
        self.query = model.list(self.table).order_by(self.table.id.desc())
        try:
            area = request.params['area']
        except KeyError:
            return
        if area is not None and area != '':
            self.query = self.query.filter_by(area=area)

    def list_details(self):
        id = request.params['id']
        c.entry = model.list(self.table).get(id)
        c.parent = self.parent
        print c.parent
        return render('/customer/entry_details.mako')

    def render_list(self):
        if not request.params.has_key('area') or request.params['area'] == '':
            c.list_functions = ('delete')
        return render('/customer/list.mako')

