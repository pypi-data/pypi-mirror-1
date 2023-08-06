import logging
from datetime import datetime,timedelta

from divimon.lib.base import *
from transaction import TransactionController
from stocks_out import StocksOutController
#created = datetime.Now()

log = logging.getLogger(__name__)

class StocksOutTodayController(StocksOutController):

    #def _list_query(self):
        #self.query = model.Session.query(self.table).order_by(self.table.id.desc())
        ##print dir(self.query)
        ##self.query = self.query.filter_by(created=str(datetime.now))#2008-07-02 07:52:06.441337
        ##try:
            ##area = request.params['area']
        ##except KeyError:
            ##return
        ##if area is not None and area != '':
            ##self.query = self.query.filter_by(area=area)

    def _list_query(self):
        self.query = model.Session.query(self.table).order_by(self.table.id.desc())
        now = datetime.now()
        today = datetime(now.year, now.month, now.day, 0, 0)
        tomorrow = today + timedelta(1)
        self.query = self.query.filter(self.table.c.created<tomorrow).filter(self.table.c.created>=today)