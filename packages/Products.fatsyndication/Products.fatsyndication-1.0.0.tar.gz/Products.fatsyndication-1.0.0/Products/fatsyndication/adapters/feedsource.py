from Products.CMFCore.utils import getToolByName

class BaseFeedSource:

    # It's only a mixin, so it doesn't fully implement IFeedSource
    #implements(IFeedSource)

    def __init__(self, context):
        self.context = context

    def getMaxEntries(self):
        """See IFeedSource.
        """
        syntool = getToolByName(self.context, 'portal_syndication')
        return syntool.getMaxItems()

