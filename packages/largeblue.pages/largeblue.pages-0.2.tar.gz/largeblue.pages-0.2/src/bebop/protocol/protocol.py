#!/usr/local/env/python
#############################################################################
# Name:         protocol.py
# Purpose:      Defines protocols which simplify registrations
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import sys
import types

import zope.component
import zope.interface
import zope.schema

from zope.interface.interface import InterfaceClass
from zope.configuration.fields import Path
from zope.dottedname.resolve import resolve

import interfaces

from zope.component import zcml
from zope.app.component import metadirectives
from zope.app.component import contentdirective


def isclassframe(frame):
    return '__module__' in frame.f_locals

def ensurelist(obj):
    if obj is None:
        return None
    if not isinstance(obj, list):
        return [obj]
    if not isinstance(obj, tuple):
        return [obj]
    return obj

class ProtocolError(Exception):
    """Protocol exception"""


class Declaration(object):
    """A zcml declaration."""
    
    tagname = u'zcml'
    namespace = u'zope'
    directive = None        # must be set in the subclasses
    activated = False       # each declaration can be only activated once
    module = None           # the module the declaration belongs to
    
    def __init__(self, **kw):
        self.__dict__.update(kw)
        for key, field in self.directive.namesAndDescriptions():
            if field.required:
                if key not in kw:
                    raise KeyError
            if key not in kw:
                self.__dict__[key] = field.default

    def _default_str(self, obj):
        return str(obj)
        
    def fields(self):
        return zope.schema.getFieldNamesInOrder(self.directive)
        
    def tag(self):
        return '%s:%s' % (self.namespace, self.tagname)
        
    def record(self, context=None, inset='   '):
        """Returns the declaration as ZCML."""
        
        def stringify(obj):
            if isinstance(obj, list) or isinstance(obj, tuple):
                return " ".join([stringify(x) for x in obj])
                
            if hasattr(obj, '__name__') and hasattr(obj, '__module__'):
                if obj.__module__ == '__builtin__':
                    return obj.__name__
                return '%s.%s' % (obj.__module__, obj.__name__)
                        
            # we do not want to see <repr ...> within ZCML
            default = self._default_str(obj)
            assert not default.startswith('<')
            return default
            
        def checkpath(field, value):
            if context is not None and isinstance(field, Path):
                zcmlpath = context.path('')
                if value.startswith(zcmlpath):
                    return './' + value[len(zcmlpath)-1:]    
            return value
        
        
        lines = []
        lines.append('%s<%s' % (inset, self.tag()))
        for k in self.fields():
            try:
                v = getattr(self, k)
                field = self.directive[k]
                if v != field.default:
                    v = stringify(v)
                    if v:
                        if k.endswith('_'):
                            k = k[:-1]
                        v = checkpath(field, v)
                        lines.append('%s%s%s="%s"' % (inset, inset, k, v))
            except AttributeError:
                pass
        lines.append('%s/>' % inset)
        return '\n'.join(lines)


class ComplexDeclaration(Declaration):
    """A declaration that mimics a complex directive."""

    def __init__(self, **kw):
        super(ComplexDeclaration, self).__init__(**kw)
        self.declarations = []
        
    def startTag(self, inset):
        return '<%s>' % self.tagname

    def record(self, context=None, inset='   '):
        """Returns the declaration as ZCML."""
        result = [inset + self.startTag()]
        for declaration in self.declarations:
            result.append(declaration.record(context=context, 
                                                inset=inset+'    '))
        result.append('%s</%s>' % (inset, self.tag()))
        return '\n'.join(result)


class SubDeclaration(Declaration):
    """A subdeclaration of a complex declaration."""

    def tag(self):
        return self.tagname


class FactoryDeclaration(Declaration):
    """A declaration of a adapter or utility factory."""

    factory = None
    
    @property
    def module(self):
        """Returns the module of the factory"""
        return self.factory.__module__


class ComponentOrFactoryDeclaration(Declaration):
    """A declaration of a component or factory."""
    
    component = None


