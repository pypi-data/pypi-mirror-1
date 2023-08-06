from zope.interface import implements

from bebop.ordering.interfaces import IOrdering, IOrderable
from bebop.ordering.ordering import Ordering as DefaultOrdering
from bebop.protocol import protocol

from largeblue.pages.interfaces import IPage, IPageContainer


def len_sans_non_orderables(target):
    l = 0
    for obj in target.values():
        if IPage.providedBy(obj):
            l += 1
    return l


class Ordering(DefaultOrdering):
    implements(IOrdering)
    protocol.adapter(IPageContainer)
    debug = False
    def __init__(self,context):
        """
          
          We override to only count the orderable items
          
          
        """
        
        self.context = context # the container
        self._count = len_sans_non_orderables(self.context)
        self._initOrder()
    
    def __setitem__(self,name,item):
        """
          
          Again, lastpos changes to be len of self (not the container)
          
          
        """
        
        container = self.context
        lastposition = len_sans_non_orderables(container)
        
        # got an adapter not a content item
        if IOrdering.providedBy(item):
            item = item.context
            
        container[name] = item
        ordereditem = IOrderable(item)
        ordereditem.setOrder(lastposition)
        self._refresh() # do not forget this one
    
    def _initOrder(self):
        """
          
          We make sure obj is orderable
          
          
        """
        
        self._items = {}
        adapted = []
        # get container content in container order
        for obj in self.context.values():
            if IPage.providedBy(obj):
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
    
    def _refresh(self):
        """Updates the items dict from knowledge about positions."""
        for obj in self.context.values():
            if IPage.providedBy(obj):
                ordereditem = IOrderable(obj)
                self._items[ordereditem.order] = ordereditem
            
        
    
    def _moveOne(self,positions,direction=1):
        td = {}
        # move down, exit when already at end position
        if direction == -1 and positions[-1] == len_sans_non_orderables(self.context) - 1:
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
        for n in range(len_sans_non_orderables(self.context)):
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
        lastposition = len_sans_non_orderables(self.context)
        for k,v in self._items.items():
            if k not in positions:
                item = self.getItemFromPosition(k)
                item.setOrder(item.getOrder()+lastposition)
        self._initOrder()
    
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
        lastposition = len_sans_non_orderables(self.context)
        for id in positions:
            item = self.getItemFromPosition(id)
            item.setOrder(item.getOrder()+lastposition)
        self._initOrder()
    
