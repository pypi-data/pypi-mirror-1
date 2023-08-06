'''Domain Model based on FRBR.

(For info on FRBR see docs/frbr.txt)
 
Item (Release): corresponds to a published item (not the individual item but that
particular run -- i.e. something with e.g. an ISBN). Item usually
corresponds to a single work but can contain many works.

Work: Represents the underlying work. So, for example, different published
editions (or recordings) of Beethoven\'s Ninth Symphony will all have an
associated underlying work "Beethoven\'s Ninth Symphony".

Person: any kind of entity

Persons are associated to Works and Items in a many 2 many relationship with a
role attribute.
  * We also allow the same person to be associated with the same work/item many
    times (to allow for the possibility that the same person has multiple
    roles).

Relation to FRBR
================

FRBR has conceptual model:

  Work
    - Expression (aka Edition)
      - Manifestation
        - Item

Crudely our mapping is:

PDW Work --> FRBR Work (+ some FRBR Expressions)
PDW Item --> FRBR Manifestation (+ some FRBR expressions)

  * Works have types.   
  * We allow works to refer to other works.
  * An item may have many works.

Examples of how this works:
---------------------------

0. Catalogues (from e.g. a Library or Amazon)

All catalogues list Items in our system (in FRBR terms one could see them as
Manifestation or Editions).

1. Book: "Forsyte Saga (vol 1)" by Galsworthy

work: Forsyte Saga (vol 1)
expression: Forsyte Saga X Edition
manifestation/item: Penguin book isbn XXXXX published ...

In our system we we\'d have a single work for the Forsyte saga. A new edition would
not be registered as a new work *unless* it represented such a major change as
justifying a new copyright (for example a translation would fall into this
category).

The Manifestation/Item becomes an Item in our system.


2. Recording: von Karajan conducting Beethoven Symphony No. 1 in A minor

work: (composition) Beethoven Symphony in A minor
work: (recording/performance): von Karajan recording
  
manifestation (release)
  * may contain many recordings 
  * has tracks etc

In our system:
  * Work 1: Beethoven Symphony
  * Work 2: von Karajan recording
  * Item: The release


Notes on FlexiDate implementation
=================================

Support for having arbitrary dates but which can be sorted properly and have an
associated machine-readable version.

For any given date attributed \'date\' end up with 3 cols:

  * _date (represented on object as date)
  * date_normed
  * date_ordered


'''
import os
import urllib

# SQLAlchemy stuff
from sqlalchemy import *
from sqlalchemy import orm
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from types import *
from meta import metadata, Session
import pdw.name

mapper = Session.mapper

# Enumerations
class ROLES:
    author = u'author'
    editor = u'editor'
    performer = u'performer'

class WORK_TYPES:
    text = u'text'
    composition = u'composition'
    recording = u'recording'
    photograph = u'photograph'

class ENTITY_TYPES:
    person = u'person'
    organization = u'organization'

person_table = Table('person', metadata,
    Column('id', UuidType, primary_key=True, default=UuidType.default),
    Column('srcid', UnicodeText),
    Column('name', UnicodeText),
    Column('aka', UnicodeText),
#   Flexidate columns
#    Column('birth_date', FlexiDateType),
    Column('birth_date', types.UnicodeText), # user entered version
    Column('birth_date_normed', types.UnicodeText), # iso 8601
    Column('birth_date_ordered', types.Float), # ordered version see swiss.date
#   Flexidate columns
#    Column('death_date', FlexiDateType),
    Column('death_date', types.UnicodeText), # user entered version
    Column('death_date_normed', types.UnicodeText), # iso 8601
    Column('death_date_ordered', types.Float), # ordered version see swiss.date
    Column('entity_type', Unicode(255), default=ENTITY_TYPES.person),
    Column('notes', UnicodeText),
)

work_table = Table('work', metadata,
    Column('id', UuidType, primary_key=True, default=UuidType.default),
    Column('srcid', UnicodeText),
    Column('title', UnicodeText),
    Column('type', Unicode(100), default=WORK_TYPES.text),
#   Flexidate columns
#    Column('date', FlexiDateType),
    Column('date', types.UnicodeText), # user entered version
    Column('date_normed', types.UnicodeText), # iso 8601
    Column('date_ordered', types.Float), # ordered version see swiss.date
    Column('notes', UnicodeText),
)

item_table = Table('item', metadata,
    Column('id', UuidType, primary_key=True, default=UuidType.default),
    Column('srcid', UnicodeText),
    Column('title', UnicodeText),
#   Flexidate columns
#    Column('date', FlexiDateType),
    Column('date', types.UnicodeText), # user entered version
    Column('date_normed', types.UnicodeText), # iso 8601
    Column('date_ordered', types.Float), # ordered version see swiss.date
    Column('type', Unicode(100), default=WORK_TYPES.text),
    Column('notes', UnicodeText),
)

extra_table = Table('extra', metadata,
    Column('id', Integer, primary_key=True),
    # name of table
    Column('table', Unicode(100)),
    # must always have UUIDs as pks ...
    Column('fkid', UuidType),
    Column('key', UnicodeText),
    Column('value', JsonType),
)

