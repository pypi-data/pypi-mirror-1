from meta import *
mapper = Session.mapper

import types

sale_table = Table('sale', metadata,
    Column('id', Integer, primary_key=True),
    Column('price', Float),
    Column('quantity', Integer),
    Column('date', types.FlexiDateType),
    Column('item_id', Text, ForeignKey('item.id')),
    Column('price2', Float),
    Column('extras', types.JsonType),
)

from frbr import DomainObject, Item, orm

class Sale(DomainObject):
    pass

mapper(Sale, sale_table, properties={
    'item': orm.relation(Item, backref='sales')
    },
    order_by=sale_table.c.price,
)

