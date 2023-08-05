from zope.i18nmessageid import MessageFactory
_ = MessageFactory("iqpp.plone.commenting")

GLOBALS = globals()

MESSAGES = {
    "comment-added"          : _("Your comment has been added."),
    "comment-added-moderated": _("Your entry has been received. However, it will not be published until it has been reviewed by the site owner."),
    "comment-published"      : _("Comment has been published."),
    "comment-not-published"  : _("Comment has not been published."),
    "comment-rejected"       : _("Comment has been rejected."),
    "comment-not-rejected"   : _("Comment has not been rejected."),
    "comments-deleted"       : _("All comments have been deleted."),
    "comment-deleted"        : _("Your comment has been deleted."),
    "comment-not-deleted"    : _("Your comment wasn't able to be deleted."),
    "comment-modified"       : _("Your comment has been modified."), 
    "comment-not-modified"   : _("Your comment wasn't able to be modified."),
    "comment-added-subject"  : _("A new comment has been added"),
    "options-saved"          : _("Your options has been saved"),
}

REVIEW_STATES = (
    u"private",
    u"pending",
    u"published",
)

REVIEW_STATES_CHOICES = (
    (_(u"Default"),   u'default'),
    (_(u"Private"),   u'private'),
    (_(u"Pending"),   u'pending'),
    (_(u"Published"), u'published'),
)

DEFAULT_CHOICES = (
    (_(u"Default"),  'default'),
    (_(u"Enabled"),  True),
    (_(u"Disabled"), False),
)

ENCODING = "utf-8"