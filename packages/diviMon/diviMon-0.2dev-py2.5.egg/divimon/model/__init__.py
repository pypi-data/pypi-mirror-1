
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
        Column('created', DateTime, nullable=False, default=datetime.now),
        Column('name', Unicode(64), default=''),
        Column('area', Integer, ForeignKey('area.id')),
        Column('address', UnicodeText, default=''),
    )

area = Table('area', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(64), default=''),
        Column('details', UnicodeText, default=''),
    )

confirm = Table('confirm', meta,
        Column('id', Integer, primary_key=True),
        Column('created', DateTime, nullable=False, default=datetime.now),
        Column('dr', Integer, ForeignKey('transaction.id')),
        Column('quantity', Integer, default=0),
    )

customer = Table('customer', meta,
        Column('id', Integer, primary_key=True),
        Column('created', DateTime, nullable=False, default=datetime.now),
        Column('name', Unicode(64), default=''),
        Column('area', Integer, ForeignKey('area.id')),
        Column('address', UnicodeText, default=''),
    )

inventory = Table('inventory', meta,
        Column('id', Integer, primary_key=True),
        Column('item', Integer, ForeignKey('item.id')),
        Column('qty', Float, nullable=False, default=0),
    )

item = Table('item', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(64), default=''),
        Column('description', UnicodeText, default=''),
        Column('unit', Unicode(16), default=''),
        Column('price', Float, nullable=False, default=0),
        Column('code', Unicode(32), default='', unique=True),
    )

pay_type = Table('pay_type', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(8), nullable=False),
    )

stocks_out = Table('stocks_out', meta,
        Column('id', Integer, primary_key=True),
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
    )

trans_item = Table('trans_item', meta,
        Column('id', Integer, primary_key=True),
        Column('transaction', Integer, ForeignKey('transaction.id')),
        Column('item', Integer, ForeignKey('item.id')),
        Column('qty', Float, nullable=False, default=0),
        Column('price', Float, nullable=False, default=0),
        Column('in_out', Unicode(3), nullable=False, default='out'),
        Column('received_qty', Float, nullable=False, default=0),
    )

trans_type = Table('trans_type', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(8), nullable=False),
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

class Confirm(Base):
    pass

class Customer(Base):
    pass

class Inventory(Base):
    pass

class Item(Base):
    pass

class PayType(Base):
    pass

class Transaction(Base):
    pass

class TransItem(Base):
    pass

class TransType(Base):
    pass

class StocksOut(Base):
    pass


mapper(Area, area)
mapper(Confirm, confirm)
mapper(Customer, customer)
mapper(Agent, agent)
mapper(Inventory, inventory)
mapper(Item, item, properties=dict(
        inventory=relation(Inventory),
    ))
mapper(PayType, pay_type, properties=dict(
        transaction=relation(Transaction),
    ))
mapper(StocksOut, stocks_out)
mapper(Transaction, transaction, properties=dict(
        item=relation(Item, secondary=trans_item),
        trans_item=relation(TransItem),
    ))
mapper(TransItem, trans_item)
mapper(TransType, trans_type, properties=dict(
        transaction=relation(Transaction),
    ))


