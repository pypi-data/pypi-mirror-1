#!/usr/local/env/python
#############################################################################
# Name:         locking.py
# Purpose:      Convenience functions for WebDAV locks
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################


import zope.locking.interfaces
from zope.app.keyreference.interfaces import IKeyReference

def lock(obj):
    broker = zope.locking.interfaces.ITokenBroker(obj, None)
    if broker is not None:
        return broker.lock()

def get(obj):
    broker = zope.locking.interfaces.ITokenBroker(obj, None)
    if broker is not None:
        try:
            keyreference = IKeyReference(obj, None)
            if keyreference is not None:
                return broker.get()
        except zope.app.keyreference.interfaces.NotYet:
            pass

def unlock(obj):
    token = get(obj)
    if token is not None:
        return token.end()

def owner(obj):
    try:
        token = get(obj)
        if token is not None:
            return sorted(token.principal_ids)
    except TypeError:   # not lockable
        return None