class Protocol(object):
    """Base class of a protocol."""
    
    zope.interface.implements(interfaces.IProtocol)
    
    all_protocols = []
    declaration_factory = None
    
    def __init__(self, name, provides=None):
         self.name = name
         self.activated = set()  # activated for a set of modules
         self.written = set()    # written for a set of modules
         self.declarations = {}  # module name: list of declarations
         self.provides = provides
         if self not in self.all_protocols:
            self.all_protocols.append(self)
         
    def __repr__(self):
         return "<protocol %r>" % self.name
    __str__ = __repr__
    
    def _sorted_modules(self, modules=None):
        if modules is None:
            modules = self.declarations.keys()
        return sorted(modules)
        
    def activate(self, modules=None):
        """Activates all declarations within given modules."""
        modules = self._sorted_modules(modules)
        for key in modules:
            for declaration in self.declarations[key]:
                declaration.register()
                declaration.activated = True
        self.activated.update(modules)
        
    def deactivate(self, modules=None):
        """Deactivates all declarations within given modules."""
        modules = self._sorted_modules(modules)
        for key in modules:
            for declaration in self.declarations[key]:
                declaration.unregister()
                declaration.activated = False
        self.activated.update(modules)
        
    def configure(self, context, modules=None):
        """Activates all declarations within a configuration context."""
        modules = self._sorted_modules(modules)
        for key in modules:
            for declaration in self.declarations[key]:
                if not declaration.activated:
                    declaration.configure(context)
                    declaration.activated = False
        self.activated.update(modules)
        
    def __call__(self, *args, **kw):
        """Must be specialized."""
        
    def declare(self, *args, **kw):
        """Adds a declaration to the protocol.
        
        The declaration is registered immediately if the protocol is 
        active in the relevant module.
        
        Otherwise the declaration is collected for later registration.
        """
        
        declaration = self.declaration_factory(*args, **kw)
        module = declaration.module
       
        if module in self.written:
            msg = "protocol '%s' is written and must be"\
                  " reopened for extensions" % self.name
            raise ProtocolError(msg)
        self.declarations.setdefault(module, []).append(declaration)
        if module in self.activated:
            declaration.register()
        return declaration
            
    def record(self, context=None, modules=None):
        declarations = []
        modules = self._sorted_modules(modules)
        for key in modules:
            declarations += self.declarations[key]
        result = recordDeclarations(declarations, context=context)
        self.written.update(modules)
        return result
        
    def reopen(self, modules=None):
        if modules is None:
            self.written.clear()
        else:
            self.written = self.written - set(modules)
                    

def recordDeclarations(declarations, context=None):
    namespaces = set()
    selected = []   
    for declaration in declarations:
        namespaces.add(declaration.namespace)
        selected.append(declaration)
            
    result = ['<configure']
    for namespace in sorted(namespaces):
        pat = '       xmlns:%s="http://namespaces.zope.org/%s"'
        result.append(pat % (namespace, namespace))
    result.append('      >')
    result.append('   <!-- GENERATED PROTOCOL. DO NOT MODIFY OR INCLUDE -->')
    
    for declaration in selected:
        result.append(declaration.record(context=context))
    result.append('</configure>')
    return '\n'.join(result)
    

class Adapter(object):
    """A convenience base class for Protocol adapters."""
    
    def __init__(self, context):
        self.context = context
        
        
class AdapterDeclaration(FactoryDeclaration):
    """An adapter declaration."""
    
    directive = zcml.IAdapterDirective
    tagname = 'adapter'
    
    trusted = False
    locate = False
    
    def configure(self, context):
        zcml.adapter(context, (self.factory,), 
            provides=self.provides, for_=self.for_,
            permission=self.permission,
            name=self.name or '',
            trusted=self.trusted,
            locate=self.locate)

    def register(self):
        zope.component.provideAdapter(
            factory=self.factory,
            provides=self.provides,
            adapts=self.for_,
            name=self.name)
    
    def unregister(self):
        zope.component.globalSiteManager.unregisterAdapter(
            factory=self.factory,
            provided=self.provides,
            required=self.for_,
            name=self.name)


