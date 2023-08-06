from unittest import defaultTestLoader
from Products.PloneTestCase import PloneTestCase as ptc
from collective.indexing.tests.utils import TestHelpers

ptc.setupPloneSite()


# test-specific imports go here...
from transaction import commit
from collective.indexing.utils import isActive
from collective.indexing.monkey import setAutoFlush
from collective.indexing.config import AUTO_FLUSH


class InstallationTests(ptc.PloneTestCase, TestHelpers):

    def afterSetUp(self):
        setAutoFlush(False)             # turn off auto-flushing...

    def beforeTearDown(self):
        # reset to default
        setAutoFlush(AUTO_FLUSH)

    def testInstallation(self):
        # without the product indexing should happen normally...
        self.assertEqual(self.create(), ['foo'])
        self.assertEqual(self.remove(), [])
        # now the package is installed, which shouldn't change things,
        # even though queued indexing hasn't been activated yet...
        ptc.installPackage('collective.indexing', quiet=True)
        self.failIf(isActive())
        self.assertEqual(self.create(), ['foo'])
        self.assertEqual(self.remove(), [])
        # the profile gets applied, i.e. the package is quick-installed
        # again, things should get indexed, but only at transaction commit
        self.portal.portal_quickinstaller.installProduct('collective.indexing')
        self.failUnless(isActive())
        self.assertEqual(self.create(), [])
        commit()
        self.assertEqual(self.fileIds(), ['foo'])
        self.assertEqual(self.remove(), ['foo'])
        commit()
        self.assertEqual(self.fileIds(), [])
        # after un-installing the package indexing should be immediate again
        self.portal.portal_quickinstaller.uninstallProducts(('collective.indexing',))
        commit()
        self.failIf(isActive())
        self.assertEqual(self.create(), ['foo'])
        self.assertEqual(self.remove(), [])


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

