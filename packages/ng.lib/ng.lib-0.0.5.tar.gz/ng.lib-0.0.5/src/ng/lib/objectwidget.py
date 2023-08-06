### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ObjectWidget for the Zope 3

$Id: smartimagewidget.py 665 2007-04-01 21:32:40Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 665 $"

from zope.app.form.browser import ObjectWidget

from zope.security.proxy import removeSecurityProxy
from zope.app.form.utility import setUpWidgets, applyWidgetsChanges

class ObjectWidget(ObjectWidget) :

  def getInputValue(self):
    ob = removeSecurityProxy(super(ObjectWidget,self).getInputValue())
    return ob

  def applyChanges(self, content):
    field = self.context
    value = field.query(content, None)
    if value is None:
        value = self.factory()

    changes = applyWidgetsChanges(self, field.schema, target=value,
                                  names=self.names)
    if changes:
        ob = removeSecurityProxy(value)
        field.set(content, ob)

    return changes

