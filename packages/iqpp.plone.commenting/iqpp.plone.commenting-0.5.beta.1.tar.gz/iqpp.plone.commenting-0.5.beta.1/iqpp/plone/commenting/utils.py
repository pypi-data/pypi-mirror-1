# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.commenting imports
from iqpp.plone.commenting.config import ENCODING

def getMemberInfo(context, member_id, name, email):
    """
    """
    mtool = getToolByName(context, "portal_membership")

    if member_id is not None:
        # getMemberById doesn't speek unicodish :-(        
        member_id = member_id.encode("utf-8")
    member = mtool.getMemberById(member_id)
    
    if name != "":
        name = name
    elif member_id != "":        
        mi = mtool.getMemberInfo(member_id)            
        name =  mi and mi['fullname'] or member_id
    else:
        # This should never happens
        name = "Anonymous"

    if email != "":
        email = email
    elif member_id != "":
        email = member and member.getProperty("email", "") or ""
    else:
        # This should never happens
        email = ""

    # TODO: "is_manager" should rather be decided by the the permission
    # "Manage comments"? 
    return {        
        "name"       : name, 
        "email"      : email,
        "is_manager" : member and member.has_role("Manager")
    }    