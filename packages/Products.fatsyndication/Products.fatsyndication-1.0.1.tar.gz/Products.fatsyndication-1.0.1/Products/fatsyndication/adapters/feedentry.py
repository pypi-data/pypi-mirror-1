# Zope 3 imports
from zope.interface import implements

# Zope 2 imports

# basesyndication imports
from Products.basesyndication.interfaces import IFeedEntry

# Archetypes imports
from Products.Archetypes.config import UUID_ATTR, REFERENCE_CATALOG
from Products.Archetypes.ExtensibleMetadata import FLOOR_DATE

# CMF imports
from Products.CMFCore.utils import getToolByName


class BaseFeedEntry:
    """
    """

    # It's only a mixin, so it doesn't fully implement IFeedEntry
    #implements(IFeedEntry)

    def __init__(self, context):
        self.context = context

    def getWebURL(self):
        """See IFeedEntry.
        """
        return self.context.absolute_url()

    def getTitle(self):
        """See IFeedEntry.
        """
        return self.context.Title()

    def getDescription(self):
        """See IFeedEntry.
        """
        return self.context.getExcerpt()

    def getUID(self):
        """See IFeedEntry.
        """
        return self.context.UID()

    def getAuthor(self):
        """See IFeedEntry.
        """
        creator = self.context.Creator()
        member = self.context.portal_membership.getMemberById(creator)
        return member and member.getProperty('fullname') or creator

    def getEffectiveDate(self):
        """See IFeedEntry.
        """
        effective = self.context.effective()
        if effective == FLOOR_DATE:
            effective = self.context.created()
            # XXX But what if created returns the FLOOR_DATE too?
            # This will break feeds as python's datetime library needs dates above 1900.
        return effective

    def getModifiedDate(self):
        """See IFeedEntry.
        """
        return self.context.modified()

    def getTags(self):
        """See IFeedEntry.
        """
        return self.context.Subject()

    def getRights(self):
        """See IFeedEntry.
        """
        # XXX Implement me properly!
        # self.context.Rights() ??
        return ''

    def getEnclosure(self):
        """See IFeedEntry.
        """
        # Override this method if you want to do podcasting.
        pass


class DocumentFeedEntry(BaseFeedEntry):
    """Adapter for CMFDefault's Document, which also works for talkback
    comment objects.
    """

    implements(IFeedEntry)

    def getUID(self):
        """See IFeedEntry.
        """
        # CMFDefault Documents do not have a UID, so we give them one as
        # IFeedEntry instances need to uniquie identifier.  We just
        # reuse/abuse the archetypes machinery here.
        uid = getattr(self.context, UUID_ATTR, None)
        if uid is None:
            refcat = getToolByName(self.context, REFERENCE_CATALOG)
            uid = refcat._getUUIDFor(self.context)
        return uid

    def getBody(self):
        """See IFeedEntry.
        """
        return self.context.CookedBody()

    def getDescription(self):
        """See IFeedEntry.
        """
        return self.context.Description()

