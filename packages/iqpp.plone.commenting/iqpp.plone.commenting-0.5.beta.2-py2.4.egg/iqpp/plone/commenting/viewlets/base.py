# iqpp.plone.commenting imports
from iqpp.plone.commenting.interfaces import ICommentingOptions

class CommentingViewletsBase(object):
    """
    """
    @property
    def available(self):
        """
        """
        co = ICommentingOptions(self.context)
        if co.getEffectiveOption("is_enabled") == False:
            return False
        
        return True