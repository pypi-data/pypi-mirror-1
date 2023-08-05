Tests the attributes and views for IComment and ICommenting
-----------------------------------------------------------

First, we add a comment to our test document to have something to play with:

    >>> from iqpp.plone.commenting.interfaces import ICommenting
    >>> manager = ICommenting(self.d)
    >>> new_comment = manager.addComment(
    ...     reply_to = u"", 
    ...     subject = u"My Subject", 
    ...     message = u"My Message", 
    ...     name= u"John Doe")

Anonymous
=========


Now we're ready to call the various views. First we test as anonymous, to verify that the permissions are respected:

    >>> from Products.Five.testbrowser import Browser
    >>> browser = self.getBrowser()
    >>> browser.handleErrors = False
    >>> try:
    ...     browser.open('http://nohost/plone/document/delete_comment?comment_id=%s' % str(new_comment.id))
    ...     self.fail()
    ... except:
    ...     pass
    
    >>> try:
    ...     browser.open('http://nohost/plone/document/edit_comment?comment_id=%s' % str(new_comment.id))
    ...     self.fail()
    ... except:
    ...     pass
    
    >>> try:
    ...     browser.open('http://nohost/plone/document/publish_comment?comment_id=%s' % str(new_comment.id))
    ...     self.fail()
    ... except:
    ...     pass
    
    >>> try:
    ...     browser.open('http://nohost/plone/document/reject_comment?comment_id=%s' % str(new_comment.id))
    ...     self.fail()
    ... except:
    ...     pass
    
    >>> try:
    ...     browser.open('http://nohost/plone/document/edit_comment_form?comment_id=%s' % str(new_comment.id))
    ...     self.fail()
    ... except:
    ...     pass

As Manager
==========

Now we log in as Manager and revisit the URLs

    >>> self.loginAsPortalOwner()
    >>> browser = self.getBrowser(logged_in=True)
    >>> browser.handleErrors = False

    >>> browser.open('http://nohost/plone/document/edit_comment_form?comment_id=%s' % str(new_comment.id))

edit comment
************

Note: this also tests unicode conversion in the adapter.

    >>> browser.open('http://nohost/plone/document/edit_comment?comment_id=%s&subject=foo&message=baz' % str(new_comment.id))
    >>> modified_comment = manager.getComment(id=new_comment.id)
    >>> modified_comment.subject
    u'foo'
    >>> modified_comment.message
    u'baz'    

publish comment
***************

    >>> modified_comment.review_state
    u'pending'

    >>> browser.open('http://nohost/plone/document/publish_comment?comment_id=%s' % str(new_comment.id))
    >>> modified_comment.review_state
    u'published'

reject comment
**************

    >>> browser.open('http://nohost/plone/document/reject_comment?comment_id=%s' % str(new_comment.id))
    >>> modified_comment.review_state
    u'private'

delete_comment
**************

Finally we delete the comment and verify:

    >>> number_of_comments = len(manager.getComments())
    >>> browser.open('http://nohost/plone/document/delete_comment?comment_id=%s' % str(new_comment.id))

    >>> len(manager.getComments()) == number_of_comments - 1
    True
