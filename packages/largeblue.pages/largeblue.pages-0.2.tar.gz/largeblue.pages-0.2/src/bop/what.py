#!/usr/local/env/python
#############################################################################
# Name:         what
# Purpose:      Type related functions and adapters
# Maintainer:
# Copyright:    (c) 2004 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import zope.interface
from zope.app.file.interfaces import IFile
from zope.dublincore.interfaces import IZopeDublinCore
from zope.copypastemove.interfaces import IContainerItemRenamer

from bebop.protocol import protocol
import bop.shortcut
import bop.helper
import bop.shortref
import bop.html
import interfaces

fulltexts = protocol.GenericFunction('IFulltexts')
"""Returns a dict of slot, text items."""


@fulltexts.when(None)
def default_fulltexts(obj):
    name = getattr(obj, '__name__', None) or u''
    texts = dict(name=name)
    dc = IZopeDublinCore(obj, None)
    if dc is not None:
        texts['title'] = dc.title or u''
        texts['description'] = dc.description or u''
    return texts

@fulltexts.when(IFile)
def file_fulltexts(obj):
   
    texts = default_fulltexts(obj)
    try:
        texts['text'] = bop.html.fullText(obj)
    except:
        bop.helper.printTrace('Cannot create fulltext')    
    return texts


class What(protocol.Adapter):
    """An adapter for type specific infos."""
    
    zope.interface.implements(interfaces.IWhat)
    protocol.adapter(None, permission='zope.Public')

    @property
    def type(self):
        return str(self.context.__class__)
    
    @property
    def ref(self):
        return bop.shortref.ensureRef(self.context)
    
    @property
    def classname(self):
        return self.context.__class__.__name__

    @property
    def name(self):
        return getattr(self.context, '__name__', None)
        
    @property
    def title(self):
        return bop.shortcut.title(self.context)

    @property
    def description(self):
        return bop.shortcut.description(self.context)

    @property
    def fulltext(self):
        texts = fulltexts(self.context)
        if texts:
            values = []
            for key, value in sorted(texts.items()):
                values.append('%s: %s' % (key.title(), value))
            result = u'\n'.join(values)
            return result
        return u''

    @property
    def subjects(self):
        return bop.shortcut.subjects(self.context)
        
    @property
    def language(self):
        return bop.shortcut.language(self.context)

class Name(protocol.Adapter):

    def getName(self):
        return getattr(self.context, '__name__', None)
        
    def setName(self, name):
        parent = self.context.__parent__
        old_name = self.context.__name__
        renamer = IContainerItemRenamer(parent)
        renamer.renameItem(old_name, name)
        
    name = property(getName, setName)


class Title(protocol.Adapter):

    def getTitle(self):
        return bop.dc(self.context).title
        
    def setTitle(self, title):
        bop.dc(self.context).title = title or u''
        
    title = property(getTitle, setTitle)

        
class Description(protocol.Adapter):
    """An adapter for descriptions."""

    def getDescription(self):
        return bop.dc(self.context).description
        
    def setDescription(self, description):
        bop.dc(self.context).description = description or u''
        
    description = property(getDescription, setDescription)


class Subjects(protocol.Adapter):
    """An adapter for subjects, resp. topics or keywords."""
    
    def getSubjects(self):
        return bop.shortcut.subjects(self.context)
        
    def setSubjects(self, subjects):
        bop.dc(self.context).subjects = subjects

    subjects = property(getSubjects, setSubjects)

