#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to support posibility more convenient work with
interfaces

$Id: interface.py 51221 2008-07-01 08:46:18Z cray $
"""
__author__  = "Andrey Orlov"
__license__ = "GPL"
__version__ = "$Revision: 51221 $"

def _(s) : return s

from zope.interface import classImplements
from zope.interface.declarations import _implements
from sys import _getframe
from zope.schema.fieldproperty import FieldProperty
from zope.schema.interfaces import IField

def implements(*kv) :
    _implements("implements",kv,classImplements)
    for interface in kv :
        for name in interface.names(all=True) :
            if IField.providedBy(interface[name]) :
                _getframe(1).f_locals[name]=FieldProperty(interface[name])

if __name__ == '__main__' :
    print "Hit the road, jack. Please don't comeback no more"