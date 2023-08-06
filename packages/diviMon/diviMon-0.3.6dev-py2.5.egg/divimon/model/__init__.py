
from datetime import datetime
from pylons import config
from sqlalchemy import Column, MetaData, Table, ForeignKey
from sqlalchemy.types import *
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import mapper, relation

import divimon.lib.helpers as h


Session = scoped_session(sessionmaker(autoflush=True, transactional=True,
    bind=config['pylons.g'].sa_engine))

meta = MetaData()

agent = Table('agent', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u''),
        Column('area', Integer, ForeignKey('area.id')),
        Column('address', Unicode(1024), default=u''),
        Column('created', DateTime, nullable=False, default=datetime.now),
    )

area = Table('area', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u''),
        Column('details', Unicode(1024), default=u''),
        Column('created', DateTime, nullable=False, default=datetime.now),
    )

confirm = Table('confirm', meta,
        Column('id', Integer, primary_key=True),
        Column('dr', Integer, ForeignKey('transaction.id')),
        Column('quantity', Integer, default=0),
        Column('created', DateTime, nullable=False, default=datetime.now),
    )

cheque = Table('cheque', meta,
        Column('id', Integer, primary_key=True),
        Column('dr', Integer, ForeignKey('transaction.id')),
        Column('date', Date, nullable=False, default=datetime.now),
        Column('bank_details', Unicode(1024), default=u''),
        #Column('bank_name', Unicode(1024), default=u''),
        #Column('bank_branch', Unicode(1024), default=u''),
        Column('amount', Float, default=0),
        Column('status', Integer, ForeignKey('cheque_status.id')),
        Column('created', DateTime, nullable=False, default=datetime.now),
    )

cheque_status = Table('cheque_status', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u''),
        Column('created', DateTime, nullable=False, default=datetime.now),
    )

customer = Table('customer', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u''),
        Column('area', Integer, ForeignKey('area.id')),
        Column('address', Unicode(1024), default=''),
        #Column('credit_limit', Float, default=0),
        Column('created', DateTime, nullable=False, default=datetime.now),
    )

#amount = Table('amount', meta,
        #Column('id', Integer, primary_key=True),
        #Column('amount', Float, nullable=False, default=0),
        #Column('classification', Integer, ForeignKey('amount_class.id')),
        #Column('created', DateTime, nullable=False, default=datetime.now),
    #)

#amount_class = Table('amount_class', meta,
        #Column('id', Integer, primary_key=True),
        #Column('name', Unicode(64), nullable=False),# expense, budget
        #Column('created', DateTime, nullable=False, default=datetime.now),
    #)

budget = Table('budget', meta,
        Column('id', Integer, primary_key=True),
        Column('budget', Float, nullable=False, default=0),
        Column('month', Date, nullable=False, default=datetime.now),
        Column('created', DateTime, nullable=False, default=datetime.now),
    )

budget_expense = Table('budget_expense', meta,
        Column('id', Integer, primary_key=True),
        Column('budget', Integer, ForeignKey('budget.id')),
        Column('expense', Integer, ForeignKey('expense.id')),
        Column('created', DateTime, nullable=False, default=datetime.now),
    )

expense = Table('expense', meta,
        Column('id', Integer, primary_key=True),
        Column('area', Integer, ForeignKey('area.id')),
        Column('release', Float, nullable=False, default=0),
        Column('returns', Float, nullable=False, default=0),
        Column('created', DateTime, nullable=False, default=datetime.now),
    )

expense_breakdown = Table('expense_breakdown', meta,
        Column('id', Integer, primary_key=True),
        Column('expense', Integer, ForeignKey('expense.id')),
        Column('fuel', Float, nullable=False, default=0),
        Column('meal', Float, nullable=False, default=0),
        Column('toll_fee', Float, nullable=False, default=0),
        Column('miscellaneous', Float, nullable=False, default=0),
        Column('created', DateTime, nullable=False, default=datetime.now),
    )

expense_type = Table('expense_type', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(64), nullable=False),
        Column('created', DateTime, nullable=False, default=datetime.now),
    )

history = Table('history', meta,
        Column('id', Integer, primary_key=True),
        Column('user', Integer, ForeignKey('user.id')),
        Column('controller', Unicode(64), nullable=False, default='index'),
        Column('action', Unicode(64), nullable=False, default='index'),
        Column('arguments', Unicode(1024), nullable=False, default=u''),
        #Column('c', Unicode(1024), nullable=False, default=u''),
        Column('created', DateTime, nullable=False, default=datetime.now()),
    )

ht_session = Table('session', meta,
        Column('id', Integer, primary_key=True),
        #Column('user', Unicode(128), unique=False),
        Column('user', Integer, ForeignKey('user.id')),
        Column('login', DateTime, unique=False),
    )

inventory = Table('inventory', meta,
        Column('id', Integer, primary_key=True),
        Column('item', Integer, ForeignKey('item.id')),
        Column('qty', Float, nullable=False, default=0),
        Column('created', DateTime, nullable=False, default=datetime.now()),
    )

item = Table('item', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(128), default=u'', unique=True),
        #Column('code', Unicode(32), default=u'', unique=True),
        Column('description', Unicode(1024), default=u''),
        Column('unit', Unicode(16), default=u''),
        Column('price', Float, nullable=False, default=0),
        Column('purchase_price', Float, nullable=False, default=0),
        Column('created', DateTime, nullable=False, default=datetime.now()),
    )

pay_type = Table('pay_type', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(64), nullable=False),
        Column('created', DateTime, nullable=False, default=datetime.now()),
    )

