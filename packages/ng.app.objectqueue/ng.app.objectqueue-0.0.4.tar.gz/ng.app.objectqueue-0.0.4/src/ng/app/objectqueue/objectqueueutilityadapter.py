### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ObjectQueueAdapter class for the Zope 3 based ng.app.objectqueue package

$Id: objectqueueutilityadapter.py 49787 2008-01-29 22:36:59Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49787 $"

from zope.component import getUtilitiesFor
from interfaces import IObjectQueue
    
def ObjectQueueUtilityAdapter(context) :
    try :
        return ( y for x,y in getUtilitiesFor(IObjectQueue, context=context) ).next()
    except StopItteration :
        raise TypeError        
