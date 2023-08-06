#A module that uses the adapter protocol
import zope.interface
from bebop.protocol import protocol

import interfaces

class SampleAdapter(object):
    zope.interface.implements(interfaces.ISample)
    protocol.adapter(zope.interface.Interface)
    
class NamedSampleAdapter(object):
    zope.interface.implements(interfaces.ISample)
    protocol.adapter(zope.interface.Interface, name='demo')

class SampleMultiAdapter(object):
    zope.interface.implements(interfaces.ISample)
    protocol.adapter(str, int)
    
class TrustedAdapter(object):
    zope.interface.implements(interfaces.ISample)
    protocol.adapter(dict, trusted=True)
    
    