### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QueueUtility adapter for the Zope 3 based objectqueue package

$Id: queueutility.py 49723 2008-01-24 23:28:18Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49723 $"

from zope.app.zapi import getUtility
from ng.app.objectqueue.interfaces import IObjectQueue
from zope.component import ComponentLookupError

def QueueUtility(ob) :
    try :
        return getUtility(IObjectQueue, context=ob)
    except ComponentLookupError :
        print "\nCannot get utility with IObjectQueue interface\n"
