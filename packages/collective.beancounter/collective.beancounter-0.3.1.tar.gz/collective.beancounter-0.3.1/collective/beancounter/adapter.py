# -*- coding: utf-8 -*-
#
# File: skeleton.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__    = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__  = "$Revision: 53835 $"
__version__   = '$Revision: 53835 $'[11:-2]

from zope import interface

from collective.beancounter.interfaces import IBeanCounter, IBeanCounterFieldFilter


def null_filter(dummy):
    return True


def countable_fields(content):
    schema = content.Schema()
    field_filter = IBeanCounterFieldFilter(content, null_filter)
    return filter( field_filter, schema.fields())

def count_schema_fields(content):
    schema = content.Schema()
    return len(countable_fields(schema))

def filled_fields(content):
    l = countable_fields(content)
    return [f.getName() for f in l if f.get(content)]

def empty_fields(content):
    l = countable_fields(content)
    return [f.getName() for f in l if not f.get(content) ]

class ATBeanCounter(object):
    interface.implements(IBeanCounter)

    def __init__(self,context):
        self.context = context

    @property
    def percentage(self):
        nr = len(countable_fields(self.context))
        filled = len(filled_fields(self.context))
        return ((filled*1.0) / (nr*1.0)) * 100.0

class ATFieldFilter(object):
    """
    Filter out fields which:
      - are not user settable
      - are not in the "default" schemata
      - are not in the special plone field blacklist
      - are not boolean fields (these are true or false, i.e. always "filled")
    """
    interface.implements(IBeanCounterFieldFilter)

    PLONE_FIELDS="constrainTypesMode locallyAllowedTypes immediatelyAddableTypes".split()
    FIELD_BLACKLIST="BooleanField"

    def __init__(self,context):
        self.context = context

    def __call__(self, f):
        return f.schemata == "default" and f.mode == "rw" and f.getName() not in self.PLONE_FIELDS and f.__class__.__name__ not in self.FIELD_BLACKLIST


# vim: set ft=python ts=4 sw=4 expandtab :
