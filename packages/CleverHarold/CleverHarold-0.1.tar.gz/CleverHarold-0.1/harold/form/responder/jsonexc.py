#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# JSON exception decorator
#
# The json decorator calls its decorated function normally,
# and if there is an exception during the call, it instead returns the
# exception values as a json-encoded mapping.
#
# This is especially useful when combined with the validators, because
# the validators store all of their exceptions before raising their own.
# The effect of this is that all parameters are validated and all
# invalid values are specified at once.
#
# Note that the json decorator *does not* encode normal
# responses, only exceptions.  To encode the normal responses, the
# Harold code publisher should be used.  The code publisher and this
# decorator should be used together.
#
# When a decorated function raises a ValidationError, as it will when one of its
# validators fails, it will return a mapping in the form of::
#
#    {'errors' : [sequence of errors],
#     'values' : [sequence, of valid values] }
#
# When any other exception type is raised, the 'values' sequence will be empty.
#
#
##
from inspect import getargspec
from harold.lib import keys, con_type, make_annotated, ValidationError


json_anno_template = """
def %(name)s%(signature)s:
    %(docstring)r
    return %(name)s.func_json_anno%(values)s
"""


def json(**attrs):
    """ returns decorator for making json exception handlers

    @param **attrs arbitrary keyword-value pairs to assign to the decorated function
    @return decorator function that wraps its original with JSON exception handling
    """
    content_type = 'content_type'
    exc_status = '500 Internal Server Error'

    if content_type not in attrs:
        attrs[content_type] = con_type.json


    def make_json_env(func, params, kwds):
        """ make_json_env(...) -> hack to locate the wsgi environ and munge it

        """
        args, varargs, varkw, defaults = getargspec(func)
        if keys.env in args:
            environ = params[args.index(keys.env)]
        else:
            environ = kwds.get(keys.env, {})
        environ[keys.content_type] = con_type.json
        environ[keys.response_status] = exc_status


    def json_deco(original):
        """ json_deco(original) -> replace original with a json-enabled copy

        """
        def json_anno(*varparams, **keyparams):
            """ json_anno(...) -> annotation which makes exceptions json-friendly

            original return values and execption values should be
            json-encoded elsewhere. (e.g., by the harold code
            publisher).
            """
            try:
                return original(*varparams, **keyparams)
            except (ValidationError, ), exc:
                make_json_env(original, varparams, keyparams)
                return dict(errors=exc.args[0], values=exc.args[1])
            except (Exception, ), exc:
                make_json_env(original, varparams, keyparams)
                return dict(errors=[str(exc), ], values=[])

        replacement = make_annotated(original, json_anno_template)
        for k, v in attrs.items():
            setattr(replacement, k, v)
        replacement.func_json_anno = json_anno
        return replacement
    
    return json_deco
