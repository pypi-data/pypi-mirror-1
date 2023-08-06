#!/usr/local/env/python
#############################################################################
# Name:         bop
# Purpose:      Support for HTML processing
# Maintainer:
# Copyright:    (c) 2004 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'
import sys, os, re, string, logging, time, tempfile, mimetools
import htmlentitydefs

from cStringIO import StringIO
from subprocess import Popen, PIPE

import zope.app.file.interfaces
import zope.app.file.image
import zope.contenttype
import zope.traversing.api
import zope.traversing.browser
import zope.dublincore.interfaces
import zope.schema.vocabulary
import zope.i18n

from zope.component import ComponentLookupError
from zope.app.security.interfaces import PrincipalLookupError
from zope.security.management import queryInteraction
from zope.publisher.interfaces import IRequest
from zope.publisher.browser import TestRequest
from zope.publisher.browser import BrowserView

from bebop.protocol import protocol
try:
    from cElementTree import ElementTree
except ImportError:    
    from elementtree import ElementTree
try:
    from bebop.cachedir.interfaces import ICacheDir
except ImportError:
    ICacheDir = None
from soup import cachedSoup
    
import interfaces
import permalink
import helper
import shortcut
import shortref

here = os.path.dirname(__file__)

absolutePrefixes = 'http:', 'ftp:', 'https:', 'mailto:'
linkRefs = dict(a='href', img='src') # treat 'a href' and 'img src'

# list of tags, from the HTML 4.01 specification
closingTags =  ['a', 'abbr', 'acronym', 'address', 'applet',
            'b', 'bdo', 'big', 'blockquote', 'button',
            'caption', 'center', 'cite', 'code',
            'del', 'dfn', 'dir', 'div', 'dl',
            'em', 'fieldset', 'font', 'form', 'frameset',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'i', 'iframe', 'ins', 'kbd', 'label', 'legend',
            'map', 'menu', 'noframes', 'noscript', 'object',
            'ol', 'optgroup', 'pre', 'q', 's', 'samp',
            'script', 'select', 'small', 'span', 'strike',
            'strong', 'style', 'sub', 'sup', 'table',
            'textarea', 'title', 'tt', 'u', 'ul',
            'var', 'body', 'colgroup', 'dd', 'dt', 'head',
            'html', 'li', 'option', 'p', 'tbody',
            'td', 'tfoot', 'th', 'thead', 'tr']
nonClosingTags = ['area', 'base', 'basefont', 'br', 'col', 'frame',
            'hr', 'img', 'input', 'isindex', 'link',
            'meta', 'param']
extraTags = ['embed']
allTags = closingTags + nonClosingTags + extraTags
linkRefs = dict(a='href', img='src', embed='src')
maxPageSize = 2**16


def tidyHTML(filename, new_inline_tags=None):
    """ Tidy the (X)HTML file given by filename. """

    # Try to read original
    fd = open(filename, "r")
    original = fd.read()
    fd.close()

    # Build up the command sequence
    command = ["tidy", "-qn", "-asxml", "-latin1"]

    if new_inline_tags:
        command.append("--new-inline-tags")
        command.append(string.join(new_inline_tags, ","))

    command.append(filename)

    # Call tidy on the host
    try:
        process = Popen(command, bufsize=1024, stdout=PIPE, stderr=PIPE)
        output, errors = process.communicate()
    except OSError:
        helper.warning('Unable to execute tidy - is it in your PATH?')
        return original

    # Check whether the result is valid XML
    try:
        tree = ElementTree()
        tree.parse(StringIO(output))
    except:
        tree = None

    if tree is None:
        helper.warning('Invalid xhtml %s' % file)
        return original
    return output


