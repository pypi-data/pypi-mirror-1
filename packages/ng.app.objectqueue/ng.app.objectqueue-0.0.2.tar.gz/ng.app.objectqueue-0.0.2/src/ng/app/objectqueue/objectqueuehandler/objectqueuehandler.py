### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: objectqueuehandler.py 49681 2008-01-23 14:17:03Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49681 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from ng.app.objectqueue.interfaces import IObjectQueue

def handleAdded(object, event) :
    try :
        IObjectQueue(event.object).itemAdd(event.object)
    except TypeError :
        pass

def handleModified(object, event) :
    try :
        IObjectQueue(object).itemModify(event.object)
    except TypeError :
        pass        


def handleRemoved(object, event) :
    try :
        IObjectQueue(object).itemRemove(event.object)
    except TypeError :
        pass
                
