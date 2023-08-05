### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 49016 2007-12-25 08:57:10Z antel $
"""
__author__  = "Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49016 $"
 
from zope.interface import Interface

class IObjectQueueAnnotable(Interface) :
    pass

objectqueuekey="ng.app.objectqueue.objectqueue.ObjectQueue"

