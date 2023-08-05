### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: objectqueuehandler.py 49787 2008-01-29 22:36:59Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49787 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from ng.app.objectqueue.interfaces import IObjectQueueAll

def handleAdded(ob, event) :
    for queue in IObjectQueueAll(ob) :
        queue.handleAdded(ob)
        
def handleModified(ob, event) :
    for queue in IObjectQueueAll(ob) :
        queue.handleModified(ob)

def handleRemoved(ob, event) :
    for queue in IObjectQueueAll(ob) :
        queue.handleRemoved(ob)
                
