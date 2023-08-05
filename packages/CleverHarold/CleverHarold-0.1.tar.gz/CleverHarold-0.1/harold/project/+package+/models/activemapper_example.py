#/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This is an example model module using the SQLAlchemy ActiveMapper
# extension.  The code below is almost a verbatim copy+paste from the
# ActiveMapper examples.
#

from sqlalchemy import *
from sqlalchemy.ext.activemapper import (ActiveMapper, column, one_to_many,
                                         one_to_one, objectstore)


##
# Clever Harold 0.1 connects the default_metadata object only.  This will
# change in the near term.
__metadata__ = default_metadata


class Person(ActiveMapper):
    class mapping:
        id          = column(Integer, primary_key=True)
        full_name   = column(String)
        first_name  = column(String)
        middle_name = column(String)
        last_name   = column(String)
        birth_date  = column(DateTime)
        ssn         = column(String)
        gender      = column(String)
        home_phone  = column(String)
        cell_phone  = column(String)
        work_phone  = column(String)
        prefs_id    = column(Integer, foreign_key=ForeignKey('preferences.id'))
        addresses   = one_to_many('Address', colname='person_id', backref='person')
        preferences = one_to_one('Preferences', colname='pref_id', backref='person')

    def __str__(self):
        s =  '%s\n' % self.full_name
        s += '  * birthdate: %s\n' % (self.birth_date or 'not provided')
        s += '  * fave color: %s\n' % (self.preferences.favorite_color or 'Unknown')
        s += '  * personality: %s\n' % (self.preferences.personality_type or 'Unknown')

        for address in self.addresses:
            s += '  * address: %s\n' % address.address_1
            s += '             %s, %s %s\n' % (address.city, address.state, address.postal_code)

        return s


class Preferences(ActiveMapper):
    class mapping:
        __table__        = 'preferences'
        id               = column(Integer, primary_key=True)
        favorite_color   = column(String)
        personality_type = column(String)


class Address(ActiveMapper):
    class mapping:
        id          = column(Integer, primary_key=True)
        type        = column(String)
        address_1   = column(String)
        city        = column(String)
        state       = column(String)
        postal_code = column(String)
        person_id   = column(Integer, foreign_key=ForeignKey('person.id'))
