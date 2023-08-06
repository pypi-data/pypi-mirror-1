
from datetime import datetime
from pylons import config
from sqlalchemy import Column, MetaData, Table, ForeignKey
from sqlalchemy.types import *
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import mapper, relation

import subicpos.lib.helpers as h


Session = scoped_session(sessionmaker(autoflush=True, transactional=True,
    bind=config['pylons.g'].sa_engine))

meta = MetaData()

adjustment = Table('adjustment', meta,
        Column('id', Integer, primary_key=True),
        Column('created', DateTime, nullable=False, default=datetime.now),
        Column('transaction', Integer, ForeignKey('transaction.id')),
        Column('branch', Integer, ForeignKey('branch.id')),
    )

adjust_item = Table('adjust_item', meta,
        Column('id', Integer, primary_key=True),
        Column('trans_item', Integer, ForeignKey('trans_item.id')),
        Column('adjustment', Integer, ForeignKey('adjustment.id')),
        Column('qty', Float, nullable=False, default=0),
        Column('action', Unicode(1), nullable=False, default='='),
    )

branch = Table('branch', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(64), default=''),
        Column('details', UnicodeText, default=''),
    )

classification = Table('classification', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(64), default=''),
        Column('description', UnicodeText, default=''),
    )

item = Table('item', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(64), default=''),
        Column('description', UnicodeText, default=''),
        Column('classification', Integer, ForeignKey('classification.id')),
        Column('price', Float, nullable=False, default=0),
        Column('code', Unicode(32), default='', unique=True),
    )

inventory = Table('inventory', meta,
        Column('id', Integer, primary_key=True),
        Column('item', Integer, ForeignKey('item.id')),
        Column('branch', Integer, ForeignKey('branch.id')),
        Column('qty', Float, nullable=False, default=0),
    )

pay_type = Table('pay_type', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(8), nullable=False),
    )

transaction = Table('transaction', meta,
        Column('id', Integer, primary_key=True),
        Column('branch', Integer, ForeignKey('branch.id')),
        Column('type', Integer, ForeignKey('trans_type.id')),
        Column('total_price', Float, nullable=False, default=0),
        Column('total_tendered', Float, nullable=False, default=0),
        Column('change', Float, nullable=False, default=0),
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

class Adjustment(Base):
    pass

class AdjustItem(Base):
    pass

class Branch(Base):
    pass

class Classification(Base):
    pass

class Item(Base):
    pass

class Inventory(Base):
    pass

class PayType(Base):
    pass

class Transaction(Base):
    pass

class TransItem(Base):
    pass

class TransType(Base):
    pass



mapper(Adjustment, adjustment, properties=dict(
        adjust_item=relation(AdjustItem),
    ))
mapper(AdjustItem, adjust_item)
mapper(Branch, branch, properties=dict(
        adjustment=relation(Adjustment),
        inventory=relation(Inventory),
        transaction=relation(Transaction),
    ))
mapper(Classification, classification)
mapper(Inventory, inventory)
mapper(Item, item, properties=dict(
        inventory=relation(Inventory),
    ))
mapper(PayType, pay_type, properties=dict(
        transaction=relation(Transaction),
    ))
mapper(Transaction, transaction, properties=dict(
        item=relation(Item, secondary=trans_item),
        trans_item=relation(TransItem),
    ))
mapper(TransItem, trans_item)
mapper(TransType, trans_type, properties=dict(
        transaction=relation(Transaction),
    ))


