#/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This is an example model culled from the SQLObject documentation.
#

from sqlobject import *


class Person(SQLObject):
    firstName = StringCol()
    middleInitial = StringCol(length=1, default=None)
    lastName = StringCol()
    addresses = MultipleJoin('Address')
    roles = RelatedJoin('Role')
    

class Address(SQLObject):
    street = StringCol()
    city = StringCol()
    state = StringCol(length=2)
    zip = StringCol(length=9)
    person = ForeignKey('Person')


class Role(SQLObject):
    name = StringCol(alternateID=True, length=20)
    persons = RelatedJoin('Person')

