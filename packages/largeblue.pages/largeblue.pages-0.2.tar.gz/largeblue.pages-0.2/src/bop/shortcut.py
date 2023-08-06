#!/usr/local/env/python
#############################################################################
# Name:         bop
# Purpose:      Useful shortcuts
# Maintainer:
# Copyright:    (c) 2004 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'
"""This module contains useful shortcuts which reduce
the number of imports and difficult to remember module paths.
"""
import sys, locale, thread

import zope.component
import zope.interface
import zope.lifecycleevent
import zope.app.intid

from zope.app.file import File as ZopeAppFile
from zope.app.folder import Folder
from zope.dublincore.interfaces import IZopeDublinCore
from zope.annotation.interfaces import IAnnotatable
from zope.publisher.browser import BrowserView
from zope.app.container.interfaces import INameChooser
from zope.app.container.interfaces import IWriteContainer
from zope.app.container.interfaces import IContained
from zope.traversing.interfaces import IPhysicallyLocatable
from zope.location.interfaces import ISublocations
from zope.app.catalog.interfaces import ICatalog
from zope.i18nmessageid import MessageFactory
from zope.copypastemove.interfaces import IContainerItemRenamer

# genuine shortcuts defined by imports

from zope.app.zapi import getRoot as root
from zope.app.zapi import getPath as path
from zope.security.interfaces import Unauthorized

from zope.security.proxy import removeSecurityProxy as unsecure
from zope.component import getUtility as get
from zope.component import queryUtility as query
from zope.component import getAllUtilitiesRegisteredFor as all

# basic event handling
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent as CreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent as ModifiedEvent
from zope.lifecycleevent import ObjectCopiedEvent as CopiedEvent
from zope.lifecycleevent import Attributes, Sequence

from bebop.protocol.protocol import GenericFunction, Adapter
from bebop.protocol.protocol import adapter, utility, subscriber
from bebop.protocol.protocol import implements, require, allow, factory
from bebop.protocol import browser

import interfaces
defaultLanguage = '?'

dc = IZopeDublinCore

def File(*args, **kw):
    bopfile = zope.component.queryUtility(interfaces.IBopFileFactory)
    if bopfile is not None:
        return bopfile(*args, **kw)
    else:
        return ZopeAppFile(*args, **kw)    

def all(iface, context=None):
    """Returns all registered utilites for a given interface."""
    sm = zope.component.getSiteManager(context)
    return sm.getAllUtilitiesRegisteredFor(iface)
    
def adapt(iface=zope.interface.Interface, object=None, multi=None, name=''):
    """A shortcut for a queryMultiAdapter call:
        
        bop.adapt(IFace, a)  <=> IFace(obj, None)
        bop.adapt(IFace, multi=(a, b)) <=> queryMultiAdapter((a, b), IFace)
    
    """
    if multi is not None:
        return zope.component.queryMultiAdapter(multi, iface, name=name)
    return zope.component.queryAdapter(object, iface, name=name)
        
def parent(obj):
    """Returns the parent of an object or None.
    
    Uses duck typing to ensure that a value is returned.
    """
    return getattr(obj, '__parent__', None)
    
def parents(obj):
    """Iterates over parents, parents of parents etc."""
    p = getattr(obj, '__parent__', None)
    while p is not None:
        yield p
        p = getattr(p, '__parent__', None)
        
def site(context):
    """Returns the nearest site for a given object."""
    return IPhysicallyLocatable(context).getNearestSite()

def catalog(context, name='bebop.model.catalog'):
    """Returns the nearest catalog for a given object.
    
    Uses the bebop.model.catalog as a default catalog.
    """
    return query(ICatalog, context=context, name=name)
    
def sublocations(context, recursively=False):
    """Yields the sublocations of an object.
    
    If `recursively` is true all sublocations of sublocations are also 
    yielded.
    
    """
    subs = ISublocations(context, None)
    if subs is not None:
        for sub in subs.sublocations():
            yield sub
            if recursively:
                for s in sublocations(sub):
                    yield s

def threadid():
    """Returns the id of the current thread."""
    return thread.get_ident()
    
def intid(obj):
    """Returns the nearest int id utility for an object."""
    utility = get(zope.app.intid.interfaces.IIntIds, context=obj)
    return utility.register(obj)  
   
def intid2obj(uid, context):
    """Returns the object that corresponds to an int id."""
    utility = get(zope.app.intid.interfaces.IIntIds, context=context)
    return utility.getObject(uid)
 
def modify(obj, schema=None, **kw):
    """Modifies the given schema fields of an object.
    
    Throws a modification event with descriptions of the changed attributes.
    If schema is None the attributes are modified directly and
    a unspecific modification event is thrown.
    """
    if schema is None:
        for key, value in kw.items():
            setattr(obj, key, value)
        notify(ModifiedEvent(obj))
    else:
        for key, value in kw.items():
            field = schema[key]
            field.set(obj, value)
        notify(ModifiedEvent(obj,
            Attributes(schema, *kw.keys())))
    

