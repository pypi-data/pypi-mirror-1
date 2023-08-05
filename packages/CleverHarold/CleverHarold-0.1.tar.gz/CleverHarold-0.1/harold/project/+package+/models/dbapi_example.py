#/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This is an example model for the DBAPI data provider.  The minimum requirements
# are objects with 'create' and 'drop' strings; these are considered tables.
#
# This is example (and the DBAPI provider) aren't meant to replace an ORM, only
# to serve as a starting point for future capabilities.
#


class Person:
    create = "CREATE TABLE person (firstName TEXT, middleInitial TEXT, lastName TEXT)"
    drop = "DROP TABLE person"


class Address:
    create = "CREATE TABLE address (street TEXT, city TEXT, state TEXT, zip TEXT)"
    drop = "DROP TABLE address"
