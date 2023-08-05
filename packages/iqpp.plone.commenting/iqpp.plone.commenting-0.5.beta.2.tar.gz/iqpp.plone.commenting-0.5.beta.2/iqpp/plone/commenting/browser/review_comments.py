# zope imports
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("iqpp.plone.commenting")

# Five imports
from Products.Five.browser import BrowserView

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.commenting imports
from iqpp.plone.commenting.config import MESSAGES
from iqpp.plone.commenting.interfaces import ICommenting

class ReviewCommentsView(BrowserView):
    """Provides methods to review comments.
    """    

    def publishComment(self):
        """
        """
        ptool = getToolByName(self.context, "plone_utils")
        comment_id = self.request.get("comment_id")

        commenting = ICommenting(self.context)
        result = commenting.publishComment(comment_id)

        if result:
            ptool.addPortalMessage(_(MESSAGES["comment-published"]))
        else:
            ptool.addPortalMessage(_(MESSAGES["comment-not-published"]))

        self._redirect()

    def rejectComment(self):
        """
        """
        ptool = getToolByName(self.context, "plone_utils")
        comment_id = self.request.get("comment_id")

        commenting = ICommenting(self.context)
        result = commenting.rejectComment(comment_id)

        if result:
            ptool.addPortalMessage(_(MESSAGES["comment-rejected"]))
        else:
            ptool.addPortalMessage(_(MESSAGES["comment-not-rejected"]))

        self._redirect()

    def _redirect(self):
        """
        """
        url = self.context.absolute_url()
        b_start = self.request.get("b_start", None)
        if b_start is not None:
            url = "%s?b_start:int=%d" % (url, b_start)
        self.request.response.redirect(url)