#!/usr/local/env/python
#############################################################################
# Name:         interfaces.py 
# Last Modified $Date: 2005-06-14 14:51:06 +0200 (Di, 14 Jun 2005) $ 
# $Rev: 605 $
# Last Modified by $Author: knobloch $
# Purpose:      Provide interface and class for ordered items
# Maintainer:
# Copyright:    (c) 2004,2005 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
# 
##############################################################################
import unittest
from persistent import Persistent
from zope import annotation
from zope import component
from zope import event
from zope import lifecycleevent

from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite

from zope.interface import implements
from zope.component import adapts
from zope.app.container.interfaces import IContained
from zope.location.interfaces import ILocation
from zope.annotation.interfaces import (IAttributeAnnotatable, IAnnotations, 
                                        IAnnotatable)
from zope.annotation.attribute import AttributeAnnotations
from zope.schema.fieldproperty import FieldProperty

from bebop.ordering.interfaces import IOrderable
from bebop.protocol import protocol

import bop.annotation

class Orderable(Persistent):
    """Makes annotatable objects orderable.

    >>> from zope import component
    >>> class my(Persistent):
    ...    implements(IAttributeAnnotatable,IContained)
    ...    def __init__(self,content):
    ...       self.content = content

    >>> s = my("one")
    
    Now the object is orderable:
    
    >>> oi = IOrderable(s)
    >>> other = my("another")
    >>> other = IOrderable(other)
    >>> other.setOrder(3)
    >>> oi.setOrder(2)
    >>> oi.getOrder()
    2
    >>> for x in sorted([other,oi]):
    ...    print x.__parent__.content
    one
    another
    >>> oi.setOrder(0)

    """
    implements(IOrderable, ILocation)
    component.adapts(IContained)
    protocol.require(IOrderable,permission="zope.View")

#    _order = FieldProperty(IOrderable['order'])
    _order = 0
    __parent__ = None
            
    def getOrder(self):
        """Getter for order """    
        return self._order
            
    def __cmp__(self,other):
        """Compare method for adapter """
        return self._order.__cmp__(other._order)
            
    def setOrder(self, orderposition=0):
        """Setter for orderposition. Avoids unnecssary _p_changed marks."""
        if self._order != orderposition :
            self._order = orderposition
                
    order = property(getOrder, setOrder)
    
    def hasOrder(self):
        return '_order' in self.__dict__
    
    # BBB code
    @property
    def context(self):
        return self.__parent__

OrderableFactory = bop.annotation.factory(Orderable)

def test_suite():
    return unittest.TestSuite((
        DocTestSuite(),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
