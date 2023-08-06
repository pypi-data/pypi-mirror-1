# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase
from plone.memoize.instance import memoize

from collective.disqus.browser.configlet import IDisqusSettings

class DisqusViewlet(ViewletBase):
    """
    Viewlet that for DISQUS comment system.  
    """
    index = ViewPageTemplateFile("disqus_panel.pt")
    
    def update(self):
        """
        Update parameters used to render template.
        """
        super(DisqusViewlet, self).update()
        portal_discussion = getToolByName(self.context, 'portal_discussion', None)
        
        self.is_discussion_allowed = False
        if portal_discussion is not None:
            self.is_discussion_allowed = portal_discussion.isDiscussionAllowedFor(aq_inner(self.context))
            
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        self.settings = IDisqusSettings(portal)
        
    def render_js_settings(self):
        """
        Config for DISQUS JSEmbed API (see: http://wiki.disqus.net/JSEmbed/)
        """
        result = 'var disqus_identifier = "%s";' % self.context.UID()
        if self.settings.dev_mode:
            result += '\nvar disqus_developer = 1;'
        return result
