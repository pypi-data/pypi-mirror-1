#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

def get():
    return None

get.expose = True
get.content_type = 'text/json'


class AudioFile:
    expose = ['__call__']
    def __init__(self, filename, length=30):
        self.filename = filename
        self.length = length

    def __call__(self):
        return 'filename=%s; length=%s' % (self.filename, self.length)


class AudioDisc:
    expose = ['__call__']
    def __init__(self):
        self.id = '3'

    def __call__(self, name):
        return 'id=%s; name=%s' % (self.id, name)


class AudioRack:
    expose = ['__call__']
    def __init__(self, id):
        self.id = id

    def __call__(self, status):
        return 'id=%s; status=%s' % (self.id, status)


class AudioTrack:
    expose = ['__call__']
    def __init__(self, id, name):
        self.id = id
        self.name = name

    ## no __call__

    def __repr__(self):
        return 'id=%s; name=%s' % (self.id, self.name)


class AudioClip:
    expose = ['__call__']
    
    def __init__(self, environ):
        self.environ = environ

    def __call__(self):
        return self.environ['wsgi.version']


class AudioDevice:
    expose = ['__call__']
    
    def __init__(self, environ):
        self.environ = environ

    def __call__(self, application):
        return self.environ['wsgi.version'], application

