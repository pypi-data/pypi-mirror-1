# Five imports
from Products.Five.browser import BrowserView

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.commenting imports
from iqpp.plone.commenting import utils
from iqpp.plone.commenting.interfaces import IGlobalCommenting

class MyCommentsView(BrowserView):
    """
    """
    def getCommentsForMember(self, member_id=None):
        """
        """
        mtool = getToolByName(self.context, "portal_membership")
        cm = IGlobalCommenting(self.context)
        comments =  cm.getCommentsForMember(member_id)

        result = []
        for i, comment in enumerate(comments):
            
            if mtool.checkPermission("Manage portal", self.context) is None and \
               comment.review_state != "published":
                continue
                   
            if i % 2 == 0:
                css_class = "even"
            else:
                css_class = "odd"
            
            member_info = utils.getMemberInfo(
                self.context, 
                comment.member_id, 
                comment.name, 
                comment.email
            )
            
            result.append({
                "id"                  : comment.id,
                "subject"             : comment.subject,
                "message"             : comment.message,
                "transformed_message" : comment.transformed_message,
                "name"                : member_info["name"],
                "email"               : member_info["email"],
                "css_class"           : css_class,
                "review_state"        : comment.review_state,
                "created"             : comment.created,
                "member_id"           : comment.member_id,
            })
        
        return result
        
