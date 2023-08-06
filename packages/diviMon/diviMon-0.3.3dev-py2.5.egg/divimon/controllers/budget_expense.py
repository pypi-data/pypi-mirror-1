import logging

from divimon.lib.base import *
from divimon import model

log = logging.getLogger(__name__)

class BudgetExpenseController(ListController):
    table = model.BudgetExpense
    parent = dict(
        budget = dict(
                table = model.Budget,
                column = 'id',
            ),
        expense = dict(
                table = model.Expense,
                column = 'id',
            ),
        )
