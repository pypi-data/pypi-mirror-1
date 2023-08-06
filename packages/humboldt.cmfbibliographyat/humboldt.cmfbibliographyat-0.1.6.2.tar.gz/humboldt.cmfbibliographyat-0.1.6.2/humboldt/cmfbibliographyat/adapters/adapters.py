##########################################################################
# humboldt.cmfbibliographyat - published under the GNU Public License V 2
# Written by Andreas Jung, ZOPYX Ltd. & Co. KG, D-72070 Tuebingen, Germany
##########################################################################

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
        """ See IFeedSource """

        ps = getToolByName(self.context, "portal_syndication")
        if not ps.isSyndicationAllowed(self.context):
            raise ValueError("Site syndication via RSS feeds is not allowed. "\
                             "Ask the sites system administrator to go to "\
                             "portal_syndication > Policies and enable "\
                             "syndication. Each folder then needs to have "\
                             "syndication enabled.")

        brains = self.context.getFolderContents()
        objs = [brain.getObject() for brain in brains]
        objs = [o for o in objs if IBibliographicItem.providedBy(o)]
        for o in objs:
            o2 = IFeedEntry(o, None)
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

    def getDescription(self):
        return ''

    def getBody(self):
        """ Look up a view for a bib reference. The optional request
            parameter is eiterh 'simple', 'full' or refers to the name
            of a bibliographic style (requires ATBiblioStyles installed).
        """

        default_views = {'simple' : '@@feed_simple_view',
                         'full' : '@@feed_full_view'}

        style = self.context.REQUEST.get('style', None)
        if not style:
            return ''

        if style in default_views:
            view = self.context.restrictedTraverse(default_views[style], None)
            if view:
                return view()
        else:
            styles_tool = getToolByName(self.context, 'portal_bibliostyles', None)
            if styles_tool:
                result = styles_tool.portal_bibliostyles.formatList(self.context,
                                                                style,
                                                                instance=None,
                                                                title_link=True,
                                                                title_link_only_if_owner=False,
                                                                brains_object=False,
                                                                sort=False)
                if result:
                    return result[0]
        return ''
