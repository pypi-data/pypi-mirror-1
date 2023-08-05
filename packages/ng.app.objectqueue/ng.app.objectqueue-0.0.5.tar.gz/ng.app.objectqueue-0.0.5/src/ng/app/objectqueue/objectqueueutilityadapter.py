### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ObjectQueueAdapter class for the Zope 3 based ng.app.objectqueue package

$Id: objectqueueutilityadapter.py 49894 2008-02-02 15:43:40Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49894 $"

from zope.component import getUtilitiesFor
from interfaces import IObjectQueue
    
def ObjectQueueUtilityAdapter(context) :
    try :
        return ( y for x,y in getUtilitiesFor(IObjectQueue, context=context) ).next()
    except StopItteration :
        raise TypeError        
