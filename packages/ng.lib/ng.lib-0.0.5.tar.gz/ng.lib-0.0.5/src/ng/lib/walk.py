### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Walk Zope3 a different way

$Id: smartimagewidget.py 665 2007-04-01 21:32:40Z cray $
"""
__author__  = "Andrey Orlov,2008"
__license__ = "GPL"
__version__ = "$Revision: 665 $"

from zope.app.container.interfaces import IReadContainer

class WalkTreeBase(object) :
    """ Base walk tree do nothing """
    def __init__(self,ob,function = lambda x : x) :
        self.queue = [ob]
        self.function = function

    def __iter__(self) :
        while self.queue :
            ob = self.queue.pop()
            yield self.function(ob)
            if IReadContainer.providedBy(ob) :
                for x in ob.values() :
                    self.push(x)
                    
    def push(self,ob) :
        raise TypeError,"Push operation is not correctly defined"

    def __len__(self) :
        return len(self.queue)

class BFSWalkTree(WalkTreeBase) :
    """ Do Breadth-first search """
    
    def push(self,ob) :
        self.queue.insert(0,ob)

class DFSWalkTree(WalkTreeBase) :
    """ Do Depth-first search """
    
    def push(self,ob) :
        self.queue.append(ob)

        