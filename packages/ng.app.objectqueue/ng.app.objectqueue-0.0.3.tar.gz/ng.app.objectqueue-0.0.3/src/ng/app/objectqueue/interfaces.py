### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based objectqueue package

$Id: interfaces.py 49723 2008-01-24 23:28:18Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 49723 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Int, Choice
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.schema.vocabulary import SimpleVocabulary
from zope.app.container.interfaces import IReadContainer

class IObjectQueueHandler(Interface) :
    
    def itemAdd(ob) :
        """ Add object into queue
        """

    def itemRemove(ob) :
        """ Remove object from queue
        """

    def itemModify(ob) :
        """ Modufy object in queue
        """




class IObjectQueueDataAdd(Interface) :

    maxlen = Int(
        title=u"Maximum Length",
        description=u"maximum length of queue",
        default=10,
        )

    style = Choice(
        title=u'Style',
        description=u"Style of queue",
        vocabulary = SimpleVocabulary.fromValues([u"fifo", u"lifo"]),
        default=u"fifo",
        required=True,
        )
    
    #condition

    order = Choice(
        title=u'Order',
        description=u"Order",
        vocabulary = SimpleVocabulary.fromValues([u"straight", u"reverse"]),
        default=u"straight",
        required=True,
        )


class IObjectQueueData(IObjectQueueDataAdd) :
    
    length  = Int(
        title=u"Length",
        description=u"Current length of queue",
        default=0,
        readonly=True,
        )


class IObjectQueue(IObjectQueueHandler, IObjectQueueData, IReadContainer):
    pass

class IObjectQueueAble(Interface) :
    """ Interface of objects that can be queued
    """