class UnnamedAdapterDeclaration(AdapterDeclaration):
    """An adapter declaration."""
    
    directive = zcml.IAdapterDirective
    tagname = 'adapter'

    def register(self):
        zope.component.provideAdapter(
            factory=self.factory,
            provides=self.provides,
            adapts=self.for_)
    
    def unregister(self):
        zope.component.globalSiteManager.unregisterAdapter(
            factory=self.factory,
            provided=self.provides,
            required=self.for_)


def _adapter(cls):
    """Class advisor for the adapter declaration."""
    protocol, parameter = cls.__dict__['__adapter_protocol__']
    del cls.__adapter_protocol__

    if parameter.provides is None :
        parameter.provides = protocol.provides
    adapts = parameter.adapts
    if adapts is None :
        adapts = zope.component.adaptedBy(cls)
    else :
        zope.component.adapter(adapts)(cls)
    try:
        adapts = list(adapts)
    except TypeError:
        adapts = [adapts]
    protocol.declare(factory=cls, 
        for_=adapts,
        provides=parameter.provides,
        name=parameter.name,
        trusted=parameter.trusted,
        permission=parameter.permission)
    return cls    


class _adapter_parameter(object):
    """Represents default values of the adapter declaration."""
    
    trusted = False
    name = ''
    provides = None
    adapts = None
    permission=None
    
    def __init__(self, **kw):
        self.__dict__.update(kw)
      
class AdapterProtocol(Protocol):
    """An adapter protocol.
    
    This base class can be used to define special adapter protocols.
    Use the default adapterProtocol below if you have no special needs.
    """
    
    declaration_factory = AdapterDeclaration
    
    def __call__(self, arg):
        adapter = self.provides(arg)
        return getattr(adapter, self.name)()
        
    def adapter(self, **kw):
        """Declares an adapter statement within a class definition."""
        frame = sys._getframe(1)
        locals = frame.f_locals
    
        if not isclassframe(frame):
            raise TypeError("adapter can be used only from a class definition.")
    
        locals['__adapter_protocol__'] =  self, _adapter_parameter(**kw)
        zope.interface.advice.addClassAdvisor(_adapter)
 
adapterProtocol = AdapterProtocol('adapter')    # a basic adapter protocol that
                                                # is used by the adapter
                                                # statement below

class adapter(_adapter_parameter):
    """Substitute for the adapter directive.

    If called with a class definition it uses a class advisor to declare
    the class as an adapter.
    
    If called as a decorator it declares the function as an adapter.
    """
       
    def __init__(self, *adapted, **kw):
        self.adapts = adapted
        self.__dict__.update(kw)
        frame = sys._getframe(1)
        locals = frame.f_locals
        if not isclassframe(frame):
            return
        locals['__adapter_protocol__'] = adapterProtocol, self
        zope.interface.advice.addClassAdvisor(_adapter)

    def __call__(self, f):
        adapterProtocol.declare(factory=f,
            for_=self.adapts, 
            provides=self.provides,
            name=self.name,
            permission=self.permission)
        return f
        
        
class UtilityDeclaration(ComponentOrFactoryDeclaration):
    """A utility declaration."""
    
    directive = zcml.IUtilityDirective
    tagname = 'utility'
    
    def __init__(self, **kw):
        super(UtilityDeclaration, self).__init__(**kw)
        factory = self.factory = kw.get('factory')
        component = self.component = kw.get('component')
        self.permission = kw.get('permission')
        if factory is None:
            if component is None:
                raise TypeError(
                    "Either factory or component must be specified.")
            if isinstance(component, str):
                self.module = '.'.join(component.split('.')[:-1])
               
        elif component is not None:
            raise TypeError("Can't specify factory and component.")
        
    def _default_str(self, obj):
        if obj == self.component:
            return '%s.%s' % (self.module, self.variable)
        return str(obj)
        
    def configure(self, context):
        zcml.utility(context, factory=self.factory,
                                    component=self.component,
                                    provides=self.provides,
                                    permission=self.permission,
                                    name=self.name)            
            
    def register(self):
        if self.factory is None:
            obj = self.component
        else:
            obj = self.factory()
        zope.component.provideUtility(obj, 
            provides=self.provides, name=self.name)
    
    def unregister(self):
        if self.factory is None:
            obj = self.component
        else:
            obj = self.factory()
        zope.component.globalSiteManager.unregisterUtility(obj,
                                      provides=self.provides,
                                      name=self.name)


