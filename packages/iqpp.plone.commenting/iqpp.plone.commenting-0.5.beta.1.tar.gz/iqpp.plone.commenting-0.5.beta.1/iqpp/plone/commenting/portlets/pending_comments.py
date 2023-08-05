# Zope imports
from Acquisition import aq_inner

# zope imports
from zope.formlib import form
from zope.interface import implements
from zope import schema

# memoize imports
from plone.memoize.instance import memoize

# plone imports
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# CMFPlone imports
from Products.CMFPlone import PloneMessageFactory as _

# iqpp.plone.commenting imports
from iqpp.plone.commenting.interfaces import IGlobalCommenting

class IPendingCommentsPortlet(IPortletDataProvider):
    """
    """
    count = schema.Int(title=_(u'Number of objects to display'),
                       description=_(u'How many objects to list.'),
                       required=True,
                       default=5)
    
class Assignment(base.Assignment):
    """
    """
    implements(IPendingCommentsPortlet)

    def __init__(self, count=5):
        """
        """
        self.count = count

    @property
    def title(self):
        """
        """
        return _(u"Pending Comments")            

class Renderer(base.Renderer):
    """
    """
    render = ViewPageTemplateFile('pending_comments.pt')

    @property
    def available(self):
        """
        """
        mtool = getToolByName(self.context, "portal_membership")
        return mtool.checkPermission("Review comments", self.context)
        
    def Title(self):
        """
        """
        return _(u"Pending Comments")            
        
    def pending_comments(self):
        """
        """
        return self._data()

    @memoize
    def _data(self):
        limit = self.data.count
        context = aq_inner(self.context)
        c = IGlobalCommenting(context)
        
        return c.getPendingComments()[:limit]
        
class AddForm(base.AddForm):
    """
    """
    form_fields = form.Fields(IPendingCommentsPortlet)
    label = _(u"Pending Comments")
    description = _(u"This portlet displays comments which have to be reviewed.")

    def create(self, data):
        """
        """
        return Assignment(
            count=data.get('count', 5))

class EditForm(base.EditForm):
    """
    """
    form_fields = form.Fields(IPendingCommentsPortlet)
    label = _(u"Pending Comments")
    description = _(u"This portlet displays comments which have to be reviewed.")
