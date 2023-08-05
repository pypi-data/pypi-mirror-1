# plone imports
from plone.app.layout.viewlets.common import ViewletBase

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.commenting imports
from iqpp.plone.commenting.viewlets.base import CommentingViewletsBase

class AddCommentButtonViewlet(ViewletBase, CommentingViewletsBase):
    """
    """
    render = ViewPageTemplateFile('add_comment_button.pt')
    
    def showAddButton(self):
        """
        """
        mtool = getToolByName(self.context, "portal_membership")
        return mtool.checkPermission("Reply to item", self.context)

            