class UtilityProtocol(Protocol):
    """Default utility protocol."""
    
    declaration_factory = UtilityDeclaration
    
    def __call__(self, name=u''):
        return zope.component.queryUtility(self.iface, name=name)

utilityProtocol = UtilityProtocol('utility')

def utility(component=None, factory=None, 
                provides=None, permission=None, name='', variable=None):
    """Shortcut for the use of the default utility protocol within a module."""
    
    frame = sys._getframe(1)
    locals = frame.f_locals
    module_name = locals['__name__']
    utilityProtocol.declare(
        component=component, 
        factory=factory,
        provides=provides,
        permission=permission,
        name=name,
        variable=variable,
        module=module_name)


class SubscriberDeclaration(FactoryDeclaration):
    directive = zcml.ISubscriberDirective
    tagname = 'subscriber'

    @property
    def module(self):
        obj = self.handler or self.factory
        return obj.__module__
        
    def configure(self, context):
        zcml.subscriber(context,
            for_=self.for_,
            factory=self.factory,
            handler=self.handler,
            provides=self.provides,
            permission=self.permission,
            trusted=self.trusted,
            locate=self.locate)

    def register(self):
        if self.handler is None:
            zope.component.provideSubscriptionAdapter(self.factory,
                adapts=self.for_,
                provides=self.provides)
        else:
            zope.component.provideHandler(self.handler, self.for_)

    def unregister(self):
        if self.handler is None:
            zope.component.unregisterSubscriptionAdapter(
                factory=self.factory,
                required=self.for_,
                provided=self.provides)
        else:
            zope.component.globalSiteManager.unregisterHandler(
                factory=self.handler,
                required=self.for_)

class SubscriberProtocol(Protocol):
    """Default subscriber protocol."""
    
    declaration_factory = SubscriberDeclaration
    
subscriberProtocol = SubscriberProtocol('subscriber')


def subscriber(*types, **kw):
    def decorator(adapter):
        subscriberProtocol.declare(handler=adapter, for_=types, 
                            provides=kw.get('provides'))
        return adapter
    return decorator



class ClassDeclaration(ComplexDeclaration):
    """A class declaration."""
    directive = metadirectives.IClassDirective
    tagname = 'class'
    
    class_ = None

    @property
    def module(self):
        return self.class_.__module__
        
    def startTag(self):
        obj = self.class_
        dottedname = '%s.%s' % (obj.__module__, obj.__name__)
        return '<zope:%s class="%s">' % (self.tagname, dottedname)

    def configure(self, context):
        directive = contentdirective.ClassDirective(context, self.class_)
        for declaration in self.declarations:
            declaration.configure(context, directive)


class RequireDeclaration(SubDeclaration):
    """A require declaration within a class declaration."""
    directive = metadirectives.IRequireSubdirective
    tagname = 'require'

    permission = None
    attributes = None
    like_class = None
    interface = None
    set_attributes = None
    set_schema = None

    def configure(self, context, maindirective):
        maindirective.require(context,
            permission=self.permission,
            attributes=self.attributes,
            interface=self.interface,
            like_class=self.like_class,
            set_attributes=self.set_attributes,
            set_schema=ensurelist(self.set_schema))


class ImplementsDeclaration(SubDeclaration):
    """An implements declaration within a class declaration."""
    directive = metadirectives.IImplementsSubdirective
    tagname = 'implements'

    interface = None
    
    def configure(self, context, maindirective):
        maindirective.implements(context,
            interface=self.interface)


class AllowDeclaration(SubDeclaration):
    """An allow declaration within a class declaration."""
    directive = metadirectives.IAllowSubdirective
    tagname = 'allow'

    attributes = None    
    interface = None

    def configure(self, context, maindirective):
        maindirective.allow(context,
            attributes=self.attributes,
            interface=self.interface)


class FactoryDeclaration(SubDeclaration):
    """A factory declaration within a class declaration."""
    directive = metadirectives.IFactorySubdirective
    tagname = 'factory'

    id = None    
    description = ''
    title = ''

    def configure(self, context, maindirective):
        maindirective.factory(context,
            id=self.id,
            description=self.description)


