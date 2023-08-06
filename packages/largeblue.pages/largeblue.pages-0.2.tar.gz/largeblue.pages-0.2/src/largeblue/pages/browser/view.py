import logging

from zope.app.form.interfaces import ConversionError
from zope.formlib.form import EditForm, AddForm, Fields, applyChanges
from zope.component import createObject

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("largeblue")

from largeblue.pages.interfaces import IPage

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
