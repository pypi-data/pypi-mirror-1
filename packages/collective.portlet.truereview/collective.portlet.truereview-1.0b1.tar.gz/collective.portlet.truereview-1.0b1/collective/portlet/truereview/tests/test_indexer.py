from unittest import defaultTestLoader
from collective.portlet.truereview.tests.base import TestCase

from zope.component import getMultiAdapter
from plone.indexer.interfaces import IIndexer

class TestIndexer(TestCase):
    
    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'doc1', title=u"Unique title")
        self.doc = self.folder.doc1

    def test_indexer(self):
        indexer = getMultiAdapter((self.doc, self.portal.portal_catalog,), IIndexer, name='reviewerRolesAndUsers')
        self.assertEquals(['Reviewer', 'Manager'], indexer())

def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)