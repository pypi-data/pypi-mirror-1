# python imports
from datetime import datetime

# zope imports
from persistent import Persistent
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# CMFPlone imports
from Products.CMFPlone.utils import safe_unicode

# iqpp.plone.commenting imports
from iqpp.plone.commenting.config import REVIEW_STATES
from iqpp.plone.commenting.interfaces import IComment
from iqpp.plone.commenting.interfaces import ICommentAddedEvent

class Comment(Persistent):
    """A comment. 
    """    
    implements(IComment)

    id = FieldProperty(IComment['id'])
    reply_to = FieldProperty(IComment['reply_to'])
    member_id = FieldProperty(IComment['member_id'])
    name = FieldProperty(IComment['name'])
    email = FieldProperty(IComment['email'])
    subject = FieldProperty(IComment['subject'])
    message = FieldProperty(IComment['message'])
    transformed_message = FieldProperty(IComment['transformed_message'])
    review_state = FieldProperty(IComment['review_state'])
    created = FieldProperty(IComment['created'])
    modified = FieldProperty(IComment['modified'])
        
    def __init__(self, id, reply_to, subject, message, member_id=u"",
                       name=u"", email=u"", review_state=u"pending"):
        """
        """
        self.id = safe_unicode(id)
        self.reply_to = safe_unicode(reply_to)
        self.member_id = safe_unicode(member_id)
        self.name = safe_unicode(name)
        self.email = safe_unicode(email)
        self.subject = safe_unicode(subject)
        self.message = safe_unicode(message)
        self.transformed_message = u""
        self.review_state = review_state
        self.created = datetime.now()
        self.modified = datetime.now()
        
    def UID(self):
        """
        """
        return self.id

    def publish(self):
        self.review_state = u"published"
        assert(self.review_state in REVIEW_STATES)
    
    def reject(self):
        self.review_state = u"private"
        assert(self.review_state in REVIEW_STATES)
    
    def submit(self):
        self.review_state = u"pending"
        assert(self.review_state in REVIEW_STATES)
        
class CommentAddedEvent(object):
    """An event which is sent when a comment has been added.
    """
    implements(ICommentAddedEvent)
    
    def __init__(self, context, comment):
        """
        """
        # Passing the context (the ICommentable) to the subscribers enables
        # people to get to the commenting options within one of them.
        self.context = context
        self.comment = comment