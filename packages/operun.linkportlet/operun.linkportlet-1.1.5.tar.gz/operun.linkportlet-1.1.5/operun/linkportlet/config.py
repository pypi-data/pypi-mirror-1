"""Common configuration constants
"""
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('operun.linkportlet')

PROJECTNAME = "operun.linkportlet"

ADD_PERMISSIONS = {
    "operun Link Area" : "operun: Add operun Link Area",
    "operun Link Folder" : "operun: Add operun Link Folder",
    "operun Link" : "operun: Add operun Link",
}

LINK_TYPE_VOCABULARY = [
    ('internal', _(u"internal", default=u"Internal link")),
    ('external', _(u"external",default=u"External link")),
]

LINK_TARGET_VOCABULARY = [
    ('same', _(u"same_window", default=u"Same browser window")),
    ('new', _(u"new_window",default=u"New browser window")),
]