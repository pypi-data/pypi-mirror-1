__docformat__ = 'restructuredtext'

from zope import interface
from zope import component

from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.security.interfaces import Unauthorized
from zope.filerepresentation.interfaces import IReadDirectory

import zope.app.container.interfaces
import z3c.dav.propfind 
import z3c.dav.interfaces

MS_WEBFOLDER = 'Microsoft Data Access Internet Publishing Provider DAV'


class PROPFINDPATCH(z3c.dav.propfind.PROPFIND):
    """A patch for the PROPFIND method.
    
    This patch solves the MS WebFolder issue discussed at
    
    http://www.nabble.com/MS-Webfolder-WebDAV-Client:
    -Authentication-issue-with-handling-of-replies-to-PUT-requests-t3137698.html
       
    """

    interface.implements(z3c.dav.interfaces.IWebDAVMethod)
    component.adapts(interface.Interface, z3c.dav.interfaces.IWebDAVRequest)
    
    def PROPFIND(self):
        """Checks whether the request is from a MS WebFolder.
        
        Raises an authentication prompt in order to ensure that
        the objects are locked and writeable.
        """
        
        if self.request['HTTP_USER_AGENT'] == MS_WEBFOLDER:
            print "USER", self.request.principal.id
            if IReadDirectory(self.context, None) is None:
               # skips all directories: only files are locked with this patch
                if IUnauthenticatedPrincipal.providedBy(self.request.principal):
                    response = self.request.response
                    response.setHeader("MS-Author-Via", "DAV")
                    response.setHeader("WWW-Authenticate", 'Negotiate')
                                  #  'basic realm="Zope"')
                    print "raise Unauthorized", self.request.principal.id
                    raise Unauthorized
        
        return super(PROPFINDPATCH, self).PROPFIND()