#!/usr/local/env/python
#############################################################################
# Name:         cache.py
# Purpose:      thread save cache
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import time

from thread import allocate_lock

class Cache(object):
    """Thread safe cache that uses least recently accessed time to trim size """

    def __init__(self, max_size=100):
        self.writelock = allocate_lock()
        self.data = {}
        self.size = max_size

    def acquireLock(self):
        self.writelock.acquire()
        
    def resize(self):
        """ trim cache to no more than 95% of desired size """
        trim = max(0, int(len(self.data)-0.95*self.size))
        if trim:
            # don't want self.items() because we must sort list by access time
            values = map(None, self.data.values(), self.data.keys())
            values.sort()
            
            self.acquireLock()
            try :
                for val,k in values[0:trim]:
                    try :
                        del self.data[k]
                    except KeyError:
                        pass
            finally :
                self.writelock.release()    
                    
    def __delitem__(self, key):
        self.acquireLock()
        try :
            try :
                del self.data[key]
            except KeyError:
                pass
        finally :
            self.writelock.release()

    def __setitem__(self,key,val):
        if (not self.data.has_key(key) and len(self.data) >= self.size):
            self.resize()
        self.acquireLock()
        try :
            self.data[key] = (time.time(), val)
        finally :
            self.writelock.release()
            
    def __getitem__(self,key):
        """ like normal __getitem__ but updates time of fetched entry """
        val = self.data[key][1]
        self.data[key] = (time.time(),val)
        return val

    def __contains__(self, key):
        return self.data.__contains__(key)
                
    def get(self,key,default=None):
        """ like normal __getitem__ but updates time of fetched entry """
        try :
            return self[key]
        except KeyError:
            return default
            
    def values(self):
        return [v[1] for v in self.data.values()]
        
    def items(self):
        return [(pair[0], pair[1][1]) for pair in self.data.items()]

    def setdefault(self, key, value):
        try :
            return self[key]
        except KeyError :
            self[key] = value
            return value