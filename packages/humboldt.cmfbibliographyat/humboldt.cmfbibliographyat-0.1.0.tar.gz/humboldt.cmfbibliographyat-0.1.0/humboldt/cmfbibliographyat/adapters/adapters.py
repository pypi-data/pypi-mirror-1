# Zope 3 imports
from zope.interface import implements
from zope.component import getMultiAdapter

# Zope 2 imports
from DateTime.DateTime import DateTime

# CMF imports
from Products.CMFCore.utils import getToolByName

# fatsyndication imports
from Products.fatsyndication.adapters import BaseFeed
from Products.fatsyndication.adapters import BaseFeedSource
from Products.fatsyndication.adapters import BaseFeedEntry
from Products.basesyndication.interfaces import IFeedSource
from Products.basesyndication.interfaces import IFeedEntry
from Products.fatsyndication.adapters.feedsource import BaseFeedSource

from Products.CMFBibliographyAT.interface import IBibliographicItem

class BibFolderSource(BaseFeedSource):
    """ Adopting Bibfolder to IFeedSource """

    implements(IFeedSource)

    def __init__(self, context):
        self.context = context

    def getFeedEntries(self, max_only=True):
        """ See IFeedSoure """

        brains = self.context.getFolderContents()
        objs = [brain.getObject() for brain in brains]
        objs = [o for o in objs if IBibliographicItem.providedBy(o)]
        for o in objs:
            o2 = IFeedEntry(o)
            if o2:
                yield o2



class BibFolderFeed(BaseFeed):
    """Adapter for Bibfolder to IFeed """

    def getModifiedDate(self):
        """ See IFeed """
        return DateTime()


class BibReferenceEntry(BaseFeedEntry):
    """ Adopt IBibliographicItem to IFeedEntry """

    implements(IFeedEntry)

    def __init__(self, context):
        self.context = context

    def getBody(self):
        return 'hello world'