pay_status = Table('pay_status', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(64), nullable=False),
        Column('created', DateTime, nullable=False, default=datetime.now()),
    )

role = Table('role', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(256), nullable=False, default=u''),
        Column('created', DateTime, nullable=False, default=datetime.now()),
    )

stocks_out = Table('stocks_out', meta,
        Column('id', Integer, primary_key=True),
        Column('created', DateTime, nullable=False, default=datetime.now),
        Column('dr', Integer, ForeignKey('transaction.id')),
        Column('item', Integer, ForeignKey('item.id')),
        Column('area', Integer, ForeignKey('area.id')),
        Column('qty', Float, nullable=False, default=0),
        Column('confirmed', Float, nullable=False, default=0),
    )

transaction = Table('transaction', meta,
        Column('id', Integer, primary_key=True),
        Column('area', Integer, ForeignKey('area.id')),
        Column('type', Integer, ForeignKey('trans_type.id')),
        Column('total_price', Float, nullable=False, default=0),
        Column('customer', Integer, ForeignKey('customer.id')),
        Column('agent', Integer, ForeignKey('agent.id')),
        Column('created', DateTime, nullable=False, default=datetime.now),
        Column('pay_type', Integer, ForeignKey('pay_type.id')),
        Column('pay_status', Integer, ForeignKey('pay_status.id')),
        Column('created', DateTime, nullable=False, default=datetime.now()),
    )

trans_expense = Table('trans_expense', meta,
        Column('id', Integer, primary_key=True),
        Column('transaction', Integer, ForeignKey('transaction.id')),
        Column('expense', Integer, ForeignKey('expense.id')),
        Column('created', DateTime, nullable=False, default=datetime.now()),
    )

trans_item = Table('trans_item', meta,
        Column('id', Integer, primary_key=True),
        Column('transaction', Integer, ForeignKey('transaction.id')),
        Column('item', Integer, ForeignKey('item.id')),
        Column('qty', Float, nullable=False, default=0),
        Column('price', Float, nullable=False, default=0),
        Column('in_out', Unicode(3), nullable=False, default='out'),
        Column('received_qty', Float, nullable=False, default=0),
        Column('created', DateTime, nullable=False, default=datetime.now()),
    )

trans_type = Table('trans_type', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(64), nullable=False),
        Column('created', DateTime, nullable=False, default=datetime.now()),
    )

user = Table('user', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(256), nullable=False, default=u''),
        Column('password', Unicode(256), nullable=False, default=u''),
        Column('role', Integer, ForeignKey('role.id')),
        Column('email_address', Unicode(256), nullable=False, default=u''),
        Column('details', Unicode(1024), default=u''),
        Column('created', DateTime, nullable=False, default=datetime.now()),
    )


def list(cls):
    return Session.query(cls)

def get(cls, id):
    return Session.query(cls).get(id)


class Base(object):
    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

    def __init__(self, **kw):
        for k,v in kw.iteritems():
            setattr(self, k, v)


class Agent(Base):
    pass

class Area(Base):
    pass

class Budget(Base):
    pass

class BudgetExpense(Base):
    pass

class Cheque(Base):
    pass

class Cheque_status(Base):
    pass

class Confirm(Base):
    pass

class Customer(Base):
    pass

class Expense(Base):
    pass

class ExpenseBreakdown(Base):
    pass

#class ExpenseType(Base):
    #pass

class History(Base):
    pass

class HTSession(Base):
    pass

class Inventory(Base):
    pass

class Item(Base):
    children = dict(
            inventory = 'Inventory',
        )

class PayStatus(Base):
    pass

class PayType(Base):
    pass

class Role(Base):
    pass

class Transaction(Base):
    children = dict(
            trans_item = 'TransItem',
        )

class TransExpense(Base):
    pass

class TransItem(Base):
    pass

class TransType(Base):
    pass

class StocksOut(Base):
    pass

class User(Base):
    pass


mapper(History, history)

mapper(HTSession, ht_session)
mapper(User, user, properties=dict(
        ht_session=relation(HTSession),
    ))
mapper(Role, role, properties=dict(
        user=relation(User),
    ))

mapper(Agent, agent)
mapper(Area, area)
mapper(Budget, budget, properties=dict(
        expense=relation(Expense, secondary=budget_expense),
        budget_expense=relation(BudgetExpense),
    ))
mapper(BudgetExpense, budget_expense)
mapper(Cheque, cheque)
mapper(Cheque_status, cheque_status)
mapper(Confirm, confirm)
mapper(Customer, customer)
mapper(Expense, expense, properties=dict(
        expense_breakdown=relation(ExpenseBreakdown),
    ))
#mapper(ExpenseType, expense_type, properties=dict(
        #expense=relation(Expense),
    #))
mapper(ExpenseBreakdown, expense_breakdown)

mapper(Inventory, inventory)
mapper(Item, item, properties=dict(
        inventory=relation(Inventory),
    ))
mapper(PayType, pay_type, properties=dict(
        transaction=relation(Transaction),
    ))
mapper(PayStatus, pay_status, properties=dict(
        transaction=relation(Transaction),
    ))
mapper(StocksOut, stocks_out)
mapper(Transaction, transaction, properties=dict(
        item=relation(Item, secondary=trans_item),
        trans_item=relation(TransItem),
    ))
mapper(TransExpense, trans_expense)
mapper(TransItem, trans_item)
mapper(TransType, trans_type, properties=dict(
        transaction=relation(Transaction),
    ))

