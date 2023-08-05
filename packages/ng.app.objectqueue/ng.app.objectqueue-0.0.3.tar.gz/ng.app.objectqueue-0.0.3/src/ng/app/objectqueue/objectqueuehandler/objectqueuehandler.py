### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: objectqueuehandler.py 49723 2008-01-24 23:28:18Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49723 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from ng.app.objectqueue.interfaces import IObjectQueue

def handleAdded(object, event) :
    try :
        IObjectQueue(object).itemAdd(object)
    except TypeError :
        pass

def handleModified(object, event) :
    try :
        IObjectQueue(object).itemModify(object)
    except TypeError :
        pass        


def handleRemoved(object, event) :
    try :
        IObjectQueue(object).itemRemove(object)
    except TypeError :
        pass
                
