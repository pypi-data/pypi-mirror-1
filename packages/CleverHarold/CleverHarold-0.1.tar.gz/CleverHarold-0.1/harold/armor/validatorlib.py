#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# A library of ready-to-use validators for Harold.
#
# Synopsis
# --------
# Don't use this module yet; I'm not particularly happy with it in
# it's present state.
#
##
from re import match, sub
from string import ascii_letters, digits, punctuation


def min_len(minv):
    """ min_len(minv) -> returns function for checking string min len

    """
    def check(value):
        if len(value) >= minv:
            return value
        else:
            raise ValueError('Value too short')
    return check


def max_len(maxv):
    """ max_len(maxv) -> returns function for checking string max len

    """
    def check(value):
        if len(value) <= maxv:
            return value
        else:
            raise ValueError('Value too long')
    return check


def bound_len(minv, maxv):
    """ bound_len(minv, maxv) -> returns function for checking value length

    """
    minc = min_len(minv)
    maxc = max_len(maxv)
    def check(value):
        minc(value)
        maxc(value)
        return value
    return check


def all_not_in(seq):
    """ all_not_in(seq) -> returns function to ensure values are not in seq

    """
    def check(value):
        for token in seq:
            if token in value:
                raise ValueError('Value not safe')
        return value
    return check


def all_in(seq):
    """ all_in(seq) -> returns function to ensure values are in seq

    """
    def check(value):
        for token in value:
            if token not in seq:
                raise ValueError('Value not safe')
        return value
    return check


safe_sniff = all_not_in( list(punctuation) )
alphanum_only = all_in( list(digits) + list(ascii_letters) )


def is_formatted(pat):
    """ is_formatted(pat) -> returns function to ensure value matches pattern

    """
    def check(name):
        if match(pat, name):
            return name
        else:
            raise ValueError('Value does not match pattern')
    return check
    

host_pat = (r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}'
             '[a-zA-Z0-9])?\.)*[a-zA-Z0-9]'
             '([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
           )


smtp_pat = (r'^([a-zA-Z0-9_\-\.]+)@'
             '((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|'
             '(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|'
             '[0-9]{1,3})(\]?)$'
           )


hostname_formatted = is_formatted(host_pat)
email_formatted = is_formatted(smtp_pat)


def html_escape(html):
    """ remove html entities from html

    """
    html = html.replace('&', '&amp;') # Must be done first!

    #thump # characters not preceded by & (does not match &#nnn; )
    #html = sub(  '(?<!\&)#', '&38;', html)
    #thump & chars
    #html = sub(  '&(?!#\d{2,3};)', '&#35;', html)

    html = html.replace('<', '&lt;')
    html = html.replace('>', '&gt;')
    html = html.replace('"', '&quot;')

    #html = html.replace('#', '&#35;') # broken
    #html = html.replace('&', '&#38;') # broken
    html = html.replace('(', '&#40;')
    html = html.replace(')', '&#41;')

    return html


def is_int(value):
    try:
        return int(value)
    except:
        raise ValueError('Not valid integer')
