#!/usr/local/env/python
#############################################################################
# Name:         .py 
# Last Modified $Date: 2005-06-14 14:51:06 +0200 (Di, 14 Jun 2005) $ 
# $Rev: 605 $
# Last Modified by $Author: knobloch $
# Purpose:      adapter ordering a containers content 
# Maintainer:
# Copyright:    (c) 2004,2005 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
# 
##############################################################################
import unittest
from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite

from zope.interface import implements
from zope.component import adapts
from zope.component.interfaces import IFactory
from zope.app.container.interfaces import IContainer

from bebop.ordering.interfaces import IOrdering, IOrderable
from bebop.protocol import protocol

class Ordering(object):
    """
    Adapter that orders container items. Uses the IOrderable adapter to
    get positional information from the container items.
    """
    implements(IOrdering)
    protocol.adapter(IContainer)
    
    debug = False
    
    def __init__(self,context):
        """init adapter context
        >>> from bebop.ordering.tests import buildOrderingTestFolder
        >>> myfold = buildOrderingTestFolder()
        >>> mypositions = Ordering(myfold)
        >>> for n in mypositions.values():
        ...    print n.order, n.__parent__.__name__
        0 a
        1 b
        2 c
        3 d
        4 e
        5 f

        """
        self.context = context      # the container
        self._count = len(context)
        self._initOrder()
        
        
    def __len__(self):
        return len(self.context)
        
    def __getitem__(self,name):
        return self.context[name]
    
    def __setitem__(self,name,item):
        """
        Makes setitem append at the end of existing items.
        
        >>> from bebop.ordering.tests import buildOrderingTestFolder
        >>> from zope.app.folder.folder import Folder
        >>> myfold = buildOrderingTestFolder()
        >>> myOrdering = Ordering(myfold)
        
        >>> myOrdering["g"] = Folder()
        >>> tmporder = Ordering(Folder())
        >>> tmporder["a"] = Folder()
        >>> myOrdering["h"] = tmporder
        >>> for n in myOrdering.values():
        ...    print n.order, n.__parent__.__name__
        0 a
        1 b
        2 c
        3 d
        4 e
        5 f
        6 g
        7 h
        
        """
        #import pdb; pdb.set_trace()
        container = self.context
        lastposition = len(container)
        
        # got an adapter not a content item
        if IOrdering.providedBy(item):
            item = item.context
            
        container[name] = item
        ordereditem = IOrderable(item)
        ordereditem.setOrder(lastposition)
        self._refresh() # do not forget this one
        
    def _initOrder(self):
        self._items = {}
        adapted = []
        # get container content in container order
        for obj in self.context.values():
            ordereditem = IOrderable(obj)
            if not ordereditem.hasOrder():
                ordereditem.setOrder(self.next())    
            adapted.append(ordereditem)
            
        # sort by items sort method item.__cmp__
        sorted_adapters = sorted(adapted)
        
        # tell orderable items their from sorted_adapters
        runningindex = 0
        for obj in sorted_adapters:
            obj.setOrder(runningindex)
            self._items[runningindex] = obj
            runningindex += 1
  
    def next(self):
        """Returns the next available position"""
        pos = self._count
        self._count += 1
        return pos
        
    def order(self, name):
        obj = self.context.get(name)
        if obj is not None:
            return IOrderable(obj).order
        return self.next()
    
    def _refresh(self):
        """Updates the items dict from knowledge about positions."""
        for obj in self.context.values():
            ordereditem = IOrderable(obj)
            self._items[ordereditem.order] = ordereditem
            
    def _moveOne(self,positions,direction=1):
        """
        Worker method for upOne and downOne getting direction
        info by upwards = 1 and downwards = -1
        because positions can contain a non contigent list of
        selected items, the items are temporarily copied to a 
        dict in first step. Seconondly the not selected items are
        copied to tempdict to find their new places
        """
        td = {}
        # move down, exit when already at end position
        if direction == -1 and positions[-1] == len(self.context)-1:
            return
        
        for n in positions:
            # move up, exit when already at start position
            if direction == 1 and n == 0:
                return
            
            # copy selected items to their new positions in temp dict
            item = self.getItemFromPosition(n)
            td[n-(1*direction)] = item
            
        # copy the rest of the items to the open positions in tempdict
        # by searching down/upwards for free spaces in dict
        for n in range(len(self.context)):
            if n not in positions:
                tmpindex = n
                while td.has_key(tmpindex):
                    tmpindex = tmpindex + (1 * direction)
                item = self.getItemFromPosition(n)
                td[tmpindex] = item
                
        # tell the items their new position       
        for k,v in td.items():
            v.setOrder(k)
            
        # update original items dict
        self._items.update(td)
            
        self._refresh()
        
    def getItemFromPosition(self,position):   
        """
        >>> from bebop.ordering.tests import buildOrderingTestFolder
        >>> myfold = buildOrderingTestFolder()
        >>> myOrdering = Ordering(myfold)
        >>> myOrdering.getItemFromPosition(7) is None
        True
        >>> item = myOrdering.getItemFromPosition(2)
        >>> item.__parent__.__name__
        u'c'
        """
        return self._items.get(position, None)
        
    def items(self):
        return sorted(self._items.items())
    
    def values(self):
        return [v for k, v in self.items()]
    
    def keys(self):
        return sorted(self._items.keys())
    
    def getNames(self):
        """
        >>> from bebop.ordering.tests import buildOrderingTestFolder
        >>> myfold = buildOrderingTestFolder()
        >>> myOrdering = Ordering(myfold)
        >>> myOrdering.getNames()
        [u'a', u'b', u'c', u'd', u'e', u'f']

        """
        return [n.__parent__.__name__ for n in self.values()]
 
    def moveTo(self, from_pos, to_pos):
        """
        Move item from a position to a new one.
        
        >>> from bebop.ordering.tests import buildOrderingTestFolder
        >>> myfold = buildOrderingTestFolder()
        >>> myOrdering = Ordering(myfold)
        >>> myOrdering.moveTo(2, 4)
        >>> for n in myOrdering.values():
        ...    print n.order, n.__parent__.__name__
        0 a
        1 b
        2 d
        3 c
        4 e
        5 f
        """
        to_pos = max(to_pos, 0)
        if to_pos == 0:
            self.goTop([from_pos])
            return
        item = self.getItemFromPosition(from_pos)
        if to_pos > from_pos:
            item.setOrder(to_pos)
        elif to_pos < from_pos:
            item.setOrder(to_pos-1)
        self._initOrder()
        
    def goTop(self, positions):
        """
        get delta from first of selected items to top
        as move amount
        
        >>> from bebop.ordering.tests import buildOrderingTestFolder
        >>> myfold = buildOrderingTestFolder()
        >>> myOrdering = Ordering(myfold)
        >>> positions = [2]
        >>> myOrdering.goTop(positions)
        >>> for n in myOrdering.values():
        ...    print n.order, n.__parent__.__name__
        0 c
        1 a
        2 b
        3 d
        4 e
        5 f
        """
        lastposition = len(self.context)
        for k,v in self._items.items():
            if k not in positions:
                item = self.getItemFromPosition(k)
                item.setOrder(item.getOrder()+lastposition)
        self._initOrder()
        
        
    def upOne(self,positions):
        """
        >>> from bebop.ordering.tests import buildOrderingTestFolder
        >>> myfold = buildOrderingTestFolder()
        >>> myOrdering = Ordering(myfold)
        >>> positions = [1,3,4]
        >>> myOrdering.upOne(positions)
        >>> for n in myOrdering.values():
        ...    print n.order, n.__parent__.__name__
        0 b
        1 a
        2 d
        3 e
        4 c
        5 f
        """
        self._moveOne(positions,1)  
            
    def goBottom(self,positions):
        """ 
        get delta from last of selected items to bottom
        as move amount
        
        first we move first two elements to bottom
        
        >>> from bebop.ordering.tests import buildOrderingTestFolder
        >>> myfold = buildOrderingTestFolder()
        >>> myOrdering = Ordering(myfold)
        >>> positions = [0,1]
        >>> myOrdering.goBottom(positions)
        >>> for n in myOrdering.values():
        ...    print n.order, n.__parent__.__name__
        0 c
        1 d
        2 e
        3 f
        4 a
        5 b
        
        now we move two items that are not neigbours
        
        >>> myfold = buildOrderingTestFolder()
        >>> myOrdering = Ordering(myfold)
        >>> positions = [0,2]
        >>> myOrdering.goBottom(positions)
        >>> for n in myOrdering.values():
        ...    print n.order, n.__parent__.__name__
        0 b
        1 d
        2 e
        3 f
        4 a
        5 c
        """
        lastposition = len(self.context)
        for id in positions:
            item = self.getItemFromPosition(id)
            item.setOrder(item.getOrder()+lastposition)
        self._initOrder()
            
    def downOne(self,positions):
        """
        >>> from bebop.ordering.tests import buildOrderingTestFolder
        >>> myfold = buildOrderingTestFolder()
        >>> myOrdering = Ordering(myfold)
        >>> positions = [1,3,4]
        >>> myOrdering.downOne(positions)
        >>> for n in myOrdering.values():
        ...    print n.order, n.__parent__.__name__
        0 a
        1 c
        2 b
        3 f
        4 d
        5 e
        """
        self._moveOne(positions,-1)
        
        
def items(context):
    """Convenience function which returns ordered objects if possible."""
    try:
        ordering = IOrdering(context)
        return [(n.__parent__.__name__, n.__parent__) for n in ordering.values()]
    except:
        return context.items()  

