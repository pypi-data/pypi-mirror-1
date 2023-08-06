from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setHooks, setSite
from Products.GenericSetup.utils import _getDottedName
from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.tests.base import PortletsTestCase
from collective.categorizing.tests.base import CollectiveCategorizingTestCase
from collective.categorizing.portlets import categorizing

class TestPortlet(CollectiveCategorizingTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlet.Categorizing')
        self.assertEquals(portlet.addview, 'portlet.Categorizing')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlet.Categorizing')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_] 
        self.assertEquals(['plone.app.portlets.interfaces.IColumn'],
          registered_interfaces)

    def testInterfaces(self):
        portlet = categorizing.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

#    def testInvokeAddview(self):
#        portlet = getUtility(IPortletType, name='portlet.Categorizing')
#        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
#        for m in mapping.keys():
#            del mapping[m]
#        addview = mapping.restrictedTraverse('+/' + portlet.addview)

#        addview.createAndAdd(data={})

#        self.assertEquals(len(mapping), 1)
#        self.failUnless(isinstance(mapping.values()[0], categorizing.Assignment))

#    def testInvokeEditView(self):
#        mapping = PortletAssignmentMapping()
#        request = self.folder.REQUEST

#        mapping['foo'] = categorizing.Assignment()
#        editview = getMultiAdapter((mapping['foo'], request), name='edit')
#        self.failUnless(isinstance(editview, categorizing.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = categorizing.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, categorizing.Renderer))

class TestRenderer(PortletsTestCase):

    def afterSetUp(self):
        self.populateSite()
        
    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal
        request = request or self.app.REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or categorizing.Assignment(topLevel=0)

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

#    def populateSite(self):
#        self.setRoles(['Manager'])
#        self.portal.invokeFactory('CategoryContainer', 'cc')
#        cc = self.portal.cc
#        cc.invokeFactory('Category', 'c1')
#        c1 = cc.c1
#        cc.invokeFactory('Category', 'c2')
#        c1.invokeFactory('Category', 'c3')
#        cc.invokeFactory('Category', 'c4')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
