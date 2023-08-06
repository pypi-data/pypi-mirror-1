from zope.interface import implements

from interfaces import IPageStructureNeedsReindexEvent


class PageStructureNeedsReindex(object):
    implements(IPageStructureNeedsReindexEvent)
    def __init__(self, page_obj):
        self.obj = page_obj
    