def _class(cls):
    """Class advisor for the class statement."""
    protocol, subdeclarations = cls.__dict__['__class_protocol__']
    del cls.__class_protocol__
    complex = protocol.declare(class_=cls)
    complex.declarations = subdeclarations
    return cls


class ClassProtocol(Protocol):
    """A protocol for class declarations."""
    
    declaration_factory = ClassDeclaration
    
    def _declare(self, factory, locals, ifaces, kw):
        if 'interface' in kw:
            ifaces += (kw['interface'],)
        kw['interface'] = ifaces
        declaration = factory(**kw)
        if '__class_protocol__' in locals:
            locals['__class_protocol__'][1].append(declaration)
            return False
        locals['__class_protocol__'] = self, [declaration]
        return True

    def implements(self, *ifaces, **kw):
        frame = sys._getframe(1)
        locals = frame.f_locals
        if not isclassframe(frame):
            raise TypeError(
                "implements can be used only from a class definition")        
        if self._declare(ImplementsDeclaration, locals, ifaces, kw):
            zope.interface.advice.addClassAdvisor(_class)

    def require(self, *ifaces, **kw):
        frame = sys._getframe(1)
        locals = frame.f_locals
        if not isclassframe(frame):
            raise TypeError("require can be used only from a class definition")        
        if self._declare(RequireDeclaration, locals, ifaces, kw):
            zope.interface.advice.addClassAdvisor(_class)

    def allow(self, *ifaces, **kw):
        frame = sys._getframe(1)
        locals = frame.f_locals
        if not isclassframe(frame):
            raise TypeError("allow can be used only from a class definition")
        if self._declare(AllowDeclaration, locals, ifaces, kw):
            zope.interface.advice.addClassAdvisor(_class)

    def factory(self, **kw):
        frame = sys._getframe(1)
        locals = frame.f_locals
        if not isclassframe(frame):
            raise TypeError("allow can be used only from a class definition")
        declaration = FactoryDeclaration(**kw)
        if '__class_protocol__' in locals:
            locals['__class_protocol__'][1].append(declaration)
            return
        locals['__class_protocol__'] = self, [declaration]
        zope.interface.advice.addClassAdvisor(_class)
            

classProtocol = ClassProtocol('class')

# short cuts
implements = classProtocol.implements 
require = classProtocol.require 
allow = classProtocol.allow     
factory = classProtocol.factory

class GenericFunction(AdapterProtocol):
    """A protocol for generic functions.
    
    The default behavior is to do nothing if no handlers are registered.
    """

    declaration_factory = UnnamedAdapterDeclaration
    
    def __init__(self, name, bases=None, 
                        attrs=None, module_name=None, provides=None, **kw):
        if module_name is None:
            frame = sys._getframe(1)
            globals = frame.f_globals
            module_name = globals['__name__']
        if provides is None:
            if '.' in name:
                name = name.split('.')[-1]
                
            if bases is None:
                bases = (zope.interface.Interface,)
                
            provides = InterfaceClass(
                name=name, 
                bases=tuple(bases),
                attrs=attrs,
                __doc__='Generated from bebop.protocol.GenericFunction',
                __module__=module_name,
                )
        super(GenericFunction, self).__init__(
            name, 
            provides=provides)
        
    def __repr__(self):
         return "<protocol %r.%r>" % (
            self.provides.__module__, self.provides.__name__)
    __str__ = __repr__

    def __call__(self, *args):
        if len(args) > 1:
            return zope.component.queryMultiAdapter(args, self.provides)
        return self.provides(args[0], None)

    def when(self, *types, **kw):
        def decorator(f):
            self.declare(factory=f, 
                            for_=types, 
                            provides=self.provides,
                            permission=kw.get('permission'))
            return f
        return decorator


class NonNoneFunction(GenericFunction):
    """A generic function that use getAdapter calls.
    
    Raises a ComponentLookupError if the function returns None.
    """
    
    def __call__(self, *args):
        if len(args) > 1:
            return zope.component.getMultiAdapter(args, self.provides)
        return self.provides(args[0])

