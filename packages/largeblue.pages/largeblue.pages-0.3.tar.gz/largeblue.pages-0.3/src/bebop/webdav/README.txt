Bebop WebDAV
============

Besides patching PUT and PROPFIND this package also supports locking.
We need a working interaction and participation to test the lock function:

    >>> import zope.interface
    >>> import zope.security.interfaces
    >>> class DemoPrincipal(object):
    ...     zope.interface.implements(zope.security.interfaces.IPrincipal)
    ...     def __init__(self, id, title=None, description=None):
    ...         self.id = id
    ...         self.title = title
    ...         self.description = description
    ...
    >>> joe = DemoPrincipal('joe')
    >>> import zope.security.management
    >>> class DemoParticipation(object):
    ...     zope.interface.implements(zope.security.interfaces.IParticipation)
    ...     def __init__(self, principal):
    ...         self.principal = principal
    ...         self.interaction = None
    ...
    >>> zope.security.management.endInteraction()
    >>> zope.security.management.newInteraction(DemoParticipation(joe))

    >>> root = getRootFolder()

Since locking is accompanied by events we will look at the notifications:

    >>> import zope.event
    >>> zope.event.subscribers.append(printEvent)
    
The lock function returns an exclusive lock:

    >>> from bebop.webdav import locking
    >>> token = locking.lock(root)
    Event log: TokenStartedEvent unnamed
    >>> token
    <zope.locking.tokens.ExclusiveLock object at ...>
    
After locking we can ask for the token and the owner:

    >>> locking.get(root) == token
    True
    
    >>> locking.owner(root)
    ['joe']
    
Removing the lock leads to the initial state:

    >>> locking.unlock(root)
    Event log: TokenEndedEvent unnamed

    >>> locking.get(root) is None
    True
    >>> locking.owner(root) is None
    True
    
Clean up:

    >>> zope.event.subscribers.remove(printEvent)