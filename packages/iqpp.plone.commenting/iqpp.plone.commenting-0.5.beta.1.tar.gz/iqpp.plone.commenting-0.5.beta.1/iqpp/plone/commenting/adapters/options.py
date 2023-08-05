# CMFCore imports
from Products.CMFCore.utils import getToolByName

# iqpp.plone.commenting imports
from iqpp.plone.commenting.controlpanel.commenting import IPloneCommentingControlPanel

# zope imports
from persistent.dict import PersistentDict
from persistent.list import PersistentList

from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

# iqpp.plone.commenting imports
from iqpp.plone.commenting.interfaces import ICommentingOptions
from iqpp.plone.commenting.interfaces import ICommentable

KEY = "iqpp.plone.commenting.options"
                
class CommentingOptions(object):
    """An adapter, which provides commenting options for commentable objects.

    o The default getter/setter methods return the *local* options. In this way 
      the adapter can easily re-used for various edit forms, etc. By default it
      is used for the options tab.  
    o To get a global option only the getGlobalOption() method has to be used.
    o To get a effective option (local option if there is one otherwise the 
      global option) the getEffectiveOption() method is to be used. 
    """
    implements(ICommentingOptions)
    adapts(ICommentable)

    def __init__(self, context):
        """
        """
        self.context = context

        annotations = IAnnotations(context)
        options = annotations.get(KEY)

        if options is None:
            options = annotations[KEY] = {
                'options'   : PersistentDict(),
                'overrides' : PersistentList(),
            }
            # set default options; taken from the default value of interface
            options["options"]["is_enabled"] = ICommentingOptions.get("is_enabled").default
            options["options"]["is_moderated"] = ICommentingOptions.get("is_moderated").default
            options["options"]["edit_own_comments"] = ICommentingOptions.get("edit_own_comments").default            
            options["options"]["mail_from"] = ICommentingOptions.get("mail_from").default            
            options["options"]["mail_to"] = ICommentingOptions.get("mail_to").default                        
            options["options"]["send_comment_added_mail"] = ICommentingOptions.get("send_comment_added_mail").default                                    
            options["options"]["show_preview"] = ICommentingOptions.get("show_preview").default            
                                    
        self.options   = options['options']
        self.overrides = options['overrides']

    def _named_get(self, name):
        """Returns the local option with given name.
        """
        return self.options.get(name, None)
            
    def _named_set(self, name, value):
        """Sets the local option for the given name.
        """
        if name not in self.overrides:
            self.overrides.append(name)
        self.options[name] = value

    def getEffectiveOption(self, name):
        """
        """
        if name in self.overrides:
            return getattr(self, name)
        else:
            return self.getGlobalOption(name)

    def getGlobalOption(self, name):
        """We take the global options out of the control panel.
        """
        utool = getToolByName(self.context, "portal_url")
        portal = utool.getPortalObject()
                
        ro = IPloneCommentingControlPanel(portal)
        return getattr(ro, name)

    def _setOverride(self, name):
        """
        """
        if name not in self.overrides:
            self.overrides.append(name)
        
    def _removeOverride(self, name):
        """
        """
        if name in self.overrides:
            self.overrides.remove(name)
        
    @apply
    def is_enabled():
        def get(self):
            return self.options.get("is_enabled")
        def set(self, value):
            if value == "default":
                self._removeOverride("is_enabled")
            else:
                self._setOverride("is_enabled")
            self.options["is_enabled"] = value
        return property(get, set)
        
    @apply
    def is_moderated():
        def get(self):
            return self.options.get("is_moderated")
        def set(self, value):
            if value == "default":
                self._removeOverride("is_moderated")
            else:
                self._setOverride("is_moderated")
            self.options["is_moderated"] = value
        return property(get, set)

    @apply
    def edit_own_comments():
        def get(self):
            return self.options.get("edit_own_comments")
        def set(self, value):
            if value == [u"default"]:
                self._removeOverride("edit_own_comments")
            else:
                self._setOverride("edit_own_comments")
            self.options["edit_own_comments"] = value
        return property(get, set)


    @apply
    def mail_from():
        def get(self):
            return self._named_get('mail_from')
        def set(self, value):
            # TODO: Be more concise here (if value == \s*)
            if value is None:
                self._removeOverride("mail_from")
            else:
                self._setOverride("mail_from")
            self.options["mail_from"] = value
        return property(get, set)    
        
    @apply
    def mail_to():
        def get(self):
            return self._named_get('mail_to')
        def set(self, value):
            # TODO: Be more concise here (if value == \s*)
            if value is None:
                self._removeOverride("mail_to")
            else:
                self._setOverride("mail_to")
            self.options["mail_to"] = value
        return property(get, set)    
    
    @apply
    def send_comment_added_mail():
        def get(self):
            return self.options.get("send_comment_added_mail")
        def set(self, value):
            if value == "default":
                self._removeOverride("send_comment_added_mail")
            else:
                self._setOverride("send_comment_added_mail")
            self.options["send_comment_added_mail"] = value
        return property(get, set)
    
    @apply
    def show_preview():
        def get(self):
            return self.options.get("show_preview")
        def set(self, value):
            if value == "default":
                self._removeOverride("show_preview")
            else:
                self._setOverride("show_preview")
            self.options["show_preview"] = value
        return property(get, set)