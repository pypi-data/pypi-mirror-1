#!/usr/local/env/python
#############################################################################
# Name:         directive.py
# Purpose:      Defines protocol directives for ZCML
# Maintainer:   Uwe Oestermeier
# Copyright:    (c) 2007 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import sys
import os.path
import zope.interface

from zope.configuration.fields import GlobalObject
from zope.configuration.fields import PythonIdentifier
from zope.configuration.fields import Path
from zope.configuration.exceptions import ConfigurationError
from zope.configuration import xmlconfig

from bebop.protocol.protocol import Protocol
from bebop.protocol.protocol import recordDeclarations

class IProtocolInfo(zope.interface.Interface) :
    """Parameter schema for the protocol directive
    """

    package = PythonIdentifier(
        title=u"Package",
        description=u'The package which should be recorded.',
        required=False)

    module = PythonIdentifier(
        title=u"Module",
        description=u'The module which should be recorded.',
        required=False)

    record = Path(title=u"Record",
        description=u"The file path to write the generated report.",
        required=False)


class IActivateInfo(zope.interface.Interface) :
    """Parameter schema for the activate directive
    """

    protocol = GlobalObject(
        title=u"Protocol",
        description=u'Protocol to be activated.',
        required=False)

    record = Path(title=u"Record",
        description=u"The file path to write the generated report.",
        required=False)


class IExtendInfo(zope.interface.Interface) :
    """Parameter schema for the extend directive
    """

    protocol = GlobalObject(
        title=u"Protocol",
        description=u'Protocol to be activated.',
        required=False)

    module = PythonIdentifier(
        title=u"Module",
        description=u'The module that extends the protocol.',
        required=False)

    record = Path(title=u"Record",
        description=u"The file path to write the generated report.",
        required=False)


def protocolZCML(context, **kw):
    package = kw.get('package')
    if package:
        __import__(package)
        imported = sys.modules[package].__file__
        if not os.path.basename(imported).startswith('__init__.py'):
            raise TypeError('module %s imported as a package' % package)    
        modules = scan_package(package)
    else:
        module = kw.get('module')
        __import__(module)
        imported = sys.modules[module].__file__
        if os.path.basename(imported).startswith('__init__.py'):
            raise TypeError('package %s imported as a module' % module)
        modules = [module]        
    declarations = []
    for protocol in Protocol.all_protocols:
        for module in modules:
            for declaration in protocol.declarations.get(module, []):
                declarations.append(declaration)
                try:
                    declaration.configure(context)
                except ConfigurationError, msg:
                    record = declaration.record()
                    msg = '%s in protocol declaration\n%s' % (msg, record)
                    raise ConfigurationError(msg)
       
    return recordDeclarations(declarations, context=context)
   
def write(context, file, zcml):
    path = context.path(file)
    try:
        fp = open(path, 'w')
        fp.write(zcml)
        fp.close()
    except IOError:
        pass
    
def protocol(context, **kw):
    zcml = protocolZCML(context, **kw)
    file = kw.get('record')
    if file:
        write(context, file, zcml)
            
def activate(context, **kw):
    protocol = kw.get('protocol')
    protocol.configure(context)
    
    file = kw.get('record')
    if file:
        write(context, file, protocol.record())
        
def extend(context, **kw):
    protocol = kw.get('protocol')
    protocol.extensible = True
    
    module = kw.get('module')
    __import__(module)
    
    protocol.configure(context)
    
    file = kw.get('record')
    if file:
        write(
            context,
            file,
            protocol.record(context=context, modules=(module,)))
    protocol.extensible = False

def is_package(path):
    if not os.path.isdir(path):
        return False
    init_py = os.path.join(path, '__init__.py')
    init_pyc = init_py + 'c'
    # Check whether either __init__.py or __init__.pyc exist
    return os.path.isfile(init_py) or os.path.isfile(init_pyc)


def scan_package(dotted_name):
    package = sys.modules[dotted_name]
    directory = os.path.dirname(package.__file__)
    seen = set()
    modules = []
    if not is_package(directory):
        raise TypeError('%s must be a package' % dotted_name)
    for entry in sorted(os.listdir(directory)):
        entry_path = os.path.join(directory, entry)
        name, ext = os.path.splitext(entry)
        dotted_sub_name = dotted_name + '.' + name

        # Case one: modules
        if (os.path.isfile(entry_path) and ext in ['.py', '.pyc']):
            if name == '__init__':
                continue
            # Avoid duplicates when both .py and .pyc exist
            if name in seen:
                continue
            seen.add(name)
            __import__(dotted_sub_name)
            modules.append(dotted_sub_name)
        # Case two: packages
        elif is_package(entry_path):
            # We can blindly use __init__.py even if only
            # __init__.pyc exists because we never actually use
            # that filename.
            
            __import__(dotted_sub_name)
            subpackage = sys.modules[dotted_sub_name]
            modules.append(subpackage)
            for module in scan_package(dotted_sub_name):
                modules.append(module)
                
    return modules



def record(package=None, module=None):
    """Sets up a configuration context for a package or module
    and records all ZCML statements.
    """
    import bebop.protocol
    context = xmlconfig.file('meta.zcml',  bebop.protocol)
    return protocolZCML(context, package=package, module=module, debug=True)




