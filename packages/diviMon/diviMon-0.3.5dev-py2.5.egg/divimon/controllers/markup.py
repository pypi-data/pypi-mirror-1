import logging

from divimon.lib.base import *
from transaction import TransactionController
from stocks_out import StocksOutController

log = logging.getLogger(__name__)

class MarkupController(ListController):
    table = model.Transaction

    def daily(self):
        return render('/budget/daily_markup.mako')

    def weekly(self):
        return render('/budget/weekly_markup.mako')

    def index(self, id):
        return id
