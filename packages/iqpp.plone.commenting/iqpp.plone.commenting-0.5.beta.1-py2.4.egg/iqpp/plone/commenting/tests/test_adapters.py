# test imports
from base import CommentingTestCase

# iqpp.rating imports
from iqpp.plone.commenting.interfaces import ICommenting

class TestCommentManagement(CommentingTestCase):

    def testAddComment_1(self):
        manager = ICommenting(self.d)
        new_comment = manager.addComment(
                    reply_to = u"", 
                    subject = u"My Subject", 
                    message = u"My Message", 
                    name= u"John Doe")

        comments = manager.getAllComments()
        self.assertEqual(len(comments), 1)
            
        comments = manager.getComments()
        self.assertEqual(len(comments), 1)
        
        comment = comments[0]
        self.assertEqual(comment.id, new_comment.id)        
        self.assertEqual(comment.reply_to, "")
        self.assertEqual(comment.subject, "My Subject")
        self.assertEqual(comment.message, "My Message")
        self.assertEqual(comment.name, "John Doe")

        comments = manager.getComments(new_comment.id)
        self.assertEqual(len(comments), 0)

        comment = manager.getComment(new_comment.id)
        self.assertEqual(comment.id, new_comment.id)        
        self.assertEqual(comment.reply_to, "")
        self.assertEqual(comment.subject, u"My Subject")
        self.assertEqual(comment.message, u"My Message")
        self.assertEqual(comment.name, u"John Doe")

    def testAddComment_2(self):
        """Add an comment with german umlauts as strings.
        """
        manager = ICommenting(self.d)
        new_comment = manager.addComment(
                    reply_to = "", 
                    subject = "öäüÖÄÜß", 
                    message = "öäüÖÄÜß", 
                    name= "öäüÖÄÜß")

        comment = manager.getComment(new_comment.id)
        self.assertEqual(comment.id, new_comment.id)        
        self.assertEqual(comment.reply_to, "")
        self.assertEqual(comment.subject, u"öäüÖÄÜß")
        self.assertEqual(comment.message, u"öäüÖÄÜß")
        self.assertEqual(comment.name, u"öäüÖÄÜß")

    def testAddComment_2(self):
        """Add an comment with german umlauts as unicode.
        """
        manager = ICommenting(self.d)
        new_comment = manager.addComment(
                    reply_to = "", 
                    subject = u"öäüÖÄÜß", 
                    message = u"öäüÖÄÜß", 
                    name= u"öäüÖÄÜß")

        comment = manager.getComment(new_comment.id)
        self.assertEqual(comment.id, new_comment.id)        
        self.assertEqual(comment.reply_to, "")
        self.assertEqual(comment.subject, u"öäüÖÄÜß")
        self.assertEqual(comment.message, u"öäüÖÄÜß")
        self.assertEqual(comment.name, u"öäüÖÄÜß")

    def testAddCommentOfComment(self):
        manager = ICommenting(self.d)
        comment = manager.addComment(
                      reply_to = u"", 
                      subject = u"My Subject", 
                      message = u"My Message", 
                      name= u"John Doe")
            
        reply = manager.addComment(
                      reply_to = comment.id, 
                      subject = u"My Reply", 
                      message = u"My Reply Message", 
                      name= u"Jane Doe")

        comments = manager.getAllComments()
        self.assertEqual(len(comments), 2)

        comments = manager.getComments()
        self.assertEqual(len(comments), 1)
        
        comments = manager.getComments(comment.id)
        self.assertEqual(len(comments), 1)

        comments = manager.getComments(reply.id)
        self.assertEqual(len(comments), 0)
        

    def testDeleteComment1(self):
        """
        """
        manager = ICommenting(self.d)
        comment_1 = manager.addComment(
                        reply_to = u"", 
                        subject = u"My Comment 1", 
                        message = u"My Message 1", 
                        name= u"John Doe")

        reply_id = manager.addComment(
                        reply_to = comment_1.id, 
                        subject = u"My Reply", 
                        message = u"My Reply Message", 
                        name= u"Jane Doe")
            
        comment_2 = manager.addComment(
                        reply_to = u"", 
                        subject = u"My Comment 2", 
                        message = u"My Message 2", 
                        name= u"John Doe")
                        
        comments = manager.getAllComments()
        self.assertEqual(len(comments), 3)

        # reply should also be deleted.
        manager.deleteComment(comment_1.id)        
        comments = manager.getAllComments()
        self.assertEqual(len(comments), 1)

    def testDeleteReply(self):
        """
        """
        manager = ICommenting(self.d)
        comment_1 = manager.addComment(
                        reply_to = u"", 
                        subject = u"My Comment 1", 
                        message = u"My Message 1", 
                        name= u"John Doe")

        reply = manager.addComment(
                        reply_to = comment_1.id, 
                        subject = u"My Reply", 
                        message = u"My Reply Message", 
                        name= u"Jane Doe")
            
        comment_2 = manager.addComment(
                        reply_to = u"", 
                        subject = u"My Comment 2", 
                        message = u"My Message 2", 
                        name=u"John Doe")
                        
        comments = manager.getAllComments()
        self.assertEqual(len(comments), 3)

        # reply should also be deleted.
        manager.deleteComment(reply.id)        
        comments = manager.getAllComments()
        self.assertEqual(len(comments), 2)

    def testDeleteComments(self):
        """
        """
        manager = ICommenting(self.d)
        comment_1 = manager.addComment(
                        reply_to = u"", 
                        subject = u"My Comment 1", 
                        message = u"My Message 1", 
                        name=u"John Doe")

        reply_id = manager.addComment(
                        reply_to = comment_1.id, 
                        subject = u"My Reply", 
                        message = u"My Reply Message", 
                        name=u"Jane Doe")
            
        comment_2 = manager.addComment(
                        reply_to = u"", 
                        subject = u"My Comment 2", 
                        message = u"My Message 2", 
                        name=u"John Doe")
                        
        # reply should also be deleted.
        manager.deleteComments()        
        comments = manager.getAllComments()
        self.assertEqual(len(comments), 0)
        
    def testEditComment(self):
        """
        """
        manager = ICommenting(self.d)
        comment_1 = manager.addComment(
                        reply_to = u"", 
                        subject = u"My Comment 1", 
                        message = u"My Message 1", 
                        name="John Doe",)

        manager.manageComment(
            comment_id = comment_1.id,
            reply_to = u"",
            subject  = u"Modified Subject",
            message  = u"Modified Message",
            name     = u"Jane Doe",
            member_id = u"",
            email = u"",
            review_state=u"published")
            
        comment = manager.getComment(comment_1.id)

        self.assertEqual(comment.id, comment_1.id)
        self.assertEqual(comment.reply_to, "")
        self.assertEqual(comment.subject, "Modified Subject")
        self.assertEqual(comment.message, "Modified Message")
        self.assertEqual(comment.name, "Jane Doe")
        self.assertEqual(comment.review_state, "published")

                                
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCommentManagement))        
    return suite