def tidyTree(filename, new_inline_tags=None):
    """ Tidy the (X)HTML file given by filename and return
        it's elementtree.
    """
    # Try to open original (existance check with proper exceptions)
    fd = open(filename, "r")
    fd.close()

    command = ["tidy", "-qn", "-asxml"]

    if new_inline_tags:
        command.append("--new-inline-tags")
        command.append(string.join(new_inline_tags, ","))

    command.append(filename)
    # Call tidy on the host
    try:
        process = Popen(command, bufsize=1024, stdout=PIPE, stderr=PIPE)
        output, errors = process.communicate()
    except OSError:
        helper.warning('Unable to execute tidy - is it in your PATH?')
        return None

    # Check that the result is valid XML
    try:
        tree = ElementTree()
        tree.parse(StringIO(output))
    except:
        tree = None
    return removeNamespace(tree)


def removeNamespace(tree):
    NS = "{http://www.w3.org/1999/xhtml}"
    if tree is not None:
        # remove namespace uris
        for node in tree.getiterator():
            if node.tag.startswith(NS):
                node.tag = node.tag[len(NS):]
    return tree


def isHTML(markup):
    """Try to determine whether str is HTML or not.
    
    We allow also HTML fragments starting with some common tags."""
    markup = markup.lstrip().lower()
    if markup.startswith('<!doctype html'):
        return True
        
    def valid(tag, pos=0):
        pos += len(tag) 
        next = markup[pos+1:pos+2].strip()
        return next == '' or next == '>'
        
    for tag in allTags:
        if markup.startswith('<%s' % tag):
            if valid(tag):
                return True
    if markup.startswith('<!--'):
        for tag in allTags:
            index = markup.find('<%s' % tag)
            if index > 0:
                return valid(tag, index)
    return False

  
suspectLength = 36*1024
suspectTags = dict(a=100, img=100, table=10, p=1000, div=1000)


def isSuspectHTML(str):
    if len(str) > suspectLength:
        return u'Document too long'
        
    lower = str.lower()
    for tag, limit in sorted(suspectTags.items()):
        num = lower.count('<'+tag)
        if num > limit:
            return u"Too many tags (%s %s tags, %s allowed)" % (num, tag, limit)
    return False

    
