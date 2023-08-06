""" Test cases for the fatsyndication package.

:Authors: - Jan Hackel <plonecode@hackel.name>

$Id$
"""

__docformat__ = "reStructuredText"

from DateTime import DateTime
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite
from Products.basesyndication.interfaces import IFeed, IFeedEntry
from zope.interface import alsoProvides
import unittest

from Products.CMFDefault.interfaces import IDocument

PloneTestCase.installProduct("fatsyndication")
PloneTestCase.setupPloneSite()

class TestFixedIssues(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        """Setup test enviroment. Will be executed before every test-case.
        """
        self.login()
        self.setRoles(('Manager',))

    def test_issue177(self):
        """A test case for Quills issue 177, where feedentries for Documents
        (pages) reported the date of last modification as the publication date
        (effective date).
        """
        # We need a feed entry
        id = self.portal.invokeFactory("Document", title="Issue 177",
                                       id="issue177")
        entry = self.portal[id]
        # The document adapter the product provides is not registered yet
        # for the ATDocument (though it can cope with it). We have to register
        # it by ourselves. This is basically what Products.QuillsEnabled does.
        import zope.component
        from Products.ATContentTypes.interface import IATDocument
        from Products.fatsyndication.adapters.feedentry import DocumentFeedEntry
        zope.component.provideAdapter(factory=DocumentFeedEntry,
                                      adapts=[IATDocument],
                                      provides=IFeedEntry)        
        feedEntry = IFeedEntry(entry)
        # Now we set the effective date of the document to somewhere in past. 
        # The feed entry should report exactly that date
        time = DateTime("2000-01-01T01:07:07")
        entry.setEffectiveDate(time)
        self.assertEqual(entry.effective(), time)
        self.assertEqual(entry.effective(), feedEntry.getEffectiveDate())
        
def test_suite():
    suite = unittest.TestSuite( unittest.makeSuite(TestFixedIssues))
    suite.layer = PloneSite
    return suite

