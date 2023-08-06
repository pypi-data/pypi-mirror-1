from zope.app.form.interfaces import ConversionError
from zope.component import createObject
from zope.exceptions.interfaces import UserError
from zope.formlib.form import EditForm, AddForm, Fields, applyChanges

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("largeblue")

from bebop.ordering.interfaces import IOrderable, IOrdering

from largeblue.order.browser.view import OrderingView as DefaultOrderingView
from largeblue.order.ordering import Ordering

from largeblue.pages.interfaces import IPage
from largeblue.pages.schema import InvalidObjectName, _is_valid_obj_name

from widget import WYSIWYG


class PageAddForm(AddForm):
    form_fields = Fields(IPage).select('__name__', 'title', 'flag')
    label = _(u'Add Page')
    def create(self, data):
        self.context.contentName = data.get('__name__', u'')
        obj = createObject(u'largeblue.pages.Page')
        applyChanges(obj, self.form_fields, data)
        return obj
    


class PageEditForm(EditForm):
    form_fields = Fields(IPage).select('title', 'content')
    form_fields['content'].custom_widget = WYSIWYG
    label = _(u"Edit Page")


class OrderingView(DefaultOrderingView):
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
    
