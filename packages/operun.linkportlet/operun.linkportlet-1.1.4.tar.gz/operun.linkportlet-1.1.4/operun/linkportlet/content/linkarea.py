"""A folder for links and link folders"""

from zope.interface import implements

from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore.permissions import View, ModifyPortalContent
from zope.component import getMultiAdapter

from Products.Archetypes.public import *
  
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder

from Products.ATContentTypes.content.folder import ATFolder, ATFolderSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from operun.linkportlet.interfaces import IOperunLinkArea, IOperunUnique
from operun.linkportlet.config import PROJECTNAME

from operun.linkportlet import OperunLinkPortletMessageFactory as _

OperunLinkAreaSchema = ATFolderSchema.copy()

OperunLinkAreaSchema['title'].storage = atapi.AnnotationStorage()
OperunLinkAreaSchema['title'].widget.label = _(u"title")
OperunLinkAreaSchema['title'].widget.description = _(u"title_desc",
                                                     default=u"The title of this link area")
OperunLinkAreaSchema['description'].widget.visible = False

defaults_dict = {'excludeFromNav': True,
                 'allowDiscussion': False,
                 'nextPreviousEnabled': False}
# hide some fields
for propertyField in ('excludeFromNav', 'allowDiscussion', 'nextPreviousEnabled'):
     OperunLinkAreaSchema[propertyField].default = defaults_dict[propertyField]
     OperunLinkAreaSchema[propertyField].widget.visible = False
     OperunLinkAreaSchema[propertyField].languageIndependent = 1

# Finalise the schema according to ATContentTypes standards.
finalizeATCTSchema(OperunLinkAreaSchema, folderish=True, moveDiscussion=False)

# moving fields away from the settings schemata
for propertyField in ('excludeFromNav', 'allowDiscussion', 'nextPreviousEnabled'):
    OperunLinkAreaSchema.changeSchemataForField(propertyField, 'default')

class OperunLinkArea(ATFolder):
    """A folder which contains links and link folders.
    """
    implements(IOperunLinkArea, IOperunUnique)

    # Standard content type setup
    portal_type = 'operun Link Area'

    # Make sure we get title-to-id generation when an object is created
    _at_rename_after_creation = True
    
    schema = OperunLinkAreaSchema
    
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

atapi.registerType(OperunLinkArea, PROJECTNAME)