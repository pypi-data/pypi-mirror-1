# python
from datetime import datetime
from datetime import timedelta

# plone imports
from plone.app.layout.viewlets.common import ViewletBase

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.commenting imports
from iqpp.plone.commenting import utils
from iqpp.plone.commenting.interfaces import ICommenting
from iqpp.plone.commenting.interfaces import ICommentingOptions
from iqpp.plone.commenting.viewlets.base import CommentingViewletsBase

class CommentsViewlet(ViewletBase, CommentingViewletsBase):
    """
    """
    render = ViewPageTemplateFile('comments.pt')

    def __init__(self, context, request, view, manager):
        """
        """
        super(CommentsViewlet, self).__init__(context, request, view, manager)
        self.mtool = getToolByName(context, "portal_membership")

    def getComments(self, id=""):
        """Returns all comments of context.
        """
        # return top level comments in reverse chronological order
        # (latest first) and replies in chronological order (latest last)
        if id is None:
            id = ""
            reverse = True            
        else:
            reverse = False
            
        mtool = getToolByName(self.context, "portal_membership")
        auth_member_id = mtool.getAuthenticatedMember().getId()
            
        comments = ICommenting(self.context).getComments(id, reverse=reverse)
        
        result = []
        i = 0
        for comment in comments:

            if (comment.review_state == "published") or \
               (comment.member_id and comment.member_id == auth_member_id) or \
               (self.mtool.checkPermission("Manage comments", self.context) == True):
                   
                member_info = utils.getMemberInfo(
                    self.context, 
                    comment.member_id, 
                    comment.name, 
                    comment.email
                )

                if i % 2 == 0:
                    klass = "comment even"
                else:
                    klass = "comment odd"
                i += 1
                                
                if member_info["is_manager"] == True:
                    klass = klass + " manager"
            
                tool = getToolByName(self.context, 'translation_service')
                created_local = tool.ulocalized_time(
                    comment.created.isoformat(),
                    long_format=True)
            
                result.append({
                    "id"                  : comment.id,
                    "subject"             : comment.subject,
                    "message"             : comment.message,
                    "transformed_message" : comment.transformed_message,
                    "name"                : member_info["name"],
                    "email"               : member_info["email"],
                    "class"               : klass,
                    "review_state"        : comment.review_state,
                    "created"             : comment.created,
                    "created_local"       : created_local,
                    "member_id"           : comment.member_id,
                    "show_delete_button"  : self._showDeleteButton(),
                    "show_edit_button"    : self._showEditButton(comment),
                    "show_manage_button"  : self._showManageButton(),
                    "show_publish_button" : self._showPublishButton(comment),
                    "show_reject_button"  : self._showRejectButton(comment),
                    "show_reply_button"   : self._showReplyButton(comment),
                })
        
        return result

    def _showEditButton(self, comment):
        """Returns True when the user is allowed to edit given comment.
        """                
        # The edit button is shown for the owner of the comment 
        # Note: edit button and manage button are mutually exclusive.
        
        options = ICommentingOptions(self.context)
        edit_own_comments = options.getEffectiveOption("edit_own_comments")
        
        if self._showManageButton() == True:
            return False 

        if comment.member_id is not None and \
           comment.member_id == self.mtool.getAuthenticatedMember().getId() and \
           comment.review_state in edit_own_comments:
            return True
        else:           
            return False

    def _showDeleteButton(self):
        """Returns True if the authenticated user is allowed to delete a 
        comment.
        """
        if self.mtool.checkPermission("Delete comments", self.context) == True:
            return True

        return False
                
    def _showManageButton(self):
        """Returns True if the authenticated user is allowed to manage a 
        comment.
        """
        # The manage button leads to the manage comment form, which lets a
        # allowed person edit all comment info without preview, validation, 
        # etc.
        
        if self.mtool.checkPermission("Manage comments", self.context) == True:
            return True
        else:
            return False

    def _showPublishButton(self, comment):
        """Returns True if the comment is able and allowed to be published.
        """        
        if self.mtool.checkPermission("Review comments", self.context) == True and\
           comment.review_state != "published":
            return True        
        else:    
            return False

    def _showRejectButton(self, comment):
        """Returns True if the comment is able and allowed to be rejected.
        """        
        if self.mtool.checkPermission("Review comments", self.context) == True and\
           comment.review_state != "private":
            return True
        else:        
            return False
                
    def _showReplyButton(self, comment):
        """Returns True if the authenticated user is allowed to reply to 
        context.
        """
        # There are different permission for adding a comment to a content 
        # object and comment. In this way the site owner could decide whether
        # she allows threads (comments of comments) or not.

        # context is no comment
        if comment.reply_to is None:
            if self.mtool.checkPermission("Reply to item", self.context) == True:
                return True
        else:
            if self.mtool.checkPermission("Reply to comment", self.context) == True:
                return True            
        return False