class HTMLDocument(object):
    """A HTML document that provides access to parsed parts."""


    _url = r'''(?=[a-zA-Z0-9./#])    # Must start correctly
                  ((?:              # Match the leading part
                      (?:ftp|https?|telnet|nntp) #     protocol
                      ://                        #     ://
                      (?:                       # Optional 'username:password@'
                          \w+                   #         username
                          (?::\w+)?             #         optional :password
                          @                     #         @
                      )?                        # 
                      [-\w]+(?:\.\w[-\w]*)+     #  hostname (sub.example.com)
                  )                             #
                  (?::\d+)?                     # Optional port number
                  (?:                           # Rest of the URL, optional
                      /?                                # Start with '/'
                      [^.!,?;:"'<>()\[\]{}\s\x7F-\xFF]* # Can't start with these
                      (?:                               #
                          [.!,?;:]+                     #  One or more of these
                          [^.!,?;:"'<>()\[\]{}\s\x7F-\xFF]+  # Can't finish
                          #'"                           #  # or ' or "
                      )*                                #
                  )?)                                   #
               '''

    _email = r'''(?:mailto:)?               # Optional mailto:
                    ([-\+\w\.]+             # username
                    \@                      # at
                    [-\w]+(?:\.\w[-\w]*)+)  # hostname
                 '''
    
    _url_link = re.compile(_url, re.VERBOSE)
    _email_link = re.compile(_email, re.VERBOSE)
    _text_link = re.compile('\[.*?\]', re.VERBOSE)
    
    knownEncoding = None
    etree = None
    redirect = None      # url transform function
    
    def __init__(self, context, 
                    request=None, html=None, knownEncoding=None, cache=True):
        self.cache = cache     
        if request is None:
            request = helper.request()
        self.request = request
        if isinstance(context, str):
            import bop
            self.context = bop.File(context, 'text/html')
        else:
            self.context = shortcut.unsecure(context)
        
        if not cache:
            if hasattr(self.context,'_v_dom'):
                delattr(self.context, '_v_dom')
        self.transformed = False
        if knownEncoding is not None:
            self.knownEncoding = knownEncoding
        self.html = html or self.context.data
        self.etree = self.parse()
     
    @property
    def source(self):
        try:
            return self.context.data
        except AttributeError:
            return self.html
        
    def parse(self):
        try:
            tree = ElementTree()
            tree.parse(StringIO(self.html))
            return removeNamespace(tree)
        except:
            return None
            
    def tidy(self):
        def computeTidy(*args, **kw):
            if hasattr(self.context, 'path'):
                path = self.context.path
            else:
                handle, path = tempfile.mkstemp(prefix='tidyhtml.')
                os.write(handle, self.source)
                os.close(handle)
            return tidyHTML(path)
        return self.cacheResult(computeTidy, key='tidy')
        
    def info(self):
        try:
            return shortcut.path(self.context)
        except:
            return self.context
            
    def unicode(self, str):
        """Convert to unicode and generate warning if necessary."""
        if isinstance(str, unicode):
            return str
        try:
            return unicode(str, encoding=self.encoding)
        except:
            helper.warning(
                'Cannot generate unicode for %s' % str)
            return unicode(str, encoding=self.encoding, errors='replace')

    def cacheResult(self, compute, **kw):
        if self.cache and\
                ICacheDir is not None and\
                shortcut.parent(self.context) is not None:
            cachedir = shortcut.query(ICacheDir)
            if cachedir is None:
                return compute()
                
            def utf(*args, **kw):
                return helper.utf8(compute(*args, **kw))
                
            return cachedir.unicodeResult(
                self.context, self.request, utf, self.context, **kw)
        return compute()        
 
    def respond(self, compute, **kw):
        return compute()

    def all(self, tag):
        """Iterates over all tags."""
        if self.etree is not None:
            return self.etree.getiterator(tag)
        if self.soup is not None:
            return self.soup.findAll(tag)
        return []
             
    def first(self, tag):
        """Returns the first tag."""
        if self.etree is not None:
            return self.etree.find('.//' + tag)
        if self.soup is not None:
            return self.soup.first(tag)

    def getattr(self, e, attr, default=None):
        """Returns an element attribute."""
        return e.get(attr, default)
        
    def setattr(self, e, attr, value):
        """Sets an element attribute."""
        if value is None:
            helper.warning('Attempt to set %s to None' % (attr))
            return
        try:
            e.set(attr, value)
        except:
            e[attr] = value

    def delattr(self, e, attr):
        try:
            del e.attrib[attr]
        except:
            del e[attr]
            
    def settag(self, e, name):
        """Sets an element's tagname."""
        if name is None:
            helper.warning('Attempt to set name %s to None' % (attr))
            return
        if self.etree is not None:
            e.tag = name
        else:
            e.name = name
            
    def contents(self, e):
        """Returns the text contents of an element."""
        if self.etree is not None:
            return self.unicode(e.text.strip())
        texts = [s for s in e.contents if isinstance(s, unicode)]
        return u''.join(texts).strip()
        
    def toUnicode(self, e):
        if e is None:
            return u''
        if self.etree is not None:
            stream = StringIO()
            self.etree._write(stream, e, self.encoding, {})
            return self.unicode(stream.getvalue())
        return unicode(e)
        
    def document(self):
        if self.etree is not None:
            return self.toUnicode(self.etree.getroot())
        if self.soup is not None:
            return unicode(self.soup)
        return self.__unicode__()
    
    @property
    def soup(self):
        context = self.context
        if not isHTML(self.html):
            helper.warning('Invalid html %s: %s' % (self.info(), (self.html,)))
            return None
        try:
            return cachedSoup(self.html, fromEncoding=self.knownEncoding)
        except:
            helper.printTrace()
            helper.warning('Soup cannot parse %s' % self.info())
            return None
    
    @property
    def shorttitle(self):
        def computeShortTitle(*args, **kw):
            e = self.first('title')
            if e is not None:
                return self.contents(e)
        return self.cacheResult(computeShortTitle, key='shorttitle')
        
    @property
    def longtitle(self):
        def computeLongTitle(*args, **kw):
            tags = 'h1', 'h2', 'h3'
            for h in tags:
                e = self.first(h)
                if e is not None:
                    return self.contents(e)
            return u''        
        return self.cacheResult(computeLongTitle, key='longtitle')

    @property
    def body(self):
        def computeBody(*args, **kw):
            if callable(self.redirect):
                if not self.transformed:
                    for e in self.all('a'):
                        href = self.getattr(e, 'href', '#')
                        self.setattr(e, 'href',
                            self.redirect(self.context, href, 'a'))
                        # Grr, some browser do not like <a href=".." />
                        # so we enforce <a href=".."> </a>
                        if self.etree is not None:
                            if not e.text:
                                e.text = ' '
                                
                    for e in self.all('img'):
                        src = self.getattr(e, 'src', '#')
                        self.setattr(e, 'src',
                            self.redirect(self.context, src, 'img'))
                            
                    for e in self.all('embed'):
                        src = self.getattr(e, 'src', '#')
                        self.setattr(e, 'src',
                            self.redirect(self.context, src, 'img'))
                            
                    self.transformed = True
                return self.toUnicode(self.first('body')).strip()
            b = extractBody(self.source).strip()
            return self.unicode(b)
        return self.cacheResult(computeBody, key='body')

    @property
    def innerBody(self):
        return extractBody(self.body)
        
    @property
    def encoding(self):
        def computeEncoding(*args, **kw):
            if self.knownEncoding:           # a known encoding
                return self.knownEncoding
                
            if self.etree is not None:
                for e in self.etree.findall('.//meta'):
                    http_equiv = content = None
                    attrs = e.items()
                    for k, v in attrs:
                        if k == "http-equiv":
                            http_equiv = string.lower(v)
                        elif k == "content":
                            content = v
                    if http_equiv == "content-type" and content:
                        # use mimetools to parse the http header
                        header = mimetools.Message(
                            StringIO("%s: %s\n\n" % (http_equiv, content))
                            )
                        encoding = header.getparam("charset")
                        if encoding:
                            return encoding
         
            return guessEncoding(self.source, soup=self.soup)
        return self.cacheResult(computeEncoding, key='encoding')     
 
    @property
    def links(self):
        return [self.getattr(a, 'href') for a in self.all('a')]
    
    @property
    def sources(self):
        return [self.getattr(i, 'src') for i in self.all('img')]
        
    @property
    def alllinks(self):
        return self.links + self.sources
        
    def __unicode__(self):
        if isinstance(self.html, unicode):
            return self.html
        return unicode(self.html,
                    encoding=self.encoding,
                    errors='replace')
                    
    def text(self):
        if self.etree is not None:
            elements = self.etree.getiterator()
            return u' '.join([e.text.strip() for e in elements if e.text])
        stripped = stripTags(self.source)
        if isinstance(stripped, unicode):
            return stripped
        return unicode(stripped,
                    encoding=self.encoding,
                    errors='replace')

    def urls(self, request=None, absolute=False):
        """Extracts all links from a document."""
        
        if request is None:
            request = helper.request()
        result = []
        encoding = self.encoding
        for link in self.alllinks:
            if link is None:
                continue
            if link.startswith('#'):
                continue
            link = link.encode(encoding).replace('&amp;', '&')
            if isAbsoluteURL(link):
                result.append(link)
            elif absolute:
                host = request['HTTP_HOST']
                path = request['PATH_INFO']
                if link.startswith('/'):
                    fullpath = joinURL(host, link, normalize=True)    
                else:
                    fullpath = joinURL(host, path, link, normalize=True)
                result.append('http://' + fullpath)
            else:
                result.append(link)                
        return result