work_2_item = Table('work_2_item', metadata,
    Column('work_id', UuidType, ForeignKey('work.id'), primary_key=True),
    Column('item_id', UuidType, ForeignKey('item.id'), primary_key=True),
)

work_2_person = Table('work_2_person', metadata,
    Column('work_id', UuidType, ForeignKey('work.id'), primary_key=True),
    Column('person_id', UuidType, ForeignKey('person.id'), primary_key=True),
    Column('role', UnicodeText, default=ROLES.author)
)

item_2_person = Table('item_2_person', metadata,
    Column('item_id', UuidType, ForeignKey('item.id'), primary_key=True),
    Column('person_id', UuidType, ForeignKey('person.id'), primary_key=True),
    Column('role', UnicodeText, default=ROLES.author)
)


class DomainObject(object):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        repr = '<%s' % self.__class__.__name__
        table = orm.class_mapper(self.__class__).mapped_table
        for col in table.c:
            repr += ' %s=%s' % (col.name, getattr(self, col.name))
        return repr.encode('utf8', 'ignore')
    
    def __repr__(self):
        return self.__str__()

    def purge(self):
        Session.delete(self)


def _create_person_work(work, role=ROLES.author):
    return WorkPerson(work=work, role=role)

class Person(DomainObject):
    items = association_proxy('item_persons', 'item',
        #creator=_create_item_person
        )
    works = association_proxy('work_persons', 'work',
        # creator=_create_person_work
        )

    @classmethod
    def by_name(self, name, create=True):
        '''Return first Person with name `name`, or create if does not
        exist and `create` is True.
        '''
        out = self.query.filter_by(name=name).first()
        if out:
            return out
        elif create:
            return Person(name=name)
        else:
            return None

    def _readable_id(self):
        name_str = pdw.name.normalize(self.name, parser_class=pdw.name.FirstLast).strip()
        name_str = name_str.encode('utf8') # needs to be utf8 not unicode for the urllib.quote
        name_str = name_str.replace(' ', '_')
        encoded_name = urllib.quote(name_str)
        
        return encoded_name 
    readable_id = property(_readable_id)

def _decode_person_readable_id(readable_id):
    name_str = urllib.unquote(readable_id)
    name_str = name_str.replace('_', ' ')
    name_str = name_str.decode('utf8')
    decoded_name = pdw.name.normalize(name_str, parser_class=pdw.name.LastFirst).strip()
    return decoded_name

def get_persons_matching_readable_id_query(readable_id):
    name = _decode_person_readable_id(readable_id)
    artist_query = Person.query.filter_by(name=name)
    return artist_query



def _create_work_person(person, role=ROLES.author):
    return WorkPerson(person=person, role=role)

class Work(DomainObject):
    persons = association_proxy('work_persons', 'person', creator=_create_work_person)

    def __str__(self):
        out = super(Work, self).__str__()
        out += ' person=%s' % [ a.__str__() for a in self.persons ]
        return out

    def _readable_id(self):
        if self.persons:
            name = self.persons[0].name # assume first person is creator for now
            name_str = pdw.name.normalize(name, parser_class=pdw.name.FirstLast).strip()
        else:
            name_str = ""
        encoded_name = ('%s--%s' % (self.title, name_str)).replace(' ', '_')
        
        return encoded_name 
    readable_id = property(_readable_id)

def _decode_work_readable_id(readable_id):
    decoded_title, decoded_name = "", ""
    readable_id_sections = readable_id.split("--")
    if len(readable_id_sections) == 2:
        for i in range(len(readable_id_sections)):
            readable_id_sections[i] = readable_id_sections[i].replace('_', ' ')
        decoded_title, name_str = readable_id_sections
        decoded_name = pdw.name.normalize(name_str, parser_class=pdw.name.LastFirst).strip()
    return decoded_title, decoded_name

def get_works_matching_readable_id(readable_id):
    title, name = _decode_work_readable_id(readable_id)
    artist_query = Work.query.filter(and_(Work.title==title, Person.name==name))
    return artist_query.all()


def _create_item_person(person, role=ROLES.author):
    return ItemPerson(person=person, role=role)

class Item(DomainObject):
    def __str__(self):
        out = super(Item, self).__str__()
        out += ' person=%s' % [ a.__str__() for a in self.persons ]
        return out
    persons = association_proxy('item_persons', 'person', creator=_create_item_person)

    def _readable_id(self):
        if self.persons:
            name = self.persons[0].name # assume first person is creator for now
            name_str = pdw.name.normalize(name, parser_class=pdw.name.FirstLast).strip()
        else:
            name_str = ""
        encoded_name = ('%s--%s' % (self.title, name_str)).replace(' ', '_')
        
        return encoded_name 
    readable_id = property(_readable_id)

def _decode_item_readable_id(readable_id):
    decoded_title, decoded_name = "", ""
    readable_id_sections = readable_id.split("--")
    if len(readable_id_sections) == 2:
        for i in range(len(readable_id_sections)):
            readable_id_sections[i] = readable_id_sections[i].replace('_', ' ')
        decoded_title, name_str = readable_id_sections
        decoded_name = pdw.name.normalize(name_str, parser_class=pdw.name.LastFirst).strip()
    return decoded_title, decoded_name

