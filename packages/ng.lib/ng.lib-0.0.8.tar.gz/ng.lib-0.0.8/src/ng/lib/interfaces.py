#! /usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to support posibility more convenient work with
interfaces

$Id: interfaces.py 52544 2009-02-11 07:54:46Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52544 $"

def _(s) : return s

from zope.interface import Interface
from zope.schema import Bool, TextLine, Tuple


class IContainConstraint(Interface) :
    allow = Bool(title=u'Flag to allow contain',default=True)

class IOrderInformation(Interface) :

    name = Tuple( title=u'Sequence of names', value_type = TextLine(default=u''))

    def dict() :
        """ Return dict numbers of names """
    
if __name__ == '__main__' :
    print "Hit the road, jack. Please don't comeback no more"
