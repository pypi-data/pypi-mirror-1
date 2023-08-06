from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.schema.interfaces import ISource
from htmlentitydefs import codepoint2name

from Acquisition import aq_get
_ = MessageFactory('plone')

from Products.CMFCore.utils import getToolByName

class LinkVocabulary(object):
    """Vocabulary factory for ATLink objects.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        request = aq_get(context, 'REQUEST', None)
        catalog = getToolByName(context, 'portal_catalog', None)
        if catalog is None:
            return None
        folder_dict = self._getFolderDict(catalog)
        link_list = []
        items = catalog(portal_type="operun Link")
        items_dict = dict([(i.UID, self._renderLinkTitle(i, folder_dict)) for i in items])
        items_list = [(k, v) for k, v in items_dict.items()]
        items_list.sort(lambda x, y: cmp(x[1], y[1]))
        terms = [SimpleTerm(k, title=v) for k, v in items_list]
        return SimpleVocabulary(terms)
    
    def _getFolderDict(self, catalog):
        folder_dict = {}
        folder_list = []
        # get all Link Folder objects
        for folder_brain in catalog(portal_type='operun Link Folder'):
            folder_path = folder_brain.getPath()
            folder_list.append((folder_path.count('/'), folder_path, folder_brain.Title))
            folder_dict[folder_path] = folder_brain.Title.decode('latin-1').encode('latin-1')
            
        # get the min depth - so we get the depth of one folder which lies directly
        # below the Link Area
        if len(folder_list)>0:
            min_depth = min(folder_list)[0]
            folder_list = [entry for entry in folder_list if entry[0]>min_depth]
        	
            while len(folder_list)>0:
                min_depth = min(folder_list)[0]
	            
                for entry in folder_list:
	                if entry[0] == min_depth:
	                    folder_dict[entry[1]] = '%s > %s'% (folder_dict[entry[1][:entry[1].rindex('/')]],folder_dict[entry[1]])
                folder_list = [entry for entry in folder_list if entry[0]>min_depth]    
            
        return folder_dict
    
    def _renderLinkTitle(self, link_brain, folder_dict):
        link_title = self.unicode2htmlentities(link_brain.Title)
        link_path = link_brain.getPath()
        folder_title = folder_dict.get(link_path[:link_path.rindex('/')], None)
        if folder_title:
            link_title = '%s > %s' % (self.unicode2htmlentities(folder_title), link_title)
        return link_title
    
    def unicode2htmlentities(self, str):
        """Replaces Unicode characters with HTML entities
        """
        unicode_string = unicode(str, 'utf-8')
        htmlentities = list()
        for c in unicode_string:
            o = ord(c)
            if o < 128:
                htmlentities.append(c)
            elif o < 256:
                htmlentities.append(unicode(chr(ord(c)), 'latin-1'))
            else:
                htmlentities.append('?')
        return ''.join(htmlentities)

LinkVocabularyFactory = LinkVocabulary()
