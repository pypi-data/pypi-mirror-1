### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: objectqueueannotation.py 49001 2007-12-24 13:29:26Z antel $
"""
__author__  = "Elena Antusheva, 2007"
__license__ = "GPL"
__version__ = "$Revision: 49001 $"

from ng.app.objectqueue.objectqueue import ObjectQueue
from zope.annotation.interfaces import IAnnotations 
from ng.app.objectqueue.interfaces import objectqueuekey

def IObjectQueueAnnotable(context) :

    try :
        an = IAnnotations(context)[objectqueuekey]
    except KeyError :
        an = IAnnotations(context)[objectqueuekey] = ObjectQueue()

    return an
