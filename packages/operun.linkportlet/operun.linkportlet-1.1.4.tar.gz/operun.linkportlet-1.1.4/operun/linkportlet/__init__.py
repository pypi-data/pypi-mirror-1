"""Main product initializer
"""

from zope.i18nmessageid import MessageFactory
from operun.linkportlet import config

from Products.Archetypes import atapi
from Products.CMFCore import utils

# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

OperunLinkPortletMessageFactory = MessageFactory('operun.linkportlet')

def initialize(context):
    """Intializer called when used as a Zope 2 product.
    """
    
    from content import linkarea, linkfolder, link
    
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)