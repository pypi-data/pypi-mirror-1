EasyCommenting is a commenting system for Plone.

Features

    * Optional preview
    * Optional moderation
    * Optional e-mail notification
    * Optional editing of own comments (within adjustable review states)
    * Optional emphasizing of manager comments (via CSS-class)
    * Optional replies of replies (via permissions)
    * Global and Local options
    * Message transformation (via Plone's intelligent text)
    * Pluggable (write adapters for commenting, options, transformations)
      
Installation

    1. Extract the tarball and put the iqpp directory in <instance>/lib/python
    2. Put the .zcml files into <instance>/etc/package-includes
    3. Restart Zope
    4. Go to the quickinstaller and install iqpp.plone.commenting
    5. Go to "manage portlets" and add pending comments portlet
    6. Optionally go to site-setup/commenting and change your options

Installation via buildout (recommended)

    Alternatively, just add the following lines within the [instance]-section 
    of your buildout

    eggs =
        iqpp.plone.commenting 

    zcml =
        iqpp.plone.commenting
        iqpp.plone.commenting-overrides
        

    After re-run your buildout process steps 3-6 above.

    You can find the egg in the Cheese Shop:    
        * http://pypi.python.org/pypi/iqpp.plone.commenting
        
Credits

  * Tom Lazar (tomster). Coding, ideas, discussion partner.