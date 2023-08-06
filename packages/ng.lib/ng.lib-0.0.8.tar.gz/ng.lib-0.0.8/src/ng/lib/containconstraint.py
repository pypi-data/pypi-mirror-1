### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Definition of contain constraint gear

$Id: containconstraint.py 52413 2009-01-30 12:47:23Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52413 $"
 

from zope.component import subscribers
from zope.interface import implements,providedBy
from interfaces import IContainConstraint
from ng.site.addon.tag.wave.interfaces import ITagRubricAnnotationAblePropagate

class ContainConstraint(object) :
    def __init__(self,interface) :

        class A(object) :
            implements(interface)
            
        self.interface = A()
        
    def deny(self,context) :
        for item in subscribers([context,self.interface],IContainConstraint) :        
            if not item.allow :
                return False
        return True         
                
    def allow(self,context) :
        return not self.deny(context)                
             
class ContainConstraintAllow(object) :
    implements(IContainConstraint)

    allow = True
    
    def __init__(self,*kv) :
        pass
        
class ContainConstraintDeny(ContainConstraintAllow) :
    allow = False
                     