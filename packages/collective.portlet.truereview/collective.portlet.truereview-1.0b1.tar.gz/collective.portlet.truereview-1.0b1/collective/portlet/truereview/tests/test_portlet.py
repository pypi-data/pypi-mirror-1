from unittest import defaultTestLoader
from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from Products.PloneTestCase.setup import default_user

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.truereview import truereview

from collective.portlet.truereview.tests.base import TestCase

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.truereview.TrueReview')
        self.assertEquals(portlet.addview,
                          'collective.portlet.truereview.TrueReview')

    def test_interfaces(self):
        portlet = truereview.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.truereview.TrueReview')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data=dict(states=('one', 'two'), types=('a','b,',), count=5))

        self.assertEquals(len(mapping), 1)
        assignment = mapping.values()[0]
        self.failUnless(isinstance(assignment, truereview.Assignment))
        self.failUnless(('one', 'two',), assignment.states)
        self.failUnless(('a', 'b',), assignment.types)
        self.failUnless(5, assignment.count)

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = truereview.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, truereview.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = truereview.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, truereview.Renderer))


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None, **kw):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or truereview.Assignment(**kw)
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer).__of__(context)

    def test_render(self):
        r = self.renderer(context=self.portal)
        r.update()
        output = r.render()
    
    def test_search_with_permission(self):
        wf = self.portal.portal_workflow
        
        self.portal.invokeFactory('Document', 'different-state')
        self.portal.invokeFactory('News Item', 'different-type')
        self.portal.invokeFactory('Document', 'not-permission')
        self.portal.invokeFactory('Document', 'show-this-one')
        
        for id in ('different-type', 'not-permission', 'show-this-one'):
            wf.doActionFor(self.portal[id], 'submit')
        
        # Make user a member site-wide
        self.setRoles(('Member',))
        
        # But give the Reviewer local role on the 'show-this-one' item
        self.portal['show-this-one'].manage_addLocalRoles(default_user, ('Reviewer',))
        self.portal['show-this-one'].reindexObject()
        
        r = self.renderer(context=self.portal, states=('pending',), types=('Document',), count=5)
        r.update()
        
        self.assertEquals(True, r.available)
        
        items = r.review_items()
        self.assertEquals(1, len(items))
        
        self.assertEquals(self.portal['show-this-one'].absolute_url(), items[0]['url'])

    def test_count_limit(self):
        wf = self.portal.portal_workflow
        
        for i in range(10):
            self.portal.invokeFactory('Document', 'd' + str(i))
            wf.doActionFor(self.portal['d' + str(i)], 'submit')
            
        r = self.renderer(context=self.portal, states=('pending',), types=('Document',), count=5)
        r.update()
        
        self.assertEquals(True, r.available)
        self.assertEquals(5, len(r.review_items()))

    def test_hidden_if_no_items(self):
        wf = self.portal.portal_workflow
        r = self.renderer(context=self.portal, states=('bogus',))
        r.update()
        self.assertEquals(False, r.available)

def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)