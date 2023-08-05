# zope imports
from zope.app.form.browser import MultiSelectWidget
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
from zope.formlib import form
from zope import schema
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('iqpp.plone.commenting')

# CMF imports
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFPlone.interfaces import IPloneSiteRoot

# plone imports
from plone.app.controlpanel.form import ControlPanelForm

# iqpp.plone.commenting imports
from iqpp.plone.commenting.config import *

class IPloneCommentingControlPanel(Interface):
    """
    """
    is_enabled = schema.Bool(title=_(u"Is enabled"),
         description=_(u"Are comments enabled?"),
         default=True,
    )
    
    is_moderated = schema.Bool(title=_(u"Is moderated"),
         description=_(u"Are comments moderated?"),
         required=True,
         default=True,
    )

    show_preview = schema.Bool(
        title=_(u"Show Preview"),
        description=_(u"Must comments be previewed prior to adding?"),
        default=False,
    )

    edit_own_comments = schema.List(
        title=_(u"Owner can edit comments"),
        description=_(u"User is allowed to edit own comment, when it is in one of selected states."),
        required=False,
        value_type = schema.Choice(
            __name__ = "edit_own_comments",
            title = u"Review State",
            default=u"pending",
            vocabulary = schema.vocabulary.SimpleVocabulary.fromItems(
                REVIEW_STATES_CHOICES[1:])),
    )

    send_comment_added_mail = schema.Bool(
        title=_(u"Send email notifications?"), 
        description=_(u"Should an email be sent for every new comment?"), 
        default=False,
    )

    mail_from = schema.TextLine(
        title=_(u"Email sender address"), 
        description=_(u"The email address that will be used as sender for mails notifying about a new comment. Leave it blank to use Plone's global email address."), 
        default=_(u""),
        required=False,
    )

    mail_to = schema.TextLine(
        title=_(u"Email recipient address"), 
        description=_(u"The address to which notifications about new comments should be sent. Leave it blank to use Plone's global email address."), 
        default=_(u""),
        required=False,
    )

class MyMultiSelectWidget(MultiSelectWidget):

    def __init__(self, field, request):
        """
        """
        super(MyMultiSelectWidget, self).__init__(
            field, field.value_type.vocabulary, request)
            
class PloneCommentingControlPanelForm(ControlPanelForm):
    """
    """
    form_fields = form.Fields(IPloneCommentingControlPanel)
    form_fields["edit_own_comments"].custom_widget = MyMultiSelectWidget
    
    label = _(u"Commenting settings")
    description = _(u"Here you can set global commenting options.")
    form_name = _("Commenting settings")
    
class PloneCommentingControlPanelAdapter(SchemaAdapterBase):
    """
    """    
    implements(IPloneCommentingControlPanel)
    adapts(IPloneSiteRoot)
    
    def __init__(self, context):
        """
        """
        super(PloneCommentingControlPanelAdapter, self).__init__(context)
        
    edit_own_comments = ProxyFieldProperty(IPloneCommentingControlPanel['edit_own_comments'])
    is_enabled = ProxyFieldProperty(IPloneCommentingControlPanel['is_enabled'])
    is_moderated = ProxyFieldProperty(IPloneCommentingControlPanel['is_moderated'])
    show_preview = ProxyFieldProperty(IPloneCommentingControlPanel['show_preview'])
    send_comment_added_mail = ProxyFieldProperty(IPloneCommentingControlPanel['send_comment_added_mail'])
    mail_to = ProxyFieldProperty(IPloneCommentingControlPanel['mail_to'])
    mail_from = ProxyFieldProperty(IPloneCommentingControlPanel['mail_from'])