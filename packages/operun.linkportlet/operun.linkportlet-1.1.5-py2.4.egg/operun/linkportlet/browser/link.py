from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent

from operun.linkportlet.interfaces import IOperunLink

class OperunLinkView(BrowserView):
    """Default view of an operun Link
    """
    
    template = ViewPageTemplateFile('link.pt')
    
    def __call__(self, *args, **kw):
        sm = getSecurityManager()
        if sm.checkPermission(ModifyPortalContent, self.context):
            return self.template()
        else:
            portal_state = getMultiAdapter((self.context, self.request), name=u"plone_portal_state")
            self.request.RESPONSE.redirect(portal_state.portal_url())
            return ''