name = GenericFunction('bop.shortcuts.IName')
name.__doc__ = u"""Returns the name of an object."""

@name.when(zope.interface.Interface)
def default_name(obj):
    if hasattr(obj, '__name__'):    # duck typing test
        return obj.__name__
    if hasattr(obj, '_v_name'):     # test for a volatile name
        return obj._v_name    
    return u'Unnamed'
    
title = GenericFunction('bop.shortcuts.ITitle')

@title.when(zope.interface.Interface)
def default_title(obj):
    """Returns the ZopeDublinCore title or the name.
    
    Returns the class name if the name starts with '++'
    since the user shouldn't see Zope namespace markers
    in titles for site managers, annotations, comments, etc.
    
    """
    if hasattr(obj, 'title'):
        return obj.title
    
    def ersatz(obj):
        n = name(obj) or u''
        if n.startswith('++'):
            return obj.__class__.__name__
        return n
        
    dc = IZopeDublinCore(obj, None)
    if dc is not None:
        return dc.title or ersatz(obj)
    return ersatz(obj)

description = GenericFunction('bop.shortcuts.IDescription')

@description.when(zope.interface.Interface)
def default_description(obj, default=u""):
    """Returns the ZopeDublinCore description or an empty string."""
    dc = IZopeDublinCore(obj, None)
    if dc is not None:
        return dc.description
    return u''

subjects = GenericFunction('bop.shortcuts.ISubjects')

@subjects.when(zope.interface.Interface)
def default_subjects(obj, default=None):
    """Returns the ZopeDublinCore description or None."""
    dc = IZopeDublinCore(unsecure(obj), None)
    if dc is not None:
        return dc.subjects
    return None
   
def languageSuffix(obj):
    name = getattr(obj, '__name__', None)
    if name and  '.' in name:
        suffix = ''
        prefix = name.split('.')[0]
        if '_' in prefix:
            suffix = prefix.split('_')[-1].lower()
        if '-' in prefix:
            suffix = prefix.split('-')[-1].lower()
        if suffix in locale.locale_alias:
            return str(suffix)
    return None

language = GenericFunction('bop.shortcuts.ILanguage')
@language.when(None)
def default_language(obj):
    """Returns the ZopeDublinCore language or '?' for unknown."""        
    dc = IZopeDublinCore(unsecure(obj), None)
    if dc is not None:
        return dc.language or languageSuffix(obj) or defaultLanguage #'?'
    return languageSuffix(obj) or defaultLanguage #'?'
    

def settitle(obj, title, maxlen=None):
    """Sets the title."""
    if maxlen is not None and len(title)>maxlen:
        title = unicode(title[:maxlen]+u"...")
    else:
        title = unicode(title)
    dc = IZopeDublinCore(obj)
    dc.title = title

def setname(obj, name):
    """Sets the name or renames an item."""
    if IContained.providedBy(obj):
        container = parent(obj)
        if container is None:
            obj.__name__ = name
        else:
            oldName = obj.__name__
            IContainerItemRenamer(container).renameItem(oldName, name)   
    else:
        obj._v_name = name
        
def ensure(container, name, factory):
    """Ensures the existance of an object within a container."""
    if name in container:
        return container[name]
    return add(container, name, factory())
    
    
add = GenericFunction('bop.shortcuts.IAdd')

@add.when(IWriteContainer, None, None)
def default_add(container, name, obj):
    """Adds an object to a container and fires all necessary events.
    
    Uses the class name of the object for the name chooser if no name is provided.
    Returns the added object. 
    """
    if name is None:
        name = obj.__class__.__name__
    
    chooser = INameChooser(container)
    name = chooser.chooseName(name, obj)
    return default_insert(container, name, obj)

insert = GenericFunction('bop.shortcuts.IInsert')

@insert.when(IWriteContainer, None, None)
def default_insert(container, name, obj):
    """Inserts a new item to a container and fires all necessary events.
    
    Raises a duplication error if the object already exists.
    
    Uses the class name of the object for the name chooser if no name is provided.
    Returns the added object. 
    """
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
    container[name] = obj
    contained = container[name]
    zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(contained))
    return contained

attachments = GenericFunction('bop.shortcuts.IAttachments')

@attachments.when(None)
def default_attachments(obj):
    return ()
    
comments = GenericFunction('bop.shortcuts.IComments')

@comments.when(None)
def default_comments(obj):
    return ()
    
class TrustedAdapter(object):
    """A convenience base class for trusted adapters."""
    
    def __init__(self, context):
        self.context = unsecure(context)

    