# zope imports
from zope.interface import implements
from zope.component import adapts

# CMFPlone imports
from Products.CMFPlone.utils import safe_unicode

# iqpp.plone.commenting imports
from iqpp.plone.commenting.interfaces import IComment
from iqpp.plone.commenting.interfaces import ICommentTransformations
        
class CommentTransformations(object):
    """An adapter for IComments, which provides text transformation from 
    intelligenttext to HTML.
    """
    implements(ICommentTransformations)
    adapts(IComment)

    def __init__(self, context):
        """
        """
        self.context = context
    
    def transformMessage(self):
        """
        """
        try:
            from plone.intelligenttext.transforms import \
                 convertWebIntelligentPlainTextToHtml as convert                 
        except ImportError:
            transformed_message = self.context.message.replace("\n", "<br/>")
        else:    
            transformed_message = convert(self.context.message)
        
        self.context.transformed_message = safe_unicode(transformed_message)