# python imports
from random import random

# Zope imports 
from AccessControl import Unauthorized
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from datetime import datetime

# zope imports
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.event import notify        
from zope.interface import implements
from zope.interface import Interface

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# CMFPlone imports
from Products.CMFPlone.utils import safe_unicode

# iqpp.plone.commenting imports
from iqpp.plone.commenting.content import Comment
from iqpp.plone.commenting.content import CommentAddedEvent
from iqpp.plone.commenting.interfaces import ICommenting
from iqpp.plone.commenting.interfaces import ICommentingOptions
from iqpp.plone.commenting.interfaces import ICommentTransformations
from iqpp.plone.commenting.interfaces import ICommentable
from iqpp.plone.commenting.interfaces import IGlobalCommenting

KEY = "iqpp.plone.commenting"

# TODO: Should this rather be a utility?
class GlobalCommenting(object):
    """
    """
    implements(IGlobalCommenting)
    adapts(Interface)

    def __init__(self, context):
        """
        """
        self.context = context
    
    def getCommentsForMember(self, member_id=None):
        """
        """
        if member_id is None:
            mtool = getToolByName(self.context, "portal_membership")
            member_id = mtool.getAuthenticatedMember().getId()
        
        result = []
        for comment in self.comments.values():
            if comment.member_id == member_id:
               result.append(comment)

        result.sort(lambda a, b: cmp(b.created, a.created))
        return result
        
    def getPendingComments(self):
        """
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(
            object_provides = "iqpp.plone.commenting.interfaces.ICommentable"
        )
    
        result = []
        for brain in brains:
            # catch "missing.value" in brain.comments
            if isinstance(getattr(brain, "pending_comments", None), list):
                for comment_id in brain.pending_comments:
                
                    c = ICommenting(brain.getObject())
                    comment = c.getComment(comment_id)
                
                    result.append({
                        "object_url" : brain.getURL(),
                        "comment_id" : comment_id,
                        "subject"    : comment.subject,
                        "created"    : comment.created,
                    })

        result.sort(lambda a, b: cmp(b["created"], a["created"]))
        return result    
        
class Commenting(object):
    """An adapter, which provides commenting for commentable objects.
    """
    implements(ICommenting)
    adapts(ICommentable)

    def __init__(self, context):
        """
        """
        self.context = context

        annotations = IAnnotations(context)
        comments = annotations.get(KEY)
        
        if comments is None:
            comments = annotations[KEY] = OOBTree()

        self.comments = comments

    def addComment(self, reply_to, subject, message, member_id="", name="", email="", notify_=True):
        """
        """
        new_id = self._generateUniqueId()
            
        # create comment
        new_comment = Comment(new_id, reply_to, subject, message, member_id,
                              name, email)

        options = ICommentingOptions(self.context)
        if options.getEffectiveOption("is_moderated"):
            new_comment.submit()
        else:
            new_comment.publish()

        self.comments[new_id] = new_comment

        # transform message
        transformer = ICommentTransformations(self.comments[new_id])
        transformer.transformMessage()
        
        # make the catalog happy
        self.context.reindexObject()

        # make the subscribers happy
        if notify_:
            notify(CommentAddedEvent(self.context, new_comment))
    
        # make the caller happy ;-)
        return new_comment

    def deleteComment(self, id):
        """
        """
        try:
            del self.comments[id]
            self.context.reindexObject()            
        except KeyError:
            return False
        else:
            for comment in self.comments.values():
                if comment.reply_to == id:
                    self.deleteComment(comment.id)
            return True
            
    def deleteComments(self):
        """
        """
        self.comments.clear()
        self.context.reindexObject()
        
    def getAllComments(self, id=None):
        """
        """
        # Todo: implement for given id
        if id is None:
            return self.comments.values()
        else:
            raise "Not implemented yet."

    def getComment(self, id):
        """
        """
        try:
            return self.comments[id]
        except KeyError:
            return None

    def getComments(self, id="", reverse=False):
        """
        """
        result = []
        for comment in self.comments.values():
            if comment.reply_to == id:
               result.append(comment)

        if reverse == True:
            result.sort(lambda a, b: cmp(b.created, a.created))
        else:
            result.sort(lambda a, b: cmp(a.created, b.created))
            
        return result
            
    def manageComment(self, comment_id, reply_to=None, subject=None, message=None,
        member_id=None, name=None, email=None, review_state=None):
        """
        """
        def conditionalAssignment(comment, field, value):
            if value is not None:
                setattr(comment, field, safe_unicode(value))
        
        comment = self.getComment(comment_id)        

        conditionalAssignment(comment, 'reply_to', reply_to)
        conditionalAssignment(comment, 'subject', subject)
        conditionalAssignment(comment, 'message', message)
        conditionalAssignment(comment, 'member_id', member_id)
        conditionalAssignment(comment, 'name', name)
        conditionalAssignment(comment, 'email', email)
        conditionalAssignment(comment, 'review_state', review_state)
        comment.modified = datetime.now()

        # transform message
        transformer = ICommentTransformations(comment)
        transformer.transformMessage()
        
        self.context.reindexObject()
        return comment

    def editComment(self, comment_id, subject, message):
        """
        """
        comment = self.getComment(comment_id)
                
        comment.subject = safe_unicode(subject)
        comment.message = safe_unicode(message)

        # transform message
        transformer = ICommentTransformations(comment)
        transformer.transformMessage()
        
        self.context.reindexObject()
        return comment

    def publishComment(self, id):
        """
        """
        try:
            comment = self.getComment(id)
            comment.publish()
            self.context.reindexObject()
            return True
        except KeyError:
            return False
        
    def rejectComment(self, id):
        """
        """
        try:
            comment = self.getComment(id)
            comment.reject()
            self.context.reindexObject()                        
            return True
        except KeyError:
            return False

    def _generateUniqueId(self):
        """Generates a unique id
        """
        now  = DateTime()
        time = '%s.%s' % (now.strftime('%Y-%m-%d'), str(now.millis())[7:])
        rand = str(random())[2:6]

        return unicode("comment."+time+rand)