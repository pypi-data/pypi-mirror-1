from zope import schema
from zope.formlib import form
from zope.component import getMultiAdapter, getUtility

from zope.interface import Interface
from zope.interface import implements

from plone.memoize.instance import memoize

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName

from zope.app.schema.vocabulary import IVocabularyFactory
from zope.app.form.browser.itemswidgets import MultiCheckBoxWidget

from operun.linkportlet import OperunLinkPortletMessageFactory as _
import re

def widgetExtender(field, request):
    """inserts further arguments needed by the widget
    """
    vocabulary = getUtility(IVocabularyFactory, name="operun.linkportlet.vocabularies.Links")(field.context)
    return MultiCheckBoxWidget(field, vocabulary, request)


class ILinkPortlet(IPortletDataProvider):
    name = schema.TextLine(title = _(u"Title"),
                            description = _(u"The title of the portlet. Will be displayed as header."),
                            required=True,
                            )
    
    links = schema.Tuple(title=_(u"Link List"),
                         description=_(u"Links to be shown in the portlet."),
                         required=True,
                         value_type=schema.Choice(
                             vocabulary="operun.linkportlet.vocabularies.Links")
                         )

class Assignment(base.Assignment):
    implements(ILinkPortlet)

    def __init__(self, name = u'Link Portlet', links = None):
        self.name = name
        self.links = links

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.name

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('linkportlet.pt')

    @property
    def available(self):
        # hide the portlet if no links haven been selected
        return len(self._linkList())
    
    def portletTitle(self):
        return self.data.name
    
    @memoize
    def _linkList(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(portal_type = 'operun Link',
                          UID = self.data.links)
        if len(results)>0:
            return results
        return []
    
    def getInternalLinkUrl(self, catalog, uid = None):
        linkurl = None
        result = catalog(UID=uid)
        if len(result) == 1:
            # there should be exactly one result
            linkurl = result[0].getURL()
            
        return linkurl
        
    def getLinks(self):
        brain_list = self._linkList()
        # as the remoteURLs from ATLink have no catalog metadata column for
        # getRemoteUrl we have to wake up these objects
        link_list = []
        
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal_url = portal_state.portal_url()
        # regular expression to identify an UID
        compiled_regexp = re.compile('^[0-9a-zA-Z]{32}$')
        catalog = getToolByName(context, 'portal_catalog')
        
        for brain in self._linkList():
            if brain.getRemoteUrl is not None:
                remoteurl = brain.getRemoteUrl
                if compiled_regexp.match(remoteurl):
                    # this is an UID - we have to check whether the target is available/visible to the current user
                    remoteurl = self.getInternalLinkUrl(catalog, remoteurl)
                    # if the remoteurl is None -> this link should not be displayed
                    if remoteurl is None:
                        continue
            
            link_list.append({'title' : brain.Title.decode('latin-1').encode('latin-1'),
                              'url'  : remoteurl,
                              'desc'  : brain.Description.decode('latin-1').encode('latin-1'),
                              'target': brain.getLinkTarget == 'new' and '_blank' or '',})
            
        sorted_list = [(l['title'], l) for l in link_list]
        sorted_list.sort()
        return [x[1] for x in sorted_list]

class AddForm(base.AddForm):
    form_fields = form.Fields(ILinkPortlet)
    form_fields['links'].custom_widget = widgetExtender
    label = _(u"Add Link Portlet")
    description = _(u"This portlet displays a selection of Links.")

    def create(self, data):
        return Assignment(name=data.get('name', u'Link Portlet'), links=data.get('links', None))

class EditForm(base.EditForm):
    form_fields = form.Fields(ILinkPortlet)
    form_fields['links'].custom_widget = widgetExtender
    label = _(u"Edit Link Portlet")
    description = _(u"This portlet displays a selection of Links.")