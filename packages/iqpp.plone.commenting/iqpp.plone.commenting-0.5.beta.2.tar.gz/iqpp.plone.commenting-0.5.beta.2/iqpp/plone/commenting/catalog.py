# zope imports
from zope.component.interfaces import ComponentLookupError

# CMFPlone imports
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

# iqpp.plone.commenting imports
from iqpp.plone.commenting.interfaces import ICommenting
from iqpp.plone.commenting.interfaces import ICommentable

def published_comments(object, portal, **kwargs):
    try:
        comments = []
        for comment in ICommenting(object).getAllComments():
            if comment.review_state == u"published":
                comments.append(comment.id)
            
        return comments
            
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

def pending_comments(object, portal, **kwargs):
    try:
        comments = []
        for comment in ICommenting(object).getAllComments():
            if comment.review_state == u"pending":
                comments.append(comment.id)
            
        return comments
            
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

registerIndexableAttribute('published_comments', published_comments)
registerIndexableAttribute('pending_comments', pending_comments)