### -*- coding: utf-8 -*- #############################################
#######################################################################
"""QuotaAdapter class for the Zope 3 based ng.app.objectqueue package

$Id: objectqueueutilities.py 50793 2008-02-21 10:53:53Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 50793 $"


from zope.component import getUtilitiesFor
from interfaces import IQuota


class QuotaAdapter(object) :

    def __init__(self,context) :
        self.context = context
        self.quotas = [ y for x,y in getUtilitiesFor(IQuota, context=context) ]

    def handleAdded(self,ob): 
        for quota in self.quotas :
            quota.handleAdded(ob)

    def handleModified(self,ob): 
        for quota in self.quotas :
            quota.handleModified(ob)
 
    def handleRemoved(self,ob): 
        for quota in self.quotas :
            quota.handleRemoved(ob)
