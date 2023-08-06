#!/usr/local/env/python
#############################################################################
# Name:         interfaces.py
# Purpose:      Permanent human readable object references
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import zope.interface
import zope.schema
from zope.component.interfaces import IFactory
from zope.app.container.interfaces import (IContainer, IContained, 
                                           IReadContainer, IWriteContainer)
from zope.app.file.interfaces import IFile
from zope.app.folder.interfaces import IFolder
from zope.annotation.interfaces import IAttributeAnnotatable

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('bebop')


class IBopFileFactory(IFactory):
    """Factory for the default file implementation used by bop.File"""


class InvalidShortRef(Exception):
    pass


class IShortRef(zope.interface.Interface):
    """The permanent id of an object.
    
    Ids look as follows: 'file1', 'file2', 'file3', 'folder1', ...
    """
    
    
class IShortRefs(zope.interface.Interface):
    """This utility provides a two way mapping between objects and
    permanent ids for each involved object class name.
    """

    def split(self, id):
        """Splits an id in the name and integer parts."""
        
    def getObject(self, id):
        """Returns the object."""

    def queryObject(self, id, default=None):
        """Returns the object or the default value."""
        
    def getId(self, ob):
        """Returns the id of the obj."""
        
    def queryId(self, ob, default=None):
        """Returns the id or the default value."""
        
    def register(self, ob):
        """Registers the object and generates a new id."""
        
    def unregister(self, ob):
        """Removes the object."""

        
class IMembers(zope.interface.Interface):
    """A mapping of members.
    
    Values must be of type IMember. 
    """

    
class IMember(zope.interface.Interface):
    """A single member."""
    
    email = zope.schema.TextLine(
        title=_(u'Mail'),
        description=_(u'The main mail address'),
        required=False,
        readonly=True)

    name = zope.schema.TextLine(
        title=_(u'Fullname'),
        description=_(u'The name of the member'),
        required=False,
        readonly=True)
        
    principal_id = zope.schema.TextLine(
        title=_(u'Principal Id'),
        description=_(u'The principal id'),
        required=False,
        readonly=True)


class IWhere(zope.interface.Interface):
    """Basic interface for location related information."""
    
    locations = zope.schema.Set(
        title=_(u'Location Ids'),
        description=_(u"A set of int ids of all object locations."))
                                   
    here = zope.schema.Int(
        title=_(u'Here'),
        description=_(u'Returns the int id of the location itself.'))


class IWhat(zope.interface.Interface):
    """Basic interface for type related information."""

    ref = zope.interface.Attribute('The short reference.')
 
    type = zope.interface.Attribute('The dotted class name.')

    classname = zope.interface.Attribute('The class name.')
    
    name = zope.interface.Attribute('Name of the object.')
    
    tite = zope.interface.Attribute('Title of the object.')
    
    subjects = zope.interface.Attribute('Subjects or keywords.')

    fulltext = zope.interface.Attribute('A text that can be searched.')

    language = zope.interface.Attribute('Main natural language.')


class IContributors(zope.interface.Interface):
    """Contributors setter and getter."""
    
    contributors = zope.interface.Attribute(
        'The principal ids of the contributors (see dc.contributors).')

    
class IWho(zope.interface.Interface, IContributors):
    """Basic interface for author related informations."""

    creator = zope.interface.Attribute(
        'Principal id of the creator of a document.')

    authors = zope.interface.Attribute(
        'The principal ids of the authors of a document.')

    authornames = zope.interface.Attribute(
        'The full names of the authors of a document.')
    
    email = zope.interface.Attribute(
        'The contact email of a person or member.')

      
class IWhen(zope.interface.Interface):
    """Basic interface for time related informations."""

    when = zope.interface.Attribute(
        'Default timestamp. Must exist.')

    created = zope.interface.Attribute(
        'Creation time, if any.')

    modified = zope.interface.Attribute(
        'Modification time, if any.')

    published = zope.interface.Attribute(
        'Publication time, if any.')

    expires = zope.interface.Attribute(
        'Expiration date, if any.')


class IHTMLPreview(zope.interface.Interface):
    """A HTML representation/preview for a content object."""
    
    
class IRDFConverter(zope.interface.Interface):
    """Converts an object into RDF triples."""
    
    namespace = zope.interface.Attribute(
        'The namespace the converter belongs to.')
    
    def convert(graph, node):
        """Adds the triples to the graph and node."""


class IRDFFormat(zope.interface.Interface):
    """A marker for the a specific RDF export/import format."""


class IRDFFactory(zope.interface.Interface):
    """A RDF import factory for content objects."""


class IZoteroFormat(IRDFFormat):
    """Export/Import format for Zotero."""


class IZopeFormat(IRDFFormat):
    """Export/Import format for Zope."""

    
class IBebopFormat(IZopeFormat):
    """Export/Import format for Bebop applications."""


class IDumpDirectory(zope.interface.Interface):
    """A export/import directory."""


class ISnapshot(zope.interface.Interface):
    """Allows to dump to or load from a dump directory."""
    
    def dump(path):
        """Make a snapshot dump."""
        
    def load(path):
        """Loads an object from a snapshot."""
        