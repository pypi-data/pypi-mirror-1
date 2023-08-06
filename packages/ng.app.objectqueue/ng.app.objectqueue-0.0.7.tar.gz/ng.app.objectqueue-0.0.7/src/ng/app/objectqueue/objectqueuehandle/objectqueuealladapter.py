### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ObjectQueueAll class for the Zope 3 bases ng.app.objectqueue

$Id: objectqueuealladapter.py 51552 2008-08-30 22:45:16Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51552 $"

from ng.app.objectqueue.objectqueue import ObjectQueue
from ng.app.objectqueue.interfaces import IObjectQueueAll, IObjectQueueAnnotation, IObjectQueue
from zope.interface import implements
from zope.app.container.contained import IContained
from zope.component import getUtilitiesFor

def ObjectQueueAllAdapter(context) :
    try :
        queue = IObjectQueueAnnotation(context)
    except TypeError :
        pass
    else :
        if queue.use :
            yield queue
        
            if queue.islast :
                raise StopIteration        
        
    for objectqueue in IObjectQueueAll(IContained(context).__parent__) :
        yield objectqueue
        
def Site2ObjectQueueAllAdapter(context) :
    try :
        yield IObjectQueueAnnotation(context)
    except TypeError :
        pass
        
    for name, objectqueue in getUtilitiesFor(IObjectQueue, context=context) :
        yield objectqueue
        
    for objectqueue in IObjectQueueAll(IContained(context).__parent__) :
        yield objectqueue

def Any2ObjectQueueAllAdapter(context) :
    return []
    