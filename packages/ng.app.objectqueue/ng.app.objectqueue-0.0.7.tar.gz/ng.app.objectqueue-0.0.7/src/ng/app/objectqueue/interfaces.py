### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based objectqueue package

$Id: interfaces.py 51552 2008-08-30 22:45:16Z cray $
"""
__author__  = "Yegor Shershnev & Elena Antusheva, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51552 $"
 
from zope.interface import Interface

from zope.schema import Text, TextLine, Field, Bool, Datetime, Int, Choice
from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.schema.vocabulary import SimpleVocabulary
from zope.app.container.interfaces import IReadContainer

class IObjectQueueHandle(Interface) :
    
    def handleAdded(ob) :
        """ Add object into queue
        """

    def handleRemoved(ob) :
        """ Remove object from queue
        """

    def handleModified(ob) :
        """ Modufy object in queue
        """

class IObjectQueueDataAdd(Interface) :

    maxlen = Int(
        title=u"Maximum Length",
        description=u"maximum length of queue",
        default=20,
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

    use = Bool(
        title=u'Queue is on',
        description=u'Queue used to store changed items',
        default=True
        )
        
    islast = Bool(
        title=u'Queue is last',
        description=u'Treatment will be stop on this queue by the up way',
        default=False
        )
        
    usemodify = Bool(
        title=u'Handle modify event',
        description=u'Modify event on object will be handled by queue',
        default=True
        )            

class IObjectQueueData(IObjectQueueDataAdd) :
    
    length  = Int(
        title=u"Length",
        description=u"Current length of queue",
        default=0,
        readonly=True,
        )


class IObjectQueueAvailable(Interface) :
    pass


class IObjectQueueAnnotable(IObjectQueueAvailable) :
    pass


class IObjectQueueUtilitable(IObjectQueueAvailable) :
    pass


class IObjectQueue(IObjectQueueHandle, IObjectQueueData, IReadContainer, IObjectQueueAnnotable):
    pass


class IObjectQueueAnnotation(IObjectQueue) :
    pass


class IObjectQueueUtility(IObjectQueue) :
    pass


class IObjectQueueAll(Interface) :
    """ Enumerator for all ObjectQueue Utilities """

    def next() :
        pass 

    def __iter__() :
        pass


class IObjectQueueUtilities(Interface) :
    """ Enumerator for all ObjectQueue Utilities """

    def next() :
        pass 

    def __iter__() :
        pass


class IObjectQueueAble(Interface) :
    """ Interface of objects that can be queue"""
 
objectqueuekey="ng.app.objectqueue.objectqueue.ObjectQueue"
