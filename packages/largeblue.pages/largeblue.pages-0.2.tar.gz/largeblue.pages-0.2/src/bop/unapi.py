#!/usr/bin/python
#############################################################################
# Name:         unapi.py
# Purpose:      Defines generic functions to support the unAPI standard
# Maintainers:  Uwe Oestermeier <u.oestermeier@iwm-kmrc.de>
# Copyright:    (c) iwm-kmrc.de KMRC - Knowledge Media Research Center
# License:      GPLv2
#############################################################################
__docformat__ = 'restructuredtext'

import os.path

from bebop.protocol import protocol
from bebop.protocol import browser

import shortcut
import shortref
import helper
import interfaces

formats = protocol.GenericFunction('IUnApiFormats')
@formats.when(None, None)
def default_formats(context, request):
    """Returns a dict of object specific unAPI formats."""
    return dict()


@formats.when(interfaces.IFile, None)
def file_formats(context, request):
    """Returns a dict of file specific unAPI formats."""
    path, ext = os.path.splitext(context.__name__)
    if ext:
        return { ext[1:] : context.contentType }
    return dict()


@formats.when(interfaces.IContainer, None)
def container_formats(context, request):
    """Returns a dict of container specific unAPI formats."""
    result = dict()
    for key, value in context.items():
        result.update(**formats(value, request))
    return result


identifier = protocol.GenericFunction('IUnApiIdentifier')
@identifier.when(None, None)
def default_identifier(obj, context):
    return shortref.ref(obj, context)

    
resolve = protocol.GenericFunction('IUnApiResolve')
@resolve.when(None, None)
def default_resolve(id, context):
    return shortref.resolve(id, context)


formatted = protocol.GenericFunction('IUnApiFormatted')
@formatted.when(None, None)
def default_formatted(obj, format):
    raise Undefined


@formatted.when(interfaces.IFile, None)
def file_formatted(obj, format):
    return obj.data, obj.contentType


def abbr(id):
    return '<abbr class="unapi-id" title="%s"></abbr>' % id

def link(context, request, view='@@unapi'):
    url = helper.url(context, request) + '/' + view
    return '<link rel="unapi-server" type="application/xml" href="%s" />' % url
   
def defaultHandler(context, request):
    """Default implementation of an unAPI handler."""
    identifier = helper.parameter(request, 'id')
    format = helper.parameter(request, 'format')
    if identifier and format:
        obj = resolve(identifier, context)
        data, content_type = formatted(obj, format)
        request.response.setHeader('Content-Type', content_type)
        return data
    
    lines = []
    start = "<?xml version='1.0' encoding='UTF-8'?>\n"
    open = "<formats>\n"
    end = "\n</formats>"
    request.response.setHeader('Content-Type', 'text/xml')
    if identifier:
        obj = resolve(identifier, context)
        for k, v in formats(obj, request).items():
            lines.append("<format name='%s' type='%s' />" % (k, v))
        return (start +
                "<formats id=\""+identifier+"\">\n"
                + '\n'.join(lines) + end)
   
    for k, v in formats(context, request).items():
        lines.append("<format name='%s' type='%s' />" % (k, v))
    return (start + open + '\n'.join(lines) + end)

handler = browser.ViewFunction()
@handler.when(None, name='unapi')
def default_handler(context, request):
    """Answers the unApi requests."""
    return defaultHandler(context, request)
                
