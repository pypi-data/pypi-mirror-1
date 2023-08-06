### -*- coding: utf-8 -*- #############################################
#######################################################################
"""ObjectQueue class for the Zope 3 based objectqueue package

$Id: objectqueue.py 51552 2008-08-30 22:45:16Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51552 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from persistent import Persistent
from interfaces import IObjectQueue, IObjectQueueData
from persistent.list import PersistentList
from zope.app.zapi import getUtility
from zope.app.intid.interfaces import IIntIds
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IContained

class ObjectQueue(Persistent,Contained) :
    """ ObjectQueue class represent queue of last modified objects
    """

    implements(IObjectQueue,IContained)

    _maxlen = 10
    
    style = u"fifo"
    
    order = u"reverse"
    
    length = 0

    use = True
    
    islast = False
    
    usemodify = True

    def __init__(self, *kv, **args) :
        super(ObjectQueue, self).__init__(self, *kv, **args)
        self.queue = PersistentList()

    def __getitem__(self, key) :
        """ Get element of queue by id
        """
        if key not in self.queue:
            raise KeyError

        return getUtility(IIntIds,context=self).getObject(int(key))

    def __len__(self) :
        return len(self.queue)

    def __contains__(self, key) :
        return key in self.keys()

    def _setmaxlen(self, value) :
        if self.order == u"straight" :
            self.queue = self.queue[:value]
        elif self.order == u"reverse" :
            self.queue = self.queue[-value:]
        self._maxlen = value
    
    def _getmaxlen(self) :
        return self._maxlen

    maxlen = property(_getmaxlen, _setmaxlen, u"Maximum length of queue")

    @property
    def length(self) :
        return len(self)
    
    def get(self, key, default=None) :
        try :
            return self[key]
        except KeyError :
            return default

    def keys(self) :
        """ Return the keys of the queue
        """
        return [x for x in self.queue]

    def items(self) :
        """ Returns queued elements as list of tuples (key, value)
        """
        return [ (x,self[x]) for x in self.keys() ]

    def __iter__(self) :
        return (x for x in self.queue)

    def values(self) :
        """ Return objects associated with elements in queue
        """
        return [ y for x,y in self.items()]
    
    def handleAdded(self, ob) :
        """ Add a key of object into queue
        """        
        try :
            uid = str(getUtility(IIntIds, context=ob).getId(ob))
        except (KeyError), msg :
            print "Can't add",ob,"because of", msg
        else :
            order = self.order
            style = self.style
            maxlen = self.maxlen
            
            if style == u"fifo" and order == u"straight" :
                self.queue.insert(0, uid)
                if len(self) >= maxlen :
                    self.queue.pop()
            elif style == u"fifo" and order == u"reverse" :
                self.queue.append(uid)
                if len(self) >= maxlen :
                    self.queue.remove(self.queue[0])
            elif style == u"lifo" and order == u"straight":
                if len(self) >= maxlen :
                    self.queue.pop()
                self.queue.append(uid)
            elif style == u"lifo" and order == u"reverse" :
                if len(self) >= maxlen :
                    self.queue.remove(self.queue[0])
                self.queue.insert(0, uid)
                
    def handleRemoved(self, ob) :
        """ Remove object from queue
        """
        try :
            uid = str(getUtility(IIntIds, context=ob).getId(ob))
        except (ValueError,KeyError), msg :
            print "Can't remove",ob,"because of",msg
        else :
            if uid not in self.keys():
                return
            self.queue.remove(uid)
        
    def handleModified(self, ob) :
        """ Modufy object in queue
        """
        if self.usemodify: 
            self.handleRemoved(ob)
            self.handleAdded(ob)
