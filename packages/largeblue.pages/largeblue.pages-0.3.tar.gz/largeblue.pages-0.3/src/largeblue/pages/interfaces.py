from zope.interface import Interface, Attribute
from zope.schema import Choice, Field, List, Text, TextLine
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.interfaces import IContained, IContainer
from zope.app.file.interfaces import IFile as IBaseFile

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("largeblue")

from schema import ObjectName


class IBasePage(IContainer):
    __name__ = ObjectName(
        title = _(u"Object Name"),
        description = _(u"The name as it appears in the object's URL.  Must be lowercase letter and numbers, with no white spaces.  Full stop '.' and underscore '_' characters are allowed"),
        default = u"page",
        required = True
    )
    title = TextLine(
        title = _(u"Human Friendly Title"),
        description = _(u"The title of the page, usually displayed in the top bar of the web browser and possible on the page as a main heading"),
        default = u"",
        required = True
    )
    flag = Choice(
        title = _(u"Page Type"),
        description = _(u"This is a (hopefully flexible) flag used to determine how to render it.  Typically, if 'static', then the Main Content (edited below) is simply rendered"),
        required = True,
        default = _(u'Static'),
        values = [
            _(u'Static'),
            _(u'Template'),
            _(u'Special')
        ]
    )
    content = Text(
        title = _(u"Main Content"),
        description = _(u"The content of the page, usually rendered in the main content area of the page, or, if the page is dynamic or special, then it may still be pulled into a sub part of the page"),
        default = u"",
        required = False
    )


class IPageContainer(IContainer):
    def __setitem__(name, obj):
        pass
    
    __setitem__.precondition = ItemTypePrecondition(IBasePage)
    


class IFile(IBaseFile):
    pass


class IPage(IBasePage):
    def __setitem__(name, obj):
        pass
    __setitem__.precondition = ItemTypePrecondition(
        IBasePage, IFile
    )


class IContainedWithinAPageContainer(IContained):
    __parent__ = Field(
        constraint = ContainerTypesConstraint(
            IPageContainer
        )
    )


class IContainedWithinAPage(IContained):
    __parent__ = Field(
        constraint = ContainerTypesConstraint(
            IPage
        )
    )


class ISelfIndexing(Interface):
    index = List(
        title = _(u"Index"),
        description = _(u"Cached index, used here to store a copy of the contained pages, so it doesn't have to be created each time it's looked up"),
        default = [],
        required = False
    )
    def reindex(self):
        pass
    


class ISelfIndexingPageContainer(IPageContainer, ISelfIndexing):
    pass


class IPageStructureNeedsReindexEvent(Interface):
    obj = Attribute(_(u'Page'))
