#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# This module defines decorators to protect functions from bad
# values.
#
# Using the Validator Excpetion Decorators
# ----------------------------------------
# To use the validation decorators in this module, first define your
# functions normally::
#
#     def change_password(user_id, new_password, confirm_password):
#         """ update the password for user specified by user_id """
#         user = lookup_user(user_id)
#         set_password(user, new_password)
#
#
# Then decorate your callable with armor.add and armor.fuse, like so::
#
#     from harold import armor
#    
#     @armor.fuse
#     @armor.add('user_id', is_real_user_id, is_active_user_id)
#     @armor.add(('new_password', 'confirm_password'), passwords_match)
#
#     def change_password(user_id, new_password, confirm_password):
#         """ update the password for user specified by user_id """        
#         user = lookup_user(user_id)
#         set_password(user, new_password)
#
#
# The validator functions are passed the value of each parameter named
# in the @armor.add decorator call, from left to right.  The result
# of each call is either fed to the next validator or used during the
# final call to the underlying function.
#
# Writing Validator Functions
# ---------------------------
# Validator functions can take one or more arguments, and those
# arguments are mapped from the parameters passed to the armor-enabled
# function.  For example, in the sample above, the parameter 'user_id'
# will be mapped as the only argument to the 'is_real_user_id' callable,
# and again to the 'is_active_user_id' callable.
#
# Validator functions can take more than one argument.  Such validator
# functions will have their parameters mapped by the enforcer from the
# named arguments into the positional arguments of the validator function.
#
# Validator functions must either raise an exception or return the same
# number of values that they are given.  The value(s) may be modified by
# the validator (thus making the validator function a validator and
# converter), but the number of return values must be the same as the
# number of parameters given with the corresponding @armor.add
# decorator.  Validator functions can raise any type of exception, and
# do not need to use the exception classes defined in this package.
#
# To illustrate, the above validator functions might be written like
# this::
#
#     def is_real_user_id(uid):
#         if not run_user_query(uid):
#             raise Exception('Unknown user')
#         return uid
#
#     def is_active_user_id(uid):
#         if not run_active_user_query(uid):
#             raise Exception('User account suspended')
#         return uid
#
#     def passwords_match(password, confirm):
#         if password != confirm:
#             raise TypeError('Passwords do not match')
#         return password, confirm
#
#
# Special Note
# ------------
# Validator functions with parameter named 'environ' or that accept
# keyword parameters will be passed the WSGI request environment if
# available.  This may be expaneded in the future to include all of
# the magic names from Harold.
#
# Special Note
# ------------
# Validator functions with extra positional arguments (e.g., \*params)
# are not supported yet, and may never be.
#
##


from inspect import getargspec
from harold.armor.basetypes import basetypes
from harold.lib import keys, make_annotated, ValidationError, DecorationError


validation_anno_template = """
def %(name)s%(signature)s:
    %(docstring)r
    return %(name)s.func_validation_anno%(values)s
"""


def add(names, *validators):
    """ decorator for annotating functions with validators

    @param names parameter name as string or tuple of names
    @param *validators one or more validators to associate with the parameter names
    @return decorator function that adds 'func_validators' attribute to decorated function
    """
    try:
        names + ''
        names = (names, )
    except (TypeError, ):
        names = tuple(names)

    def add_deco(original):
        """ add_deco(original) -> decorate original with validator mapping

        @param original function to decorate with validators
        @return original with 'func_validators' list attribute
        """
        ## ensure each of the argument names is in the original
        ## functions signature.
        args, varargs, varkw, defaults = getargspec(original)
        for value in (varargs, varkw):
            if value is not None:
                args.append(varargs)
        for name in names:
            if name not in args:
                raise DecorationError('cannot validate missing argument')

        ## find the validator mapping or create it if needed.
        try:
            valmap = original.func_validators
        except (AttributeError, ):
            valmap = original.func_validators = []

        ## find the sequence for the names or create it if needed.
        try:
            valseq = valmap[valmap.index(names)]
        except (ValueError, ):
            valseq = []
            valmap.append((names, valseq))

        ## and finally extend the sequence and return the original
        ## (now modified) function.
        valseq.extend([basetypes.get(v, v) for v in validators])
        return original

    return add_deco


def fuse(original):
    """ Decorator function to finalize the validator list and enforce calling them.

    @param original function previously decorated with the 'add' decorator
    @return replacement function that calls each validator before calling the original
    """
    ## perform this once to ensure the original function has
    ## validators at compile time.  we'll do it again below in the
    ## annotation when it's needed, but having it here will induce an
    ## exception sooner.
    get_validators(original)
    
    def enforcer_anno(*varparams, **keyparams):
        """ enforcer_anno(...) -> annotation called instead of (and before) original

        """
        orignames, origvarargs, origvarkw, origdefaults = getargspec(original)
        varparams = list(varparams)
        valid = {}
        invalid = {}

        for vkeys, validators in get_validators(original):
            idxs, vals = indexed_values(vkeys, orignames, varparams, keyparams)

            for vcall in validators:
                vcargnames, vcvarargs, vcvarkw, vcdefaults = getargspec(vcall)
                kwds = {}
                if (keys.env in vcargnames) or vcvarkw:
                    if keys.env in keyparams:
                        kwds[keys.env] = keyparams[keys.env]
                    elif keys.env in orignames:
                        kwds[keys.env] = varparams[orignames.index(keys.env)]
                try:
                    results = vcall(*vals, **kwds)
                    if len(vals) == 1:
                        results = (results, )
                except (Exception, ), exc:
                    for key in vkeys:
                        prepend_item(invalid, key, exc.args)
                else:
                    for (idx, val) in enumerate(results):
                        vals[idx] = val
                    for (idx, name), res in zip(idxs, results):
                        if idx is None:
                            keyparams[name] = res
                        else:
                            varparams[idx] = res
                        prepend_item(valid, name, results)

        ## at least one validation failed
        if invalid:
            raise ValidationError(invalid, valid)

        ## otherwise everything worked and we can call the original function
        return original(*varparams, **keyparams)

    replacement = make_annotated(original, validation_anno_template)
    replacement.func_validation_anno = enforcer_anno
    return replacement


##
# Utility to insert a value at the beginning of the list within a
# mapping.  Creates list if necessary.
#
# @param mapping dictionary-like object to modify
# @param key mapping key
# @param value value to insert
# @return None

def prepend_item(mapping, key, value):
    """ prepend_item(mapping, key, value) -> insert value at mapping[key][0]

    """
    try:
        mapping[key].insert(0, value)
    except (KeyError, ):
        mapping[key] = [value, ]


def indexed_values(keys, names, paramseq, parammap):
    """ indexed_values(...) -> returns indexes and values for named keys

    """
    indexes = []
    values = []
    for key in keys:
        try:
            index = names.index(key)
            value = paramseq[index]
        except (ValueError, ):
            index = None
            value = parammap[key]
        indexes.append((index, key))
        values.append(value)
    return indexes, values


##
# Helper to select the validator sequence from a function.
#
# @param func function with validators
# @return func.func_validators
# @exception DecorationError when func_validators not found

def get_validators(func):
    """ get_validators(func) -> returns validator mapping on func

    """
    try:
        return func.func_validators
    except (AttributeError, ):
        raise DecorationError('Function does not have validators')