def isAbsoluteURL(link) :
    """Returns true if the link is a complete URL. 
        
    Note that an absolute URL in this sense 
    might point to a local object.
    """
    for prefix in absolutePrefixes:
        if link.startswith(prefix):
            return True
    return False


def joinURL(*args, **kw):
    """Join any arbitrary strings into a forward-slash delimited list.
    Do not strip leading / from first element, nor trailing / from last element."""
    if len(args) == 0:
        return ""
    normalize = kw.get('normalize', False)
    slash = '/'
    backslash = '\\'

    if len(args) == 1:
        return str(args[0])

    else:
        args = [str(arg).replace(backslash, slash) for arg in args]

        work = [args[0]]
        for arg in args[1:]:
            if arg.startswith(slash):
                work.append(arg[1:])
            else:
                work.append(arg)

        joined = reduce(os.path.join, work)

    url = joined.replace(backslash, slash)
    if normalize:
        return os.path.normpath(url)
    return url


def guessEncoding(html, default=None, soup=None):
    """Implements improved charset detections.
    
    Uses html.soup as fallback.
    """
    try:
        options = re.DOTALL | re.IGNORECASE
        pattern = re.compile('.*<meta.*charset=(.*?)[ \'"/>]', options)
        charset = pattern.findall(html)
        if len(charset):
            return charset[0].lower()
        else:
            if soup is False:
                return None
            if soup is None:
                soup = cachedSoup(html, fromEncoding=charset)
            return soup.originalEncoding
    except:
        try:
            if soup is None:
                soup = cachedSoup(html, fromEncoding=default)    
            return soup.originalEncoding
        except:
            return default


