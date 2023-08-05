
    >>> from iqpp.plone.commenting.interfaces import ICommenting
    >>> manager = ICommenting(self.d)
    >>> new_comment = manager.addComment(
    ...     reply_to = u"", 
    ...     subject = u"My Subject", 
    ...     message = u"My Message", 
    ...     name= u"John Doe")

initially, the comment's review_state is 'private', but `addComment` implicitly sets it to `pending`:

    >>> new_comment.submit()
    >>> new_comment.review_state
    u'pending'

    >>> new_comment.reject()
    >>> new_comment.review_state
    u'private'

    >>> new_comment.publish()
    >>> new_comment.review_state
    u'published'

