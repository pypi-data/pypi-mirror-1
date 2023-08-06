"""Define a browser view for the operun Link content type.
"""

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent

from Products.CMFCore.utils import getToolByName

from operun.linkportlet.interfaces import IOperunLink

from plone.memoize.instance import memoize 

class OperunLinkView(BrowserView):
    """Default view of an operun Link
    """
    
    template = ViewPageTemplateFile('link.pt')
    
    def __call__(self, *args, **kw):
        sm = getSecurityManager()
        if sm.checkPermission(ModifyPortalContent, self.context):
            return self.template()
        else:
            # the current user is not allowed to see this content - 
            # redirect to the portal url
            portal_state = getMultiAdapter((self.context, self.request), name=u"plone_portal_state")
            self.request.RESPONSE.redirect(portal_state.portal_url())
            return ''