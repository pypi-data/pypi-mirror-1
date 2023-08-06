"""A folder for links and link folders"""

from zope.interface import implements

from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.permissions import View, ModifyPortalContent
from zope.component import getMultiAdapter

from Products.Archetypes.public import *
  
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder

try:
    from Products.ATContentTypes.content.folder import ATFolder, ATFolderSchema
except ImportError:
    from plone.app.folder.folder import ATFolder, ATFolderSchema

from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from operun.linkportlet.interfaces import IOperunLinkFolder
from operun.linkportlet.config import PROJECTNAME

from operun.linkportlet import OperunLinkPortletMessageFactory as _

OperunLinkFolderSchema = ATFolderSchema.copy()

OperunLinkFolderSchema['title'].storage = atapi.AnnotationStorage()
OperunLinkFolderSchema['title'].widget.label = _(u"title")
OperunLinkFolderSchema['title'].widget.description = _(u"title_desc",
                                                     default=u"The title of this link area")
OperunLinkFolderSchema['description'].widget.visible = False

defaults_dict = {'excludeFromNav': True,
                 'allowDiscussion': False,
                 'nextPreviousEnabled': False}
# hide some fields
for propertyField in ('excludeFromNav', 'allowDiscussion', 'nextPreviousEnabled'):
     OperunLinkFolderSchema[propertyField].default = defaults_dict[propertyField]
     OperunLinkFolderSchema[propertyField].widget.visible = False
     OperunLinkFolderSchema[propertyField].languageIndependent = 1

# Finalise the schema according to ATContentTypes standards.
finalizeATCTSchema(OperunLinkFolderSchema, folderish=True, moveDiscussion=False)

# moving fields away from the settings schemata
for propertyField in ('excludeFromNav', 'allowDiscussion', 'nextPreviousEnabled'):
    OperunLinkFolderSchema.changeSchemataForField(propertyField, 'default')

class OperunLinkFolder(ATFolder):
    """A folder which contains links or other link folders.
    """
    implements(IOperunLinkFolder)

    # Standard content type setup
    portal_type = 'operun Link Folder'

    # Make sure we get title-to-id generation when an object is created
    _at_rename_after_creation = True
    
    schema = OperunLinkFolderSchema
    
    title = atapi.ATFieldProperty('title')
    
    security = ClassSecurityInfo()

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """Download the file
        """
        sm = getSecurityManager()
        if sm.checkPermission(ModifyPortalContent, self):
            # this user might want to modify the link - so we call the view
            # directly
            self.REQUEST.RESPONSE.redirect('%s/view' % '/'.join(self.getPhysicalPath()))
        else:
            # this user is not allowed to modify the link - he'll be redirected
            portal_state = getMultiAdapter((self, REQUEST), name=u"plone_portal_state")
            RESPONSE.redirect(portal_state.portal_url())
            return ''
        return ''

atapi.registerType(OperunLinkFolder, PROJECTNAME)