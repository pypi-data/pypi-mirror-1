from persistent import Persistent 
from zope.interface import implements 

from interfaces import IGreetable 

class World(Persistent): 
    implements(IGreetable) 

    def name(self): 
        return "world"
