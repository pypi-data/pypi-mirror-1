import logging

from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.form.interfaces import ConversionError
from zope.component import adapter, createObject
from zope.event import notify
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.security.proxy import removeSecurityProxy

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("largeblue")

from event import PageStructureNeedsReindex
from interfaces import IPage, IPageContainer, IFile, ISelfIndexing
from interfaces import IPageStructureNeedsReindexEvent


def is_page_container(obj):
    return IPageContainer.providedBy(obj) and not IPage.providedBy(obj)


def get_page_container(obj):
    if is_page_container(obj):
        return obj
    return hasattr(obj, '__parent__') and get_page_container(obj.__parent__) or None


@adapter(IObjectCreatedEvent)
def handle_created(event):
    obj = event.object
    if IPage.providedBy(obj):
        if not obj.has_key('main_content.html'):
            # create an html file called main content
            html_file = createObject('largeblue.pages.File')
            html_file.contentType = 'text/html'
            html_file.data = '<div>%s</div>' % _('Under construction')
            html_file.__name__ = 'main_content.html'
            notify(
                ObjectCreatedEvent(html_file)
            )
            obj['main_content.html'] = html_file
        
    


@adapter(IObjectModifiedEvent)
def handle_modified(event):
    obj = event.object
    if IPage.providedBy(obj):
        logging.info('page modified %s' % obj.__name__)
        notify(
            PageStructureNeedsReindex(
                get_page_container(obj)
            )
        )
    elif IPageContainer.providedBy(obj):
        logging.info('page container modified %s' % obj.__name__)
        notify(
            PageStructureNeedsReindex(obj)
        )
    elif IFile.providedBy(obj):
        parent = removeSecurityProxy(obj.__parent__)
        notify(
            ObjectModifiedEvent(
                parent,
                Attributes(IPage, 'content')
            )
        )
    


@adapter(IObjectAddedEvent)
def handle_added(event):
    obj = event.object
    obj_name = event.newName
    container = event.newParent
    if IPageContainer.providedBy(container):
        notify(
            PageStructureNeedsReindex(
                get_page_container(container)
            )
        )
    


@adapter(IObjectRemovedEvent)
def handle_deleted(event):
    obj = event.object
    obj_name = event.oldName
    container = event.oldParent
    if IPageContainer.providedBy(container):
        notify(
            PageStructureNeedsReindex(
                get_page_container(container)
            )
        )
    


@adapter(IPageStructureNeedsReindexEvent)
def handle_reindex(event):
    target = event.obj
    if ISelfIndexing.providedBy(target):
        target.reindex()

