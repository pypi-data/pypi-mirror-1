from zope.i18nmessageid import MessageFactory
_ = MessageFactory("iqpp.plone.commenting")

# Five imports
from Products.Five.browser import BrowserView

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.commenting imports
from iqpp.plone.commenting.config import MESSAGES, REVIEW_STATES
from iqpp.plone.commenting.interfaces import ICommenting

class ManageCommentFormView(BrowserView):
    """
    """    
    def manageComment(self):
        """
        """
        utils = getToolByName(self.context, "plone_utils")
                    
        comment_id   = self.request.get("comment_id")
        reply_to     = self.request.get("reply_to")
        name         = self.request.get("name")
        email        = self.request.get("email")
        subject      = self.request.get("subject")
        message      = self.request.get("message")
        member_id    = self.request.get("member_id")
        review_state = self.request.get("review_state")
    
        manager = ICommenting(self.context)    
        result = manager.manageComment(
            comment_id = comment_id,
            reply_to = reply_to, 
            name = name,
            email = email,
            subject = subject,
            message = message,
            member_id = member_id,
            review_state = review_state,
        )

        if result == True:
            utils.addPortalMessage(_(MESSAGES["comment-modified"]))
        else:
            utils.addPortalMessage(_(MESSAGES["comment-not-modified"]))
            
        url = self.context.absolute_url()
        self.request.response.redirect(url)
    
    def getComment(self):
        """
        """
        comment_id = self.request.get("comment_id")
        
        manager = ICommenting(self.context)
        comment = manager.getComment(comment_id)
        
        return {
            "id"           : comment.id,
            "name"         : comment.name,
            "email"        : comment.email,
            "subject"      : comment.subject,
            "message"      : comment.message,
            "reply_to"     : comment.reply_to,
            "member_id"    : comment.member_id,
            "review_state" : comment.review_state,
        }
        
    def getReviewStates(self):
        """
        """
        return REVIEW_STATES            

