import urllib

from zope.app import zapi
from zope.app.container.browser.contents import Contents
from zope.app.container.interfaces import IContainerNamesContainer
from zope.exceptions.interfaces import UserError

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("largeblue")

from bebop.ordering.interfaces import IOrderable, IOrdering

from largeblue.pages.schema import InvalidObjectName, _is_valid_obj_name
from largeblue.pages.order.ordering import Ordering


class OrderingView(Contents):
    error = ''
    def __init__(self,context,request):
        super(OrderingView,self).__init__(context, request)
        self.orderingcontext = IOrdering(context)
    
    def renameObjects(self):
        """
          
          We override this method to manually make sure that the
          new name(s) is/are valid before renaming the page(s)
          
          
        """
        
        for name in self.request.get("new_value"):
            if not _is_valid_obj_name(name):
                raise UserError(
                    '%s: %s' % (
                        _(u'Object name invalid'),
                        InvalidObjectName.__doc__
                    )
                )
        super(OrderingView, self).renameObjects()
    
    def _normalListContentsInfo(self):
        request = self.request
        ordering = self.orderingcontext
        self.specialButtons = (
            'type_name' in request or
            'rename_ids' in request or (
                'container_rename_button' in request
                and request.get("ids")
            ) or
           'retitle_id' in request
        )
        self.normalButtons = not self.specialButtons
        flag = bool(len(ordering))
        self.supportsCut = flag
        self.supportsCopy = flag
        self.supportsDelete = flag
        self.supportsPaste = self.pasteable()
        self.supportsRename = (
            self.supportsCut and
            not IContainerNamesContainer.providedBy(
                self.context
            )
        )
        # retrieve requested action
        action = None
        if u"orderable_up" in request:
            action = ordering.upOne
        elif u"orderable_top" in request:
            action = ordering.goTop
        elif u"orderable_down" in request:
            action = ordering.downOne
        elif u"orderable_bottom" in request:
            action = ordering.goBottom
        # perform moving action if ids are selected and an action 
        # indicator was in request
        #ids = [int(x) for x in request.get('ids')]
        ids = request.get('ids')
        if action:
            if not ids:
                self.error = _("You didn't specify any ids to remove.")
                return
            sorted_names = ordering.getNames()
            names = ids
            ids = []
            for name in names:
                ids.append(
                    sorted_names.index(name)
                )
            action([int(x) for x in ids]) #perform moving action 
        # return the dicts for the view pt in correct order
        # like _normallistcontents
        for n in range(len(self.context)):
            item = ordering.getItemFromPosition(n) #self.items[n]
            if item:
                context = item.__parent__
                info = self._extractContentInfo((context.__name__, item))
                zmi_icon = zapi.queryMultiAdapter((context, self.request), name='zmi_icon')
                if zmi_icon is not None:
                    zmi_icon = zmi_icon()
                info['cb_id'] = item.getOrder() #checkboxid
                info['url'] = zapi.absoluteURL(context, self.request)
                info['icon'] = zmi_icon
                yield info
                #dict(
                #    id = context.__name__,   #items name
                #    cb_id = item.getOrder(), #checkboxid
                #    url = zapi.absoluteURL(context, self.request),
                #    icon = zmi_icon
                #)
            
        
    