def get_items_matching_readable_id(readable_id):
    title, name = _decode_item_readable_id(readable_id)
    artist_query = Item.query.filter(and_(Item.title==title, Person.name==name))
    return artist_query.all()

class WorkItem(DomainObject):
    pass

class WorkPerson(DomainObject):
    def __init__(self, work=None, person=None, role=None):
        self.work = work
        self.person = person
        self.role = role


class ItemPerson(DomainObject):
    def __init__(self, item=None, person=None, role=None):
        self.item = item
        self.person = person
        self.role = role

class Extra(DomainObject):
    pass

def extraable(cls, name='_extras', usedict=True):
    mapper = orm.class_mapper(cls)
    table = mapper.local_table
    table_name = unicode(table.name)
    primaryjoin = and_(
        extra_table.c.table == table_name,
        extra_table.c.fkid == list(table.primary_key)[0]
        )
    foreign_keys = [extra_table.c.fkid]
    from sqlalchemy.orm.collections import attribute_mapped_collection
    mapper.add_property(name, orm.relation(
        Extra,
        primaryjoin=primaryjoin,
        foreign_keys=foreign_keys,
        collection_class=attribute_mapped_collection('key'),
        # backref
        )
    )
    from sqlalchemy.ext.associationproxy import association_proxy
    def _create_extra(key, value):
        return Extra(table=table_name, key=unicode(key), value=value)
    cls.extras = association_proxy('_extras', 'value',
                creator=_create_extra)

import swiss.date as date_mod
def add_flexidate(domain_object, name):
    def get_date(self):
        return getattr(self, '_%s' % name)
    def set_date(self, newdate):
        if newdate:
            # we will use synonym on mapper below so prefix with '_'
            setattr(self, '_%s' % name, unicode(newdate))
            # TODO: normalize and make orderable
            flexidate = date_mod.parse(newdate)
            normed = unicode(flexidate.isoformat())
            ordered = flexidate.as_float()
            setattr(self, '%s_normed' % name, normed)
            setattr(self, '%s_ordered' % name, ordered)
    setattr(domain_object, '_get_%s' % name, get_date)
    setattr(domain_object, '_set_%s' % name, set_date)
    setattr(domain_object, name, property(get_date, set_date))

add_flexidate(Person, 'birth_date')
add_flexidate(Person, 'death_date')
add_flexidate(Work, 'date')
add_flexidate(Item, 'date')

## Custom Property for FlexiDate

# TODO: not yet usable properly as require SQLAlchemy >= 0.5
from sqlalchemy import sql
class FlexiDateComparator(orm.PropComparator):

    def _get_ordered(self, other):
        ordered_name = self.prop.name + '_ordered'
        col = self.prop.table.c[ordered_name]
        other = swiss.date.parse(other).as_float()
        return (col, other)

    def __gt__(self, other):
        """define the 'greater than' operation"""
        col, val = self._get_ordered(other)
        return col < val

    def __eq__(self, other):
        col, val = self._get_ordered(other)
        return col == val

mapper(Work, work_table, properties={
    # should use FlexiDateComparator here
    # but not supported in synonyms until SQLAlchemy 0.5
    # comparator_factory=FlexiDateComparator
    'date':orm.synonym('_date', map_column=True),
    'items':orm.relation(Item, secondary=work_2_item, backref='works'),
    },
    order_by=work_table.c.title,
)
mapper(Item, item_table, properties={
    # comparator_factory=FlexiDateComparator
    'date':orm.synonym('_date', map_column=True),
    },
    order_by=item_table.c.title,
)
mapper(Person, person_table, properties={
    # comparator_factory=FlexiDateComparator
    'birth_date':orm.synonym('_birth_date', map_column=True),
    'death_date':orm.synonym('_death_date', map_column=True),
    },
    order_by=person_table.c.name,
    )
mapper(WorkPerson, work_2_person, properties={
    'work': orm.relation(Work,
        backref=orm.backref('work_persons',
            cascade='all, delete, delete-orphan',
            ),
        # pointless ...
        order_by=work_table.c.title,
        ),
    'person': orm.relation(Person,
        backref=orm.backref('work_persons',
            cascade='all, delete, delete-orphan',
            ),
        # pointless ...
        order_by=person_table.c.name,
        ),
    },
    order_by=work_2_person.c.work_id,
    )
mapper(ItemPerson, item_2_person, properties={
    'item': orm.relation(Item,
        backref=orm.backref('item_persons',
            cascade='all, delete, delete-orphan'),
        ),
    'person': orm.relation(Person,
        backref=orm.backref('item_persons',
            cascade='all, delete, delete-orphan'),
        ),
    },
    order_by=item_2_person.c.item_id,
)
mapper(WorkItem, work_2_item)
mapper(Extra, extra_table)
extraable(Work)
extraable(Item)
extraable(Person)

