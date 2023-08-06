#!/usr/local/env/python
#############################################################################
# Name:         browser.py
# Purpose:      View related protocols
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import sys
import os.path
import logging

from zope import interface
from zope import component

from zope.publisher.interfaces import IPublishTraverse, NotFound
from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.app.publisher.browser import metadirectives
from zope.app.publisher.browser import viewmeta
from zope.app.publisher.browser import menu, menumeta

from zope.security.interfaces import Unauthorized, IParticipation
from zope.security.management import getSecurityPolicy

import protocol
import interfaces

logger = logging.getLogger("Bebop.protocol")

class PageDeclaration(protocol.Declaration):
    """A page declaration 

    Substitutes the viewmeta.page directive.
    """

    directive = metadirectives.IPageDirective
    tagname = 'page'
    namespace = u'browser'
    
    class_ = None
    provides = IBrowserPage
    layer = IDefaultBrowserLayer
    allowed_interface = None
    allowed_attributes = None
    attribute='__call__'
    permission='zope.Public'
    for_=interface.Interface
    template=None
    menu = None
    title = None

    @property
    def module(self):
        obj = self.class_ or self.factory 
        return obj.__module__

    def configure(self, context):
        """Configures a page.
        
        Calls the viewmeta.page directive.
        """
        viewmeta.page(context, self.name, self.permission, self.for_,
                        layer=self.layer, template=self.template,
                        class_=self.class_, 
                        allowed_interface=self.allowed_interface,
                        allowed_attributes=self.allowed_attributes,
                        attribute=self.attribute, menu=self.menu,
                        title=self.title)

    def register(self):
        component.provideAdapter(factory=self.factory,
                                      provides=self.provides,
                                      adapts=(self.for_, IBrowserRequest),
                                      name=self.name)

    def unregister(self):
        component.globalSiteManager.unregisterAdapter(factory=self.factory,
                                      provided=self.provides,
                                      required=(self.for_, IBrowserRequest),
                                      name=self.name)

class PageSubDeclaration(protocol.SubDeclaration, PageDeclaration):
    """The page declaration as a subdirective."""

class PageProtocol(protocol.Protocol):
    """A page protocol which simplifies the declaration of browser pages."""
    declaration_factory = PageDeclaration

class PagesProtocol(protocol.Protocol):
    """A page protocol which simplifies the declaration of browser pages."""
    declaration_factory = PageSubDeclaration


pageProtocol = PageProtocol('bebop.protocol.browser.page')
pagesProtocol = PagesProtocol('bebop.protocol.browser.pages')

def _pages(cls):
    """Advice for the pages statement.
    
    Collects all page subdeclarations.
    """    
    pages_parameter = cls.__dict__['__pages_protocol__']
    del cls.__pages_protocol__
    page_list = cls.__dict__['__page_protocol_list__']
    del cls.__page_protocol_list__
    pages_parameter['factory'] = cls
    pages_parameter['class_'] = cls
    for page_parameter in page_list:
        kw = dict(pages_parameter)
        kw.update(page_parameter.__dict__)
        pageProtocol.declare(**kw)
    return cls    

def pages(*for_, **kw):
    """Protocol substitute for the browser pages directive. 
    
    Defines multiple pages without repeating all of the parameters.
    The pages directive allows multiple page views to be defined
    without repeating the 'for', 'permission', 'class', 'layer',
    'allowed_attributes', and 'allowed_interface' attributes.
    """
    
    frame = sys._getframe(1)
    locals = frame.f_locals
    
    if for_:
        if 'for_' in kw:
            raise TypeError("for can be used only if solely"\
                            "keyword parameters are used.")
        kw['for_'] = for_[0]
    # Try to make sure we were called from a class def. In 2.2.0 we can't
    # check for __module__ since it doesn't seem to be added to the locals
    # until later on.
    if (locals is frame.f_globals) or ('__module__' not in locals):
        raise TypeError("pages can be used only from a class definition.")

    locals['__pages_protocol__'] = kw
    locals['__page_protocol_list__'] = []
        
    interface.advice.addClassAdvisor(_pages)


def _page(cls):
    """Advice for the page statement.
    
    Collects all page subdeclarations.
    """
    if '__page_protocol__' in cls.__dict__:
        page_parameter = cls.__dict__['__page_protocol__']
        del cls.__page_protocol__
        page_parameter['factory'] = cls
        page_parameter['class_'] = cls
        
        pageProtocol.declare(**page_parameter)
    return cls    


class page(object):
    """Substitute for the browser page directive.
    
    Adds self to the list of page declarations.
    If called as a decorator it uses the function name
    as an implicitely specified attribute parameter and default name.
    """
    
    def __init__(self, *for_, **kw):
        frame = sys._getframe(1)
        locals = frame.f_locals
        if for_:
            if 'for_' in kw:
                raise TypeError("for can be used only "\
                                "if solely keyword parameters are used.")
            kw['for_'] = for_[0]
            
        self.__dict__.update(kw)
        if 'template' in kw:
            file = frame.f_globals['__file__']
            dir = os.path.dirname(file)
            path = os.path.abspath(os.path.join(dir, self.template))
            if not os.path.exists(path):
                raise ValueError("No such file", path)
            self.template = path
       
        if locals.get('__pages_protocol__'): 
            locals.setdefault('__page_protocol_list__', []).append(self)
        else:
            locals['__page_protocol__'] = kw
            interface.advice.addClassAdvisor(_page)


    def __call__(self, f):
        if hasattr(self, 'template'):
            raise TypeError("page can be used as a decorator "\
                            "only without template parameter.")
        self.attribute = f.func_name
        if not hasattr(self, 'name'):
            self.name = f.func_name
        return f