def extractTitle(html, default=None):
    soup = cachedSoup(html, fromEncoding=default)
    title = soup.first('title')
    if title is not None:
        return title.string
    for tag in 'h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'p':
        found = soup.first(tag)
        if found:
            texts = [s for s in found.contents if isinstance(s, unicode)]
            return u''.join(texts).strip()
    return u''

    
def extractDescription(html, default="iso-8859-1"):
    options = re.DOTALL | re.IGNORECASE
    pattern = re.compile('.*<meta.*description.*content="(.*?)"', options)
    output = pattern.findall(html)
    if len(output) > 1:
        helper.warning("more than one description")
    elif len(output) == 0:
        return u''  
    return unicode(output[0], encoding=guessEncoding(html))

def extractBody(html):
    options = re.DOTALL | re.IGNORECASE
    output = re.compile('<body.*?>(.*?)</body>', options).findall(html)
    if len(output) > 1 :
        helper.warning("more than one body tag")
    elif len(output) == 0 :  # hmmh, a html fragment?
        return html  
    return output[0]


def extractTagContent(html, tag):
    options = re.DOTALL | re.IGNORECASE
    output = re.compile('<%s.*?>(.*?)</%s>' % (tag, tag), options).findall(html)
    if len(output) > 1 :
        helper.warning("more than one %s tag" % tag)
    elif len(output) == 0 : 
        return None
    return output[0]


def extractUnicodeBody(html):
    return unicode(extractBody(html), encoding=guessEncoding(html))


def stripTags(text):
    def fixup(m):
        text = m.group(0)
        if text[:1] == "<":
            return "" # ignore tags
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        elif text[:1] == "&":
            entity = htmlentitydefs.entitydefs.get(text[1:-1])
            if entity:
                if entity[:2] == "&#":
                    try:
                        return unichr(int(entity[2:-1]))
                    except ValueError:
                        pass
                else:
                    return unicode(entity, "iso-8859-1")
        return text # leave as is
    return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text).strip()


