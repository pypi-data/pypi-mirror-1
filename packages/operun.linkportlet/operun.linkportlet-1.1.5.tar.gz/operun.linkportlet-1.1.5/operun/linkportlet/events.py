from zope.component import adapter, getMultiAdapter, getUtility
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent import ObjectCopiedEvent
from Products.Archetypes.interfaces import IEditBegunEvent, IObjectInitializedEvent
from Products.Archetypes.event import ObjectInitializedEvent
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from zope.app.container.interfaces import INameChooser

from interfaces import IOperunUnique
import re

@adapter(IOperunUnique, IObjectCreatedEvent)
def operunContentUniquenessPolice(operun_unique_obj, event):
    """To make sure that just one instance of the IOperunUnique exists
    we look in the catalog for other objects of that content type
    """
    plone_site = getSite()
    if isinstance(event, ObjectCopiedEvent):
        CopyError = 'Copy Error'
        # The object is being copied.
        try:
            # we have to try-except because in case of copying a complete
            # Plone Site there might not be a portal_catalog yet
            catalog = getToolByName(plone_site, 'portal_catalog')
        except AttributeError:
            return
        # nevertheless we must prevent that an unique object can be copied
        # within one site
        results = catalog(portal_type = operun_unique_obj.portal_type)
        if len(results)>0:
            # this causes Plone to display an error message that the
            # content to be copied can't be found
            raise CopyError
    else:
        # the object is being created
        assert operun_unique_obj == event.object
        catalog = getToolByName(plone_site, 'portal_catalog')
        results = catalog(portal_type = operun_unique_obj.portal_type)
        if len(results)>0:
            instance = results[0].getObject()
            instance.REQUEST.RESPONSE.redirect(instance.absolute_url())