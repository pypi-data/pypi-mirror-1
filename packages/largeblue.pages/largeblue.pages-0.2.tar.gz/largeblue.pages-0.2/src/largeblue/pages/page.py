import logging

from zope.app import zapi
from zope.app.container.btree import BTreeContainer
from zope.app.container.contained import Contained
from zope.app.file.file import File as BaseFile
from zope.component import adapts, getUtility, createObject
from zope.component.factory import Factory
from zope.event import notify
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.interface import implements

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("largeblue")

from bebop.ordering.interfaces import IOrdering

from interfaces import IPage, IBasePage, IPageContainer, IFile, ISelfIndexing
from interfaces import IContainedWithinAPageContainer, IContainedWithinAPage


class Page(BTreeContainer):
    implements(
        IBasePage,
        IPage,
        IPageContainer,
        IContainedWithinAPageContainer
    )
    __name__ = u'page'
    __parent__ = None
    title = u''
    flag = _(u'Static')
    
    def get_content(self):
        if self.has_key('main_content.html'):
            html_file = self['main_content.html']
            if IFile.providedBy(html_file):
                return html_file.data
        return u''
    
    def set_content(self, data):
        done = False
        if self.has_key('main_content.html'):
            html_file = self['main_content.html']
            if IFile.providedBy(html_file):
                html_file.data = data
                done = True
                notify(
                    ObjectModifiedEvent(
                        html_file,
                        Attributes(IFile, 'data')
                    )
                )
        if not done:
            html_file = createObject('largeblue.pages.File')
            html_file.contentType = 'text/html'
            html_file.__name__ = 'main_content.html'
            html_file.data = data
            notify(ObjectCreatedEvent(html_file))
            self['main_content.html'] = html_file
    
    content = property(get_content, set_content)


pageFactory = Factory(
    Page,
    title = _(u'Create Page'),
    description = u''
)

class PageContainer(BTreeContainer):
    implements(IPageContainer, ISelfIndexing)
    index = []
    def _recursively_collect(self, container):
        pages = []
        for k, v in IOrdering(container).items():
            page = v.context
            item = {
                'label': page.__name__,
                'title': page.title,
                'pages': self._recursively_collect(page)
            }
            pages.append(item)
        return pages
    
    def reindex(self):
        self.index = self._recursively_collect(self)
    


class File(BaseFile):
    implements(IFile, IContainedWithinAPage)
    __name__ = __parent__ = None


fileFactory = Factory(
    File,
    title = _(u'Create Sub Page Container'),
    description = u''
)