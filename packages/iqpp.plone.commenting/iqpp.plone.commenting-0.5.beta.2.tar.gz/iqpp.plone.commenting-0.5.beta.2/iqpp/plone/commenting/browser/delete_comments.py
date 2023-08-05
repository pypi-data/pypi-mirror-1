# Zope imports
from DateTime import DateTime

# zope imports
from zope.interface import implements
from zope.interface import Interface

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("iqpp.plone.commenting")

# Five imports
from Products.Five.browser import BrowserView

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.commenting imports
from iqpp.plone.commenting import utils
from iqpp.plone.commenting.config import MESSAGES
from iqpp.plone.commenting.interfaces import ICommenting
from iqpp.plone.commenting.interfaces import ICommentingOptions

class DeleteCommentsView(BrowserView):
    """Provides Methods to delete comments.
    """    
    def deleteComment(self):
        """Deletes a comment with given comment_id (via request) of context.
        """
        ptool = getToolByName(self.context, "plone_utils")
        comment_id = self.request.get("comment_id")

        manager = ICommenting(self.context)
        result = manager.deleteComment(comment_id)

        if result == True:
            ptool.addPortalMessage(_(MESSAGES["comment-deleted"]))
        else:
            ptool.addPortalMessage(_(MESSAGES["comment-not-deleted"]))

        self._redirect()

    def deleteComments(self):
        """Deletes all comments of context.
        """    
        manager = ICommenting(self.context)
        manager.deleteComments()
        
        utils = getToolByName(self.context, "plone_utils")
        utils.addPortalMessage(_(MESSAGES["comments-deleted"]))
        
        self._redirect()

    def _redirect(self):
        """
        """
        url = self.context.absolute_url()
        b_start = self.request.get("b_start", None)
        if b_start is not None:
            url = "%s?b_start:int=%d" % (url, b_start)
        self.request.response.redirect(url)