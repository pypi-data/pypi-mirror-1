### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Open ID authenticator class (use IProfileAnnotation)

$Id: orderinformation.py 52238 2008-12-28 23:27:58Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52238 $"

from zope.interface import Interface, implements
from interfaces import IOrderInformation
from zope.cachedescriptors.property import Lazy

class OrderInformation(object) :
    implements(IOrderInformation)
    name = []

    def __init__(self,*kw) :
        pass
    
    @Lazy
    def dict(self) :
        def a(a=[0]) :
            a[0] += 1
            return a[0]
            
        return dict(((x,a()) for x in self.name))