class MenuDeclaration(protocol.UtilityDeclaration):
    """A menu declaration 

    Substitutes the viewmeta.menu directive.
    """

    directive = metadirectives.IMenuDirective
    tagname = 'menu'
    namespace = u'browser'
    
    class_ = menu.BrowserMenu
    interface = None
    title = u''
    description = u''
 
    def __init__(self, id=None, class_=menu.BrowserMenu, 
                interface=None, title=u'', description=u''):
        super(MenuDeclaration, self).__init__(name=id,
                                                factory=class_,
                                                provides=interface,
                                                id=id,
                                                class_=class_,
                                                interface=interface)

    def configure(self, context):
        """Configures a menu.
        
        Calls the menumeta.menuDirective directive.
        """
        menumeta.menuDirective(context, id=None, class_=self._class, 
                    interface=self.interface,
                    title=self.title, description=self.description)

    def register(self):
        obj = self.class_(self.id, self.title, self.description)
        zope.component.provideUtility(obj, 
                            provides=self.interface, name=self.id)

    def unregister(self):
        obj = self.class_(self.id, self.title, self.description)
        zope.component.globalSiteManager.unregisterUtility(obj,
                                      provides=self.provides,
                                      name=self.name)

class MenuProtocol(protocol.UtilityProtocol):
    """Default utility protocol."""
    
    declaration_factory = MenuDeclaration
    
    def __call__(self, id=u''):
        return zope.component.queryUtility(self.iface, name=id)

menuProtocol = MenuProtocol('menu')

def menu(id=None, class_=menu.BrowserMenu, 
                interface=None, title=u'', description=u''):
    """Shortcut for the use of the default menu protocol within a module."""
    
    frame = sys._getframe(1)
    locals = frame.f_locals
    module_name = locals['__name__']
    menuProtocol.declare(
        id=id, 
        class_=class_,
        interface=interface,
        title=title,
        description=description)


class MenuItemDeclaration(protocol.Declaration):
    """A menu item declaration 

    Substitutes the viewmeta.menu directive.
    """

    directive = metadirectives.IMenuItemDirective
    tagname = 'menuitem'
    namespace = u'browser'
    
    title = u''
    description = u''
    action = u''
    extra = None
    order = 0
    permission = None
    filter = None
    icon = None
    _for = interface.Interface
    layer = IDefaultBrowserLayer
    
    def configure(self, context):
        """Configures a menu.
        
        Calls the menumeta.menuDirective directive.
        """
        directive = menumeta.menuItemDirective(context, 
            self.menu, self.for_, self.layer)
        directive.menuItem(context,
            self.action, self.title, self.description, self.icon, self.filter,
            self.permission, self.extra, self.order)


class MenuItemProtocol(protocol.UtilityProtocol):
    """Default menuitem protocol."""
    
    declaration_factory = MenuItemDeclaration
    

menuItemProtocol = MenuItemProtocol('menuitem')

def menuItem(menu, for_,
                action, title, description=u'', icon=None, filter=None,
                permission=None, layer=IDefaultBrowserLayer, extra=None,
                order=0):
    """Shortcut for the use of the default menuitem protocol within a module."""
    
    frame = sys._getframe(1)
    locals = frame.f_locals
    module_name = locals['__name__']
    menuItemProtocol.declare(menu=menu, for_=for_,
                action=action,
                title=title,
                description=description,
                icon=icon,
                filter=filter,
                permission=permission,
                layer=layer,
                extra=extra,
                order=order)


class GenericViewFunctionTraverser(object):
    """A view class that mimics the standard page traversal.
    
    Redirects the 'index.html' call to a generic function.
    """

    interface.implements(IPublishTraverse)
    
    def __init__(self, f):
        self.func = f
        self.permission = 'zope.Public'

    def checkPermission(self):
        """Test if the principal has access according to the security policy."""
        if self.permission == 'zope.Public':
            return True
        participation = ProbeParticipation(self.request.principal)
        interaction = getSecurityPolicy()(participation)
        return interaction.checkPermission(self.permission, self.context)
        
    def __call__(self, context, request):
        self.context = context
        self.request = request
        if not self.checkPermission():
            raise Unauthorized
        return self

    def callFunction(self):
        return self.func(self.context, self.request)
        
    def publishTraverse(self, request, name):
        if name == 'index.html':
            return self.callFunction
        raise NotFound(self.context, name)


class ViewFunction(protocol.GenericFunction):
    """A generic function that is registered as a view.
    
    Note that generic functions are regvistered as public adapters and
    check the permission themselves on traversal. 
    
    See GenericViewFunctionTraverser.__call__
    
    """
    
    declaration_factory = protocol.AdapterDeclaration

    provides = interface.Interface

    def __init__(self):
        super(ViewFunction, self).__init__(None, provides=self.provides)
        
    def when(self, for_, **kw):
        def decorator(f):
            traverser = GenericViewFunctionTraverser(f)
            traverser.__name__ = f.func_name
            traverser.__module__ = f.__module__
            
            permission = kw.get('permission')
            if permission:
                traverser.permission = permission
                
            self.declare(factory=traverser, 
                    for_=(for_, IBrowserRequest), 
                    provides=self.provides,
                    name=kw['name'])
            
            return traverser

        return decorator


class ProbeParticipation:
    """A stub participation for use in hasPermission."""
    interface.implements(IParticipation)
    def __init__(self, principal):
        self.principal = principal
        self.interaction = None


