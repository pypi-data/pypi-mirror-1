# zope imports
from zope.app.form.browser import MultiSelectWidget
from zope.formlib import form

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("iqpp.plone.commenting")

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# Five imports
from Products.Five.formlib import formbase
from Products.Five.browser import pagetemplatefile

# iqpp.rating imports
from iqpp.plone.commenting.config import *
from iqpp.plone.commenting.interfaces import ICommentingOptions

class MyMultiSelectWidget(MultiSelectWidget):

    def __init__(self, field, request):
        """
        """
        super(MyMultiSelectWidget, self).__init__(
            field, field.value_type.vocabulary, request)
    
class CommentingOptionsTab(formbase.EditForm):
    """
    """
    form_fields = form.FormFields(ICommentingOptions)
    form_fields["edit_own_comments"].custom_widget = MyMultiSelectWidget
    template = pagetemplatefile.ZopeTwoPageTemplateFile("options_tab.pt")
    
    @form.action("add")
    def action_add(self, action, data):
        """
        """
        ro = ICommentingOptions(self.context)

        for field in self.form_fields:
            # Set fields
            name = field.__name__
            if name in data.keys():
                setattr(ro, name, data[name])

        # TODO: for any reason addPortalMessage is not working (means the
        # message is not displayed.)
        ptool = getToolByName(self.context, "plone_utils")
        ptool.addPortalMessage(MESSAGES["options-saved"])
                
        url = self.context.absolute_url() + "/commenting-options"
        self.request.response.redirect(url)