def extractPhrase(fulltexts, words, more=8):
    matching = []
    words = [w.lower() for w in words]
    
    def word_matches(word):
        for w in words:
            if word.lower().startswith(w):
                return True
        return False    
    
    for key, value in fulltexts.items():
        text = stripTags(value)
        splitted = text.split()
        count = 0
        match = False
        for w in splitted:
            if word_matches(w):
                match = True
                break
            count += 1
            
        if match:
            start = max(count - more, 0)
            end = count + more
            phrase = splitted[start:end]
            if end < len(splitted):
                phrase.append('...')
            return u' '.join(phrase)
            
    return None


def absoluteURL(obj, request):
    """Helper which may fail."""
    try:
        return zope.traversing.browser.absoluteURL(obj, request)
    except:
        return None


htmlify = protocol.GenericFunction('bop.html.IHtmlify')
@htmlify.when(zope.interface.Interface, zope.interface.Interface)
def default_html(obj, request):
    obj = str(obj)
    lower = obj.lower().strip()
    # pragmatic guess: may not be wellformed
    if lower.startswith('<!doctype html'):
        return extractBody(obj)  
    if lower.startswith('<html') and lower.endswith('html>'):
        return extractBody(obj)
    return '<pre>' + obj + '</pre>'
 

class HTMLPreview(BrowserView):
    """Convenient base class html previews."""
    
    zope.interface.implements(interfaces.IHTMLPreview)

    
class WeblocPreview(HTMLPreview):
    """A preview for .webloc files."""
    
    protocol.adapter(
        zope.app.file.interfaces.IFile, None,
        provides=interfaces.IHTMLPreview,
        name='.webloc')
    
    def __call__(self):
        obj = self.context
        url = extractTagContent(obj.data,'string')
        return u'<a href="%s" target="_blank">%s</a>' % (url, _title())

        
class FlashPreview(HTMLPreview):
    """A preview for flash/shockwave files."""
    
    protocol.adapter(
        zope.app.file.interfaces.IFile, None,
        provides=interfaces.IHTMLPreview,
        name='.swf')

    def __call__(self):
        url = absoluteURL(self.context, self.request)
        download_url = 'http://www.macromedia.com'\
                        '/shockwave/download/index.cgi'\
                        '?P1_Prod_Version=ShockwaveFlash'
        return u' '.join(['<embed src="%s" ' % url,
            'quality="high" loop="false" type="application/x-shockwave-flash"',
            'pluginspage="%s"' % download_url,
            '/>'])


@htmlify.when(zope.app.file.interfaces.IFile, zope.interface.Interface)
def file_html(obj, request):
    """Converts a file into a HTML representation.
    
    Uses registered preview adapters (if available) 
    which should be registered as named adapters resp. views
    with the file extension as names.
    
    Return the html as unicode string.
    """ 
               
    def _title():
        dc = zope.dublincore.interfaces.IZopeDublinCore(obj, None)
        if dc is not None:
            return dc.title or obj.__name__
        else:
            return  obj.__name__
           
    if obj.contentType == 'text/html':
        suspect = isSuspectHTML(obj.data)
        if suspect:
            url = absoluteURL(obj, request)
            link = u'<a href="%s" target="_blank">%s</a>' % (url, _title()) 
            
            msg = u'<p>The file contains suspect HTML: %s</p>' % suspect
            msg += u'<p>Open the file in a new window: %s</p>' % link
            return msg  
        return extractBody(obj.data)
    
    name = obj.__name__ or u''
    ext = helper.extension(name)
    preview = zope.component.queryMultiAdapter((obj, request),
        interfaces.IHTMLPreview,
        name=ext)
    if preview is not None:
        return preview()

    simple = 'text/plain', 'text/xml', 'text/rest'
    if obj.contentType in simple and len(obj.data) < maxPageSize:
        return htmlify(obj.data, request)
    url = absoluteURL(obj, request)

    if url and obj.contentType.startswith('image'):
        img = u'<img src="%s" title="%s" width="%s" height="%s">'
        contentType, w, h = zope.app.file.image.getImageInfo(obj.data)
        dc = zope.dublincore.interfaces.IZopeDublinCore(obj, None)
        return img % (url, _title(), w, h)
 
    dc = zope.dublincore.interfaces.IZopeDublinCore(obj, None)
    title = desc = ''
    if dc is not None:
        if dc.title:
            title = u'<h3>%s</h3>' % dc.title
        if dc.description:
            desc = u'<p>%s</p>' % dc.description
    name = obj.__name__
    result = u'%s%s<p>' % (title, desc)
    if url:
        result += u'Download <a href="%s">%s</a>' % (url, name)
    return result


