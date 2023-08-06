from zope.interface import Interface, Attribute
from zope import schema
from plone.app.portlets.interfaces import IColumn
from zope.viewlet.interfaces import IViewletManager

from zope.app.container.constraints import contains

from operun.linkportlet import OperunLinkPortletMessageFactory as _

class IOperunLinkArea(Interface):
    """A folderish content type which contains operun Links and operun Link Folders
    """
    contains('operun.linkportlet.interfaces.IOperunLinkFolder',
             'operun.linkportlet.interfaces.IOperunLink',)
    title = schema.TextLine(title = _(u"title", 
                                      default=u"Title"), 
                            required = True)
    
class IOperunLinkFolder(Interface):
    """A folder that can contain operun Links and other operun Link Folders
    """
    contains('operun.linkportlet.interfaces.IOperunLinkFolder',
             'operun.linkportlet.interfaces.IOperunLink',)
    
    title = schema.TextLine(title = _(u"title", 
                                      default=u"Title"), 
                            required = True)
    
class IOperunLink(Interface):
    """A configurable link
    """
    title = schema.TextLine(title = _(u"title",
                                      default=u"Title"), 
                            required = True)
    description = schema.Text(title = _(u"description",
                                        default=u"Description"),
                              description = _(u"description_desc",
                                              default=u"A descriptive text."),
                              required = False)
    linkType = schema.TextLine(title = _(u'link_type',
                                         default=_(u'Link Type')),
                               description = _(u'link_type_desc',
                                               default = _(u'Select whether this is an internal or external link.')),
                               required = True)
    internalLink = schema.TextLine(title = _(u"internal_remoteURL",
                                             default=u"Internal Link"),
                                   description = _(u"internal_remoteURL_desc",
                                                   default=u"A link to content inside the CMS."),
                                   required = False)
    externalLink = schema.TextLine(title = _(u'external_remoteURL',
                                             default = _(u'External Link')),
                                   description = _(u'external_remoteURL_desc',
                                                   default = _(u'A link to content outside of the CMS.')),
                                   required = False)
    linkTarget = schema.TextLine(title = _(u"link_target",
                                           default=u"Target window"),
                                       description = _(u"link_target_desc",
                                                       default=u"Select whether the link should be opened in the same window or a new one."),
                                       required = True)
    
class IOperunUnique(Interface):
    """Marker interface for classes with only one instance"""