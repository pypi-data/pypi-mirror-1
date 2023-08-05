#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# mod_python wsgi handler for paste.
#
# Synopsis
# --------
#
# ::
#
#    [Location "/"]
#        SetHandler mod_python
#        PythonDebug Off
#        PythonInterpreter "application"
#        PythonPath "['/path/to/application', ] + sys.path"
#        PythonHandler harold.lib.mppaste::handler
#        PythonOption paste.config /path/to/application/application.ini
#        PythonOption paste.app application_name
#    [/Location]
#
##

from mod_python import apache
from paste.deploy import loadapp
from harold.lib.mpwsgi import WsgiAdapter

# should this be thread-local or synchronized?
apps = {}


def handler(req):
    """ maps mod_python request to a paste application indicated by the config

    @param req mod_python request object
    @return always returns apache.OK; HTTP status set by adapter
    """
    options = req.get_options()
    configname = options['paste.config']
    interpname = options.get('PythonInterpreter', None)
    appskey = (configname, interpname)
    
    try:
        app = apps[appskey]
    except (KeyError, ):
        appname = options.get('paste.app', None)
        relativeto = options.get('paste.relative_to', None)
        app = apps[appskey] = loadapp('config:%s' % configname,
                                      name=appname,
                                      relative_to=relativeto)
    WsgiAdapter(req).run(app)
    return apache.OK
    
