#A module that uses the subscriber protocol
import zope.interface
from bebop.protocol import protocol

import interfaces

class SampleEvent(object):
    zope.interface.implements(interfaces.ISampleEvent)
    
@protocol.subscriber(interfaces.ISampleEvent)
def sampleSubscriber(event):
    print "sampleEventSubscriber called"
    
