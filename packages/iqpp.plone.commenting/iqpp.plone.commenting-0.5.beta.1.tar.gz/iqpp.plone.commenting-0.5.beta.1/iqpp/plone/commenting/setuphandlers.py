def importVarious(context):
    """Import various settings.
    """
    # Set default permissions
    portal = context.getSite()
    portal.manage_permission("Reply to comment", ("Manager", "Member"), 1)
    portal.manage_permission("Review comments",  ("Manager", "Reviewer"), 1)    
    portal.manage_permission("Delete comments",  ("Manager",), 1)
    portal.manage_permission("Manage comments",  ("Manager",), 1)    