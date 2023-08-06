from Acquisition import aq_inner

from zope import schema
from zope.app.component.hooks import getSite
from zope.interface import Interface

from plone.app.vocabularies.catalog import SearchableTextSourceBinder, SearchableTextSource
from Products.CMFPlone.interfaces import IPloneSiteRoot

from Products.ATContentTypes.interface import IATDocument
from Products.CMFCore.utils import getToolByName

class ILinkCollectionLayer(Interface):
    """A layer specific to LinkCollection
    """
    
class LocalSearchableTextSourceBinder(SearchableTextSourceBinder):
    """ make the binder search in the local folder first """

    def __call__(self, context):
        portal_url = getToolByName(context, 'portal_url', None)
        site = getSite()
        if IPloneSiteRoot.providedBy(site):
            if ILinkListFolder.providedBy(context):
                idx = 0
            else:
                idx = 1
            current_path = '/'+'/'.join(portal_url.getRelativeContentPath(site.REQUEST.PARENTS[idx]))
            self.default_query = 'path:%s' % current_path
        else:
            self.default_query = 'path:'

        return SearchableTextSource(context, base_query=self.query.copy(),
                                    default_query=self.default_query)    
                                    
class ILinkList(Interface):
    urls = schema.List(
            title=u"Referenced Documents",
            description=\
u"""Search and select the documents you want to add to your linklist. The first box contains your current selection. Below it you can do a fulltext search for documents. Below the search are the search results you can pic from. Initially they show the contents of the current folder.""",
            required=True,
            value_type=schema.Choice(
                        title=u"Add documents for referencing",
                        source=LocalSearchableTextSourceBinder(
                                    {'object_provides':IATDocument.__identifier__}
                                )
                        )
            )
    
class ILinkListDocument(Interface):
    """ marker interface for Linklists on documents"""

class ILinkListFolder(Interface):
    """ marker interface for Linklists on folders"""