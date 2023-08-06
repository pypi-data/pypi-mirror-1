# integration and functional tests
# see http://plone.org/documentation/tutorial/testing/writing-a-plonetestcase-unit-integration-test
# for more information about the following setup

from unittest import TestSuite, makeSuite, main
from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import collective.indexing
    zcml.load_config('configure.zcml', collective.indexing)
    fiveconfigure.debug_mode = False

setup_product()
ptc.setupPloneSite()


# test-specific imports go here...
from zope.component import provideUtility, getUtilitiesFor, getGlobalSiteManager
from transaction import savepoint

from collective.indexing.interfaces import IIndexQueue, IIndexing
from collective.indexing.interfaces import IIndexQueueSwitch
from collective.indexing.config import INDEX, REINDEX, UNINDEX
from collective.indexing.queue import IndexQueueSwitch
from collective.indexing.utils import getIndexer
from collective.indexing.tests import utils


class SubscriberTests(ptc.PloneTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Folder', id='folder1', title='Folder 1')
        self.folder = self.portal.folder1
        self.portal.invokeFactory('File', id='file1', title='File 1')
        self.file = self.portal.file1
        self.indexer = utils.MockIndexer()
        self.queue = self.indexer.queue
        provideUtility(self.indexer)

    def beforeTearDown(self):
        gsm = getGlobalSiteManager()
        gsm.unregisterUtility(self.indexer, IIndexing)

    def testAddObject(self):
        self.portal.invokeFactory('File', id='foo', title='Foo')
        self.assert_((INDEX, self.portal.foo, None) in self.queue)

    def testUpdateObject(self):
        self.file.update(title='Foo')
        # `update()` doesn't fire an event, so there's only one operation
        # queued up via `CatalogMultiplex`
        self.assertEqual(self.queue, [(REINDEX, self.file, None)])

    def testModifyObject(self):
        self.file.processForm(values={'title': 'Foo'})
        self.assertEqual(self.file.Title(), 'Foo')
        self.assertEqual(self.queue, [(REINDEX, self.file, None), (REINDEX, self.file, None)])

    def testRemoveObject(self):
        file1 = self.portal.file1
        self.portal.manage_delObjects('file1')
        self.assert_((UNINDEX, file1, None) in self.queue, self.queue)
        self.assertRaises(AttributeError, getattr, self.portal, 'file1')

    def testAddAndRemoveObject(self):
        self.portal.invokeFactory('File', id='foo', title='Foo')
        foo = self.portal.foo
        self.portal.manage_delObjects('foo')
        index = self.queue.index((INDEX, foo, None))
        unindex = self.queue.index((UNINDEX, foo, None))
        self.assert_(index < unindex)
        self.assertRaises(AttributeError, getattr, self.portal, 'foo')

    def testMoveObject(self):
        self.portal.folder1.invokeFactory('File', id='file2', title='File 2')
        self.portal.invokeFactory('Folder', id='folder2', title='Folder 2')
        self.queue[:] = []  # clear the queue...
        savepoint()         # need to create a savepoint, because!
        original = self.portal.folder1.file2
        cookie = self.portal.folder1.manage_cutObjects(ids=('file2',))
        self.portal.folder2.manage_pasteObjects(cookie)
        self.assert_((REINDEX, self.portal.folder1, None) in self.queue, self.queue)
        self.assert_((REINDEX, self.portal.folder2.file2, None) in self.queue, self.queue)
        self.assert_((REINDEX, self.portal.folder2, None) in self.queue, self.queue)
        # 'unindex' is called via `CatalogMultiplex`, so it's the first operation...
        self.assert_(self.queue[0], (UNINDEX, original, None))
        # but otherwise there should be no 'unindex', since it's still the same object...
        self.failIf((UNINDEX, original, None) in self.queue[1:], self.queue)
        self.assertEqual(original, self.portal.folder2.file2)

    def testCopyObject(self):
        cookie = self.portal.manage_copyObjects(ids=('file1',))
        self.folder.manage_pasteObjects(cookie)
        self.assert_((INDEX, self.folder.file1, None) in self.queue)
        self.assert_((REINDEX, self.folder, None) in self.queue)

    def testRenameObject(self):
        savepoint()         # need to create a savepoint, because!
        self.portal.manage_renameObject('file1', 'foo')
        self.assert_((REINDEX, self.portal.foo, None) in self.queue, self.queue)
        self.assertRaises(AttributeError, getattr, self.portal, 'file1')

    def testPublishObject(self):
        self.portal.portal_workflow.doActionFor(self.folder, 'publish')
        self.assertEqual(self.queue, [(REINDEX, self.folder, None), (REINDEX, self.folder, ['review_state'])])


class IntegrationTests(ptc.PloneTestCase):

    def testGetIndexer(self):
        # no indexer should be found initially...
        indexer = getIndexer()
        self.failIf(indexer, 'indexer found?')
        # a direct indexer is provided...
        direct_indexer = utils.MockIndexer()
        provideUtility(direct_indexer, name='indexer')
        indexer = getIndexer()
        self.failUnless(indexer, 'no indexer found')
        self.assertEqual(indexer, direct_indexer, 'who are you?')
        # a second direct indexer is provided...
        provideUtility(utils.MockIndexer(), name='rexedni')
        self.assertRaises(AssertionError, getIndexer)
        # queued indexing is enabled...
        provideUtility(IndexQueueSwitch(), IIndexQueueSwitch)
        indexer = getIndexer()
        self.failUnless(indexer, 'no indexer found')
        self.failUnless(IIndexQueue.providedBy(indexer), 'non-queued indexer found')
        # and we've got two indexers to dispatch things to...
        indexers = list(getUtilitiesFor(IIndexing))
        self.assertEqual(len(indexers), 2)


def test_suite():
    return TestSuite([
        makeSuite(SubscriberTests),
        makeSuite(IntegrationTests),
        ztc.FunctionalDocFileSuite(
           'browser.txt', package='collective.indexing.tests',
           test_class=ptc.FunctionalTestCase),
    ])

if __name__ == '__main__':
    main(defaultTest='test_suite')

