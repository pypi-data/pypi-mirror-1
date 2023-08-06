### -*- coding: utf-8 -*- #############################################
#######################################################################
"""handleAdded, handleModified and handleRemoved scripts for the Zope 3
based ng.app.objectqueue package

$Id: objectqueuehandler.py 53356 2009-06-30 12:38:56Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 53356 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from ng.app.objectqueue.interfaces import IObjectQueueAll
from zope.proxy import removeAllProxies

def handleAdded(ob, event) :
    for queue in IObjectQueueAll(ob) :
        queue.handleAdded(ob)

def handleModified(ob, event) :
    for queue in IObjectQueueAll(ob) :
        queue.handleModified(ob)

def handleRemoved(ob, event) :
    for queue in IObjectQueueAll(ob) :
        queue.handleRemoved(ob)

def handleMoved(ob, event) :
    if event.oldParent is not None and event.newParent is not None :
        df = dict([ (removeAllProxies(x),x) for x in IObjectQueueAll(event.oldParent) ])
        dt = dict([ (removeAllProxies(x),x) for x in IObjectQueueAll(event.newParent) ])

        sf = set(df.keys()) 
        st = set(dt.keys()) 
        
        for queue in sf - st :
            df[queue].handleRemoved(ob)
            
        for queue in st - sf :
            dt[queue].handleAdded(ob)
        