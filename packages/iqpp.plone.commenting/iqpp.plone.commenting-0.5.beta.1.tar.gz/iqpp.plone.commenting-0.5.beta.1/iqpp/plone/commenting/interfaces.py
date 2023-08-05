# zope imports
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import Interface
from zope.interface import Attribute
from zope.viewlet.interfaces import IViewletManager

# iqpp.plone.commentings imports
from config import *

_ = MessageFactory("iqpp.plone.commenting")


class ICommentable(IAttributeAnnotatable):
    """A marker interface to mark an object as commentable.
    """

class IComment(Interface):
    """Represents a comment.
    """

    id = schema.TextLine(
        title=_(u"id"),
        description=_(u"The id of comment. Must be unique"),
        required=True)

    reply_to = schema.TextLine(
        title=_(u"reply_to"),
        description=_(u"The id of the item that this comment relates to"),
        default=u"",
        required=False)

    member_id = schema.TextLine(
        title=_(u"member_id"),
        description=_(u"The id of the member that created this comment (if not anonymous)"),
        default=None,
        required=False)

    name = schema.TextLine(
        title=_(u"Name"),
        description=_(u"Your Fullname"),
        default=u"",
        required=False)

    email = schema.TextLine(
        title=_(u"E-Mail"),
        description=_(u"Your E-Mail"),
        default=u"",
        required=False)

    subject = schema.TextLine(
        title=_(u"Subject"),
        description=_(u"The subject of the comment"),
        default=u"",
        required=True)

    message = schema.Text(
        title=_(u"Message"),
        description=_(u"The message of the comment."),
        default=u"",
        required=True)
        
    transformed_message = schema.Text(
        title=_(u"Transformed Message"),
        description=_(u"The message of the comment, transformed to be safe."),
        required=False)
        
    review_state = schema.Choice(
        title=_(u"Review state"),
        description=_(u"The state of the comment (pending, published, rejected)"),
        values=REVIEW_STATES,
        default=u"private",
        required=True)

    created = schema.Datetime(
        title=_(u"Date created"),
        required=True,
    )

    modified = schema.Datetime(
        title=_(u"Date modified"),
        required=True,
    )

    # TODO: the following should really be handled by portal_workflow! [tomster]
    def submit(self):
        """submit the comment -> new review_state is 'pending'"""

    def reject(self):
        """reject the comment -> new review_state is 'private'"""

    def publish(self):
        """reject the comment -> new review_state is 'published'"""


class ICommentTransformations(Interface):
    """
    """
    def transformMessage():
        """Transforms a comment's message to arbitrary format. For instance
        to save html.
        """

class IGlobalCommenting(Interface):
    """Provides Methods for global commenting management.
    """
    def getPendingComments():
        """Returns all pending comments of a site.
        """
    
    def getCommentsForMember(member_id):
        """Returns all comments for member with given member_id.
        """
            
class ICommenting(Interface):
    """A interface which provides methods to manage comments for arbitrary 
    objects.
    """

    def addComment(reply_to, subject, message, member_id=None, name=None, email=None):
        """Adds a comment.
        """
        
    def deleteComment(id):
        """Deletes a comment by given unique id and its replies.
        """

    def deleteComments():
        """Deletes all comments of an object.
        """

    def editComment(id, subject, message):
        """Edits just the subject and the message of an comment. Used from
        members, which edit their own comments.
        """
        
    def getAllComments(id=None):
        """Returns all comments from object with given id. If id is None,
        returns all comments of the root object.
        """

    def getComment(id):
        """Returns a comment by given uniqe id.
        """

    def getComments(id=None):
        """Returns direct comments of object with given id. If id is None, 
        returns comments of root object.
        """

    def manageComment(id, reply_to, subject, message, member_id, name, email):
        """Manages all data of an a existing comment. Used from managers which 
        are allowed to change every piece of an comment.
        """

class ICommentingOptions(Interface):
    """
    """
    def getGlobalOption(name):
        """Decides from where the global option is taken. By default this is
        the value taken from the control panel.
        
        3rd-Party developer may overwrite this method to take it from 
        somewhere else, e.g. a product specific tool.
        """        
        
    def getEffectiveOption(name):
        """Returns the effective option with given name, which means: return
        the local one if there is one, otherwise the global.
        """    

    is_enabled = schema.Choice(
        title=_(u"Is enabled"),
        description =_(u"Are comments for this object enabled?"),
        vocabulary = schema.vocabulary.SimpleVocabulary.fromItems(
            DEFAULT_CHOICES),
        default="default")

    is_moderated = schema.Choice(
        title=_(u"Is moderated"),
        description =_(u"Are comments for this item moderated?"),
        vocabulary = schema.vocabulary.SimpleVocabulary.fromItems(
            DEFAULT_CHOICES),
        default="default")

    show_preview = schema.Choice(
        title=_(u"Show preview"),
        description =_(u"Must comments for this item be previewed prior to adding?"),
        vocabulary = schema.vocabulary.SimpleVocabulary.fromItems(
            DEFAULT_CHOICES),
        default="default"
    )

    edit_own_comments = schema.List(
        title=_(u"Owner can edit comments"),
        description=_(u"User is allowed to edit own comment for this item, when it is in one of selected states."),
        required=False,
        default=['default'],
        value_type = schema.Choice(
            __name__ = "edit_own_comments",
            title = u"Review State",            
            vocabulary = schema.vocabulary.SimpleVocabulary.fromItems(
                REVIEW_STATES_CHOICES)),
    )

    send_comment_added_mail = schema.Choice(
        title=_(u"Send email notifications"),
        description=_(u"Should an email be sent for every new comment on this item?"), 
        vocabulary = schema.vocabulary.SimpleVocabulary.fromItems(
            DEFAULT_CHOICES),
        default="default")

    mail_to = schema.TextLine(
        title=_(u"Email recipient address"), 
        description=_(u"The address to which notifications about new comments should be sent. Leave it blank to take the default recipient address."), 
        default=_(u""),
        required=False,
    )

    mail_from = schema.TextLine(
        title=_(u"Email sender address"), 
        description=_(u"The email address that will be used as sender for mails notifying about a new comment. Leave it blank to take the default sender address."),
        default=_(u""),
        required=False,
    )
            
class ICommentAddedEvent(Interface):
    """An event for: Comment has been added.
    """    
    context = Attribute("The object which has been commented.")
    comment = Attribute("The new comment")

class ICommentingViewletManager(IViewletManager):
    """
    """