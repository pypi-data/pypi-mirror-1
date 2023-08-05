#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# Decorator for round-trip form validation
#
# Unlike the jsonexc module, the decorator here validates an entire form
# and throws and http redirect back to the original form (or specified
# target) when an exception occurs.
#
# To use the form redirector, define your callable, armor it normally,
# then add the armor.form decorator to the callable decorator stack,
# like so::
#
#     from harold import armor, form
#
#     @form.responder.redirect
#     def assign_inventory(part_id, quantity):
#         pass
#
# If and when the callable raises a ValidationError, the request will
# be (internally) redirected to the requesting URL with additional
# keys in the environment.  The key 'harold.form.errors' will hold the
# sequence of failed values, while the 'harold.form.values' sequence
# will hold all of the values successfully validated.
#
##
from paste.recursive import ForwardRequestException
from harold.lib import keys, make_annotated, ValidationError


form_anno_template = """
def %(name)s%(signature)s:
    %(docstring)r
    return %(name)s.func_form_anno%(values)s
"""


def redirect(**attrs):
    """ decorator to make callables act like form targets

    @param **attrs arbitrary keyword-value pairs to assign to the decorated function
    @return decorator function that wraps its original with form exception handling
    """
    
    def form_exceptions_deco(original):
        """ form_exceptions_deco(original) -> replace original with form-enabled copy

        @param original function to decorate
        @return replacement function that redirects when ValidationError is raised
        @exception Exception when function cannot determine redirect target
        """
        def form_anno(*varparams, **keyparams):
            """ form_anno(...) -> originals replacement proxies its calls here

            """
            try:
                ## the original function should be armored with validators.  if
                ## one or more of them creates an exception, we have a trap for
                ## that in the following clause.
                return original(*varparams, **keyparams)

            except (ValidationError, ), exc:
                try:
                    ## TODO:  conjure a better way to locate the environment
                    environ = keyparams[keys.env]

                    if not attrs.has_key('target'):
                        ## TODO:  shouldn't this be SCRIPT_NAME + / + PATH_INFO ?
                        ref = scr = environ.get('SCRIPT_NAME', '')
                    else:
                        ref = attrs['target']
                    
                    environ[keys.form_error] = dict(exc.args[0])
                    environ[keys.form_value] = dict(exc.args[1])
                    raise ForwardRequestException(ref)
                except (KeyError, ):
                    raise

                ## the call has fallen thru the cracks with no where
                ## else to go.  what would you do here?
                raise Exception('Exception with no where to go')


        replacement = make_annotated(original, form_anno_template)
        for k, v in attrs.items():
            setattr(replacement, k, v)            
        replacement.func_form_anno = form_anno
        return replacement
    
    return form_exceptions_deco
