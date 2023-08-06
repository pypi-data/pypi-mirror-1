from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets import common as base

class PermissionedViewletWithFallbackTemplateMixin(object):
    """
    Mixin allowing a viewlet to use an alternate template if a particular
    permission is not met.
    """
    
    permission = 'View complete edit interface'
    
    def fallback_template(self):
        return NotImplemented
    
    def render(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        if mtool.checkPermission(self.permission, context):
            return self.index()
        else:
            return self.fallback_template()

class ContentViewsViewlet(PermissionedViewletWithFallbackTemplateMixin, base.ViewletBase):
    fallback_template = ViewPageTemplateFile('simpleeditbutton.pt')

class ContentActionsViewlet(PermissionedViewletWithFallbackTemplateMixin, base.ContentActionsViewlet):
    def fallback_template(self):
        return ''
