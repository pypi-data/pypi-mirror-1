from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setHooks, setSite

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import navigation
from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.tests.base import PortletsTestCase

from Products.CMFPlone.tests import dummy

class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Navigation')
        self.assertEquals(portlet.addview, 'portlets.Navigation')

    def testInterfaces(self):
        portlet = navigation.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Navigation')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], navigation.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = navigation.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, navigation.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = navigation.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, navigation.Renderer))

class TestRenderer(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.populateSite()
        
    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or navigation.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def populateSite(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory('Folder', 'folder1')
        self.portal.invokeFactory('Link', 'link1')
        self.portal.link1.setRemoteUrl('http://plone.org')
        self.portal.link1.reindexObject()
        folder1 = getattr(self.portal, 'folder1')
        folder1.invokeFactory('Document', 'doc11')
        folder1.invokeFactory('Document', 'doc12')
        folder1.invokeFactory('Document', 'doc13')
        self.portal.invokeFactory('Folder', 'folder2')
        folder2 = getattr(self.portal, 'folder2')
        folder2.invokeFactory('Document', 'doc21')
        folder2.invokeFactory('Document', 'doc22')
        folder2.invokeFactory('Document', 'doc23')
        folder2.invokeFactory('File', 'file21')
        self.setRoles(['Member'])

    def testCreateNavTree(self):
        view = self.renderer(self.portal)
        tree = view.getNavTree()
        self.failUnless(tree)
        self.failUnless(tree.has_key('children'))
    
    def testCreateNavTreeCurrentItem(self):
        # With the context set to folder2 it should return a dict with
        # currentItem set to True
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][-1]['currentItem'], True)

    def testNavTreeExcludesItemsWithExcludeProperty(self):
        # Make sure that items witht he exclude_from_nav property set get
        # no_display set to True
        self.portal.folder2.setExcludeFromNav(True)
        self.portal.folder2.reindexObject()
        view = self.renderer(self.portal.folder1.doc11)
        tree = view.getNavTree()
        self.failUnless(tree)
        for c in tree['children']:
            if c['item'].getPath() == '/plone/folder2':
                self.fail()

    def testShowAllParentsOverridesNavTreeExcludesItemsWithExcludeProperty(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property are not included
        self.portal.folder2.setExcludeFromNav(True)
        self.portal.folder2.reindexObject()
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(showAllParents=True)
        view = self.renderer(self.portal.folder2.doc21)
        tree = view.getNavTree()
        self.failUnless(tree)
        found = False
        for c in tree['children']:
            if c['item'].getPath() == '/plone/folder2':
                found = True
                break
        self.failUnless(found)

    def testNavTreeExcludesItemsInIdsNotToList(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property are not included
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(idsNotToList=['folder2'])
        view = self.renderer(self.portal.folder1.doc11)
        tree = view.getNavTree()
        self.failUnless(tree)
        for c in tree['children']:
            if c['item'].getPath() == '/plone/folder2':
                self.fail()

    def testShowAllParentsOverridesNavTreeExcludesItemsInIdsNotToList(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property are not included
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(idsNotToList=['folder2'], showAllParents=True)
        view = self.renderer(self.portal.folder2.doc21)
        tree = view.getNavTree()
        self.failUnless(tree)
        found = False
        for c in tree['children']:
            if c['item'].getPath() == '/plone/folder2':
                found = True
                break
        self.failUnless(found)

    def testNavTreeExcludesDefaultPage(self):
        # Make sure that items which are the default page are excluded
        self.portal.folder2.setDefaultPage('doc21')
        view = self.renderer(self.portal.folder1.doc11)
        tree = view.getNavTree()
        self.failUnless(tree)
        # Ensure that our 'doc21' default page is not in the tree.
        self.assertEqual([c for c in tree['children'][-1]['children']
                                            if c['item'].getPath()[-5:]=='doc21'],[])

    def testNavTreeMarksParentMetaTypesNotToQuery(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property get no_display set to True
        view = self.renderer(self.portal.folder2.file21)
        tree = view.getNavTree()
        self.assertEqual(tree['children'][-1]['show_children'],True)
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(parentMetaTypesNotToQuery=['Folder'])
        view = self.renderer(self.portal.folder2.file21)
        tree = view.getNavTree()
        self.assertEqual(tree['children'][-1]['show_children'],False)

    def testCreateNavTreeWithLink(self):
        view = self.renderer(self.portal)
        tree = view.getNavTree()
        for child in tree['children']:
            if child['portal_type'] != 'Link':
                self.failIf(child['item'].getRemoteUrl)
            if child['Title'] == 'link1':
                self.failUnlessEqual(child['item'].getRemoteUrl, 'http://plone.org')

    def testNonStructuralFolderHidesChildren(self):
        # Make sure NonStructuralFolders act as if parentMetaTypesNotToQuery
        # is set.
        f = dummy.NonStructuralFolder('ns_folder')
        self.folder._setObject('ns_folder', f)
        self.portal.portal_catalog.reindexObject(self.folder.ns_folder)
        self.portal.portal_catalog.reindexObject(self.folder)
        view = self.renderer(self.folder.ns_folder)
        tree = view.getNavTree()
        self.assertEqual(tree['children'][0]['children'][0]['children'][0]['item'].getPath(),
                                '/plone/Members/test_user_1_/ns_folder')
        self.assertEqual(len(tree['children'][0]['children'][0]['children'][0]['children']), 0)

    def testTopLevel(self):
        view = self.renderer(self.portal.folder2.file21, assignment=navigation.Assignment(topLevel=1))
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][-1]['item'].getPath(), '/plone/folder2/file21')

    def testTopLevelWithContextAboveLevel(self):
        view = self.renderer(self.portal, assignment=navigation.Assignment(topLevel=1))
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(len(tree['children']), 0)

    def testTopLevelTooDeep(self):
        view = self.renderer(self.portal, assignment=navigation.Assignment(topLevel=5))
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(len(tree['children']), 0)

    def testTopLevelWithNavigationRoot(self):
        self.portal.folder2.invokeFactory('Folder', 'folder21')
        self.portal.folder2.folder21.invokeFactory('Document', 'doc211')
        view = self.renderer(self.portal.folder2.folder21, assignment=navigation.Assignment(topLevel=1, root='/folder2'))
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(len(tree['children']), 1)
        self.assertEqual(tree['children'][0]['item'].getPath(), '/plone/folder2/folder21/doc211')

    def testTopLevelWithPortalFactory(self):
        id=self.portal.generateUniqueId('Document')
        typeName='Document'
        newObject=self.portal.folder1.restrictedTraverse('portal_factory/' + typeName + '/' + id)
        # Will raise a KeyError unless bug is fixed
        view = self.renderer(newObject, assignment=navigation.Assignment(topLevel=1))
        tree = view.getNavTree()
    
    def testShowAllParentsOverridesBottomLevel(self):
        view = self.renderer(self.portal.folder2.file21, assignment=navigation.Assignment(bottomLevel=1))
        tree = view.getNavTree()
        self.failUnless(tree)
        # Note: showAllParents makes sure we actually return items on the,
        # path to the context, but the portlet will not display anything
        # below bottomLevel. 
        self.assertEqual(tree['children'][-1]['item'].getPath(), '/plone/folder2')
        self.assertEqual(len(tree['children'][-1]['children']), 1)
        self.assertEqual(tree['children'][-1]['children'][0]['item'].getPath(), '/plone/folder2/file21')
        
    def testBottomLevelStopsAtFolder(self):
        view = self.renderer(self.portal.folder2, assignment=navigation.Assignment(bottomLevel=1))
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][-1]['item'].getPath(), '/plone/folder2')
        self.assertEqual(len(tree['children'][-1]['children']), 0)
        
    def testNoRootSet(self):
        view = self.renderer(self.portal.folder2.file21, assignment=navigation.Assignment(root=''))
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][-1]['item'].getPath(), '/plone/folder2')
        
    def testRootIsPortal(self):
        view = self.renderer(self.portal.folder2.file21, assignment=navigation.Assignment(root='/'))
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][-1]['item'].getPath(), '/plone/folder2')
        
    def testRootIsNotPortal(self):
        view = self.renderer(self.portal.folder2.file21, assignment=navigation.Assignment(root='/folder2'))
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][0]['item'].getPath(), '/plone/folder2/doc21')

    def testRootDoesNotExist(self):
        view = self.renderer(self.portal.folder2.file21, assignment=navigation.Assignment(root='/dodo'))
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(tree.get('item', None), None)
        self.assertEqual(len(tree['children']), 0)

    def testAboveRoot(self):
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(root='/folder2')
        view = self.renderer(self.portal)
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][0]['item'].getPath(), '/plone/folder2/doc21')

    def testOutsideRoot(self):
        view = self.renderer(self.portal.folder1, assignment=navigation.Assignment(root='/folder2'))
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][0]['item'].getPath(), '/plone/folder2/doc21')

    def testRootIsCurrent(self):
        view = self.renderer(self.portal.folder2, assignment=navigation.Assignment(currentFolderOnly=True))
        tree = view.getNavTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][0]['item'].getPath(), '/plone/folder2/doc21')

    def testCustomQuery(self):
        # Try a custom query script for the navtree that returns only published
        # objects
        workflow = self.portal.portal_workflow
        factory = self.portal.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('getCustomNavQuery')
        script = self.portal.getCustomNavQuery
        script.ZPythonScript_edit('','return {"review_state":"published"}')
        self.assertEqual(self.portal.getCustomNavQuery(),{"review_state":"published"})
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        self.failUnless(tree)
        self.failUnless(tree.has_key('children'))
        #Should only contain current object
        self.assertEqual(len(tree['children']), 1)
        #change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        #Should only contain current object and published folder
        self.assertEqual(len(tree['children']), 2)

    def testStateFiltering(self):
        # Test Navtree workflow state filtering
        workflow = self.portal.portal_workflow
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(wf_states_to_show=['published'])
        ntp.manage_changeProperties(enable_wf_state_filtering=True)
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        self.failUnless(tree)
        self.failUnless(tree.has_key('children'))
        #Should only contain current object
        self.assertEqual(len(tree['children']), 1)
        #change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        view = self.renderer(self.portal.folder2)
        tree = view.getNavTree()
        #Should only contain current object and published folder
        self.assertEqual(len(tree['children']), 2)
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
