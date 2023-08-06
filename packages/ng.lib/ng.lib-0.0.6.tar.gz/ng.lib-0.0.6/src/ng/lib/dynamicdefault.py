### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Definition of function used to generate fields with callable default
during runtime.

$Id: dynamicdefault.py 51828 2008-10-08 08:45:35Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51828 $"
 
from zope.schema import Field

class DefaultProperty(object) :
    def __set__(self,inst,default) :
        self.default = default
    
    def __get__(self,inst,unknown_shit) :
        default = self.default()
        inst.validate(default)
        return default

def DynamicDefault(field,*kv,**kw) :
    if not issubclass(field,Field) :
        raise TypeError,"field %s must be subclass of %s" % (field,Field)    
    
    class DynamicField(field) :
        default = DefaultProperty()

    return  DynamicField(*kv,**kw)

