from Products.CMFCore.DirectoryView import registerDirectory
from config import GLOBALS
from Products.CMFCore.permissions import setDefaultRoles

import catalog

# Workaround as just the definition of a permission in configure.zcml (without
# to use it within another place like browser, etc.) is not enough to make it 
# appear in Zope's security tab.

ReplyToComment = "Reply to comment"
setDefaultRoles(ReplyToComment, ('Manager',))

# Register skins directory
registerDirectory('skins', GLOBALS)