def relink(markup, context,
            doc=None, type='absolute', encoding=None, cache=True):
    """Recode links in a HTML document."""
    if doc is None:
        doc = HTMLDocument(context, 
                html=markup, knownEncoding=encoding, cache=cache)
    context = context.__parent__
    
    def addclass(element, ref):
        classes = doc.getattr(element, 'class', '').split()
        classes = [c for c in classes if not c.startswith('ref_')]
        classes.append('ref_' + ref)
        doc.setattr(element, 'class', ' '.join(classes))
    
    def convert(element, attr):
        ref = doc.getattr(element, attr)
        try:
            node = zope.traversing.api.traverse(context, ref)
            if node is not None:
                if type == 'perma':
                    doc.setattr(element, attr, permalink.url(node))
                elif type == 'css':
                    doc.setattr(element, attr, 
                                    helper.url(node, helper.request()))
                    addclass(element, shortref.ref(node))
                else:
                    doc.setattr(element, attr, 
                                    helper.url(node, helper.request()))
        except (zope.traversing.interfaces.TraversalError, AttributeError):
            pass
    
    for tag, attr in linkRefs.items():
        for e in doc.all(tag):
            convert(e, attr)
    return doc.document()


def wrapTag(html, tag='div', css_class='doccontent'):
    if html.startswith('<%s class="%s">' % (tag, css_class)):
        return html
    return '<%s class="%s">%s</%s>' % (tag, css_class, html, tag)


def encodedHTML(obj, request=None, default='utf-8', links=None):
    """Returns the html as unicode and also returns the used encoding.
    
    Replaces all relative links with permalinks if necessary.
    """
    if request is None:
        request = helper.request()
    markup = htmlify(obj, request)
    if not markup:
        return u'', default
    if isinstance(markup, unicode):
        if links:
            markup = relink(markup, obj, 
                                type=links, encoding=default, cache=False)
        return markup, default
    try:
        if zope.app.file.interfaces.IFile.providedBy(obj) and \
                obj.contentType == 'text/html':
           encoding = guessEncoding(obj.data, soup=False)
           doc = HTMLDocument(obj,
                              html=markup,
                              knownEncoding=encoding,
                              cache=False)
        else:
           doc = HTMLDocument(obj, html=markup, cache=False)
        encoding = doc.encoding
        if links:
            markup = relink(markup, obj, doc, type=links)
        else:
            markup = doc.document()
        return markup, encoding        
    except Exception, msg:
        helper.printTrace()
        markup = u'<p>Invalid Document: %s</p>' % msg
        return markup, default


def fragment2html(text, encoding='utf-8'):
    html = open(os.path.join(here, 'html.pt')).read()
    if isinstance(text, unicode):
        text = text.encode(encoding)
    body = extractBody(text)
    mapping = dict(
        title=extractTitle(text).encode(encoding),
        body=body,
        encoding=encoding)
    return string.Template(html).substitute(mapping) 


def fullText(obj):
    html = htmlify(obj, helper.request(test=True))
    if html:
        encoding=guessEncoding(html)
        if encoding:
            body = extractBody(html)
            if not isinstance(body, unicode):
                body = unicode(body, encoding)   
            return stripTags(body)
    return u''
