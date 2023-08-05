#/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This is an example model module using the SQLAlchemy package.  The
# code here was culled from the SA docs and it should give you a good
# starting point.
#

from sqlalchemy import *


##
# Clever Harold 0.1 connects the default_metadata object only.  This will
# change in the near term.
from sqlalchemy.schema import default_metadata as metadata


person_table = Table('person', metadata, 
    Column('person_id', Integer, primary_key=True),
    Column('person_name', String(16)),
    Column('password', String(20)),
)


address_table = Table('address', metadata,
    Column('address_id', Integer, primary_key=True),
    Column('person_id', Integer, ForeignKey("person.person_id")),
    Column('street', String(100)),
    Column('city', String(80)),
    Column('state', String(2)),
    Column('zip', String(10)),
)


class Person(object):
    def __init__(self, person_name, password):
        self.person_name = person_name
        self.password = password

    def __str__(self):
        return 'Person: %s' % (self.person_name, )


class Address(object):
    def __init__(self, street, city, state, zip):
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip


person_mapper = mapper(Person, person_table,
                       properties=dict(addresses=relation(Address))
)
address_mapper = mapper(Address, address_table)
