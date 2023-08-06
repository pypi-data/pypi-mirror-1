# Zope 3 imports
from zope.interface import implements

# Zope 2 imports
from Acquisition import Implicit
from DateTime.DateTime import DateTime

# basesyndication imports
from Products.basesyndication.interfaces import IFeed, IFeedSource

# CMF imports
from Products.CMFCore.utils import getToolByName


class FeedMixin:
    """A base mixin class for IFeed implementations.
    Doesn't depend on a specific interface supplied by context, so should
    be generically useful.
    """

    def getFeedEntries(self, max_only=True):
        """See IFeed.
        """
        entries = []
        for fs in self.getFeedSources():
            entries.extend(fs.getFeedEntries())
        if max_only:
            entries = entries[:self.getMaxEntries()]
        return entries

    def getSortedFeedEntries(self, feed_entries=None, max_only=True):
        """Return a sorted sequence of IFeedEntries.  If feed_entries is
        None, call getFeedEntries first.
        Sorting based on publication datetime, newest first.
        """
        if feed_entries is None:
            feed_entries = self.getFeedEntries(max_only=False)
        feed_entries.sort(
            lambda x, y: cmp(y.getEffectiveDate(), x.getEffectiveDate())
            )
        if max_only:
            feed_entries = feed_entries[:self.getMaxEntries()]
        return feed_entries

    def getUpdatePeriod(self):
        """See IFeed.
        """
        syntool = getToolByName(self, 'portal_syndication')
        return syntool.getUpdatePeriod()

    def getUpdateFrequency(self):
        """See IFeed.
        """
        syntool = getToolByName(self, 'portal_syndication')
        return syntool.getUpdateFrequency()

    def getImageURL(self):
        """See IFeed.
        """
        portal_url = getToolByName(self, 'portal_url')()
        return '%s/logo.png' % portal_url

    def getEncoding(self):
        """See IFeed.
        """
        pp = getToolByName(self, 'portal_properties')
        return pp.site_properties.getProperty('default_charset')

    def getMaxEntries(self):
        """See IFeed.
        """
        syntool = getToolByName(self, 'portal_syndication')
        return syntool.getMaxItems()

    def getBaseURL(self):
        """See IFeed.
        """
        return getToolByName(self, 'portal_url')()

    def getModifiedDate(self):
        """See IFeed.
        """
        entries = self.getFeedEntries()
        if not entries:
            # There are no entries, so we just return "now" as the modified
            # datetime.  Doesn't make much sense, but what would?
            return DateTime()
        modified = entries[0].getModifiedDate()
        for feedentry in entries[1:]:
            fe_modified = feedentry.getModifiedDate()
            if fe_modified > modified:
                modified = fe_modified
        return modified


class BaseFeed(FeedMixin, Implicit):
    """IFeed implementation that adds default behaviour for dealing with
    the context of the adapter.
    Also mixes in Implicit as a sacrifice to the Zope2 security gods.
    """

    implements(IFeed)

    def __init__(self, context):
        self.context = context

    def getFeedSources(self):
        """See IFeed.
        For this implementation, we just adapt self.context to IFeedSource
        and return it as the only item in a sequence.
        """
        fs = IFeedSource(self.context)
        return [fs,]

    def getWebURL(self):
        """See IFeed.
        """
        return self.context.absolute_url()

    def getTitle(self):
        """See IFeed.
        """
        return self.context.Title()

    def getDescription(self):
        """See IFeed.
        """
        return self.context.Description()

    def getUID(self):
        """See IFeed.
        """
        return self.context.UID()

