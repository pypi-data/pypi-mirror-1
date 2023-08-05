### -*- coding: utf-8 -*- #############################################
#######################################################################
"""handleAdded, handleModified and handleRemoved scripts for the Zope 3
based ng.app.objectqueue package

$Id: objectqueuehandler.py 50793 2008-02-21 10:53:53Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50793 $"

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
