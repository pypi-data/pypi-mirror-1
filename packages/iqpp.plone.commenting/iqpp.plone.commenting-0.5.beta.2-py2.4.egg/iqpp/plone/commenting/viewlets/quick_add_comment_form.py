# plone imports
from plone.app.layout.viewlets.common import ViewletBase

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# iqpp.plone.commenting imports
from iqpp.plone.commenting.browser.comment_form import CommentFormView

class QuickAddCommentFormViewlet(ViewletBase, CommentFormView):
    """
    """
    render = ViewPageTemplateFile('quick_comment_form.pt')

    def __init__(self, context, request, view, manager):
        """
        """
        super(QuickAddCommentFormViewlet, self).__init__(context, request, view, manager)
        self._errors = {}

    @property
    def available(self):
        """
        """
        action = self.request.get("action", "")
        if action in ("add", "reply"):
            return False
            
        url = self.request.get("URL", "")
        if url.endswith("comment_form"):
            return False
            
        return True