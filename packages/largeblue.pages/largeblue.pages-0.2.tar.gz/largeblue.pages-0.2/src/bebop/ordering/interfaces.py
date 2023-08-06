#!/usr/bin/python
#############################################################################
# Name:         interfaces.py
# Purpose:      Interface definitions for annotatable orderings
# Maintainers:  Manfred Knobloch <m.knobloch@iwm-kmrc.de>
#               Uwe Oestermeier <u.oestermeier@iwm-kmrc.de>
# Copyright:    (c) iwm-kmrc.de KMRC - Knowledge Media Research Center
# License:      GPLv2
#############################################################################
__docformat__ = 'restructuredtext'

import sys

import zope.interface
import zope.schema

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bebop')


class IWriteOrderable(zope.interface.Interface):
    """Adapter to make everything contained orderable."""   

    def setOrder(position):
        """Sets the current position."""


class IReadOrderable(zope.interface.Interface):
    """Adapter to make everything contained orderable."""

    def getOrder():
        """Returns the current order position."""
        
    def hasOrder():
        """Returns True if the object is already positioned."""

        
class IOrderable(IWriteOrderable, IReadOrderable):
    """Adapter to make everything contained orderable."""

    order = zope.schema.Int(title=u'Position', 
                            min=0,
                            default=0,
                            max=sys.maxint)

    
class IReadOrdering(zope.interface.Interface):
    """Read operations for ordered containers."""
    
    def values():
        """Returns the ordered list of values of the current container."""
        
    def keys(self):
        """Return ordered list of keys of the current container."""
    
    def getNames(self):
        """Returns the ordered names (not ordered keys 1, 2, 3...)."""

        
class IOrdering(IReadOrdering):
    """Adapter to handle Orderable items in a Container."""
    
    criterion = zope.schema.Choice(
        title=_(u'Criterion'),
        description=_(u'Ordering criterion.'),
        required=False,
        vocabulary = zope.schema.vocabulary.SimpleVocabulary.fromItems(
            [(u'Userdefined', u'userdefined'),
            (u'Publication Date', u'published'),
            (u'Modification Data', u'modified'),
            (u'Creation Date', u'created'),
            (u'Alphabetically', u'alphabetically')]),
            default = u'userdefined')
    
    reversed = zope.schema.Bool(
        title=_(u'Reversed'),
        description=_(u'Reversed Ordering.'),
        required=False,
        default=False)
