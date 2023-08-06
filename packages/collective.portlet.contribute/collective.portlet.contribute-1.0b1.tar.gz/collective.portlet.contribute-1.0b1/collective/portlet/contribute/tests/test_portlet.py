from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.contribute import contributecontent

from collective.portlet.contribute.tests.base import TestCase

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.contribute.ContributeContent')
        self.assertEquals(portlet.addview,
                          'collective.portlet.contribute.ContributeContent')

    def test_interfaces(self):
        portlet = contributecontent.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.contribute.ContributeContent')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data=dict(header=u"Header",
                                       text=u"Text",
                                       footer=u"Footer",
                                       omit_border=True,
                                       current_folder=True,
                                       folder='/foo',
                                       types=set(['Document'])))

        self.assertEquals(len(mapping), 1)
        assignment = mapping.values()[0]
        
        self.failUnless(isinstance(assignment, contributecontent.Assignment))
        self.assertEquals(u"Header", assignment.header)
        self.assertEquals(u"Text", assignment.text)
        self.assertEquals(u"Footer", assignment.footer)
        self.assertEquals(True, assignment.omit_border)
        self.assertEquals(True, assignment.current_folder)
        self.assertEquals("/foo", assignment.folder)
        self.assertEquals(set(['Document']), assignment.types)

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = contributecontent.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, contributecontent.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assignment = contributecontent.Assignment()

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, contributecontent.Renderer))


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Member', ))
        self.folder_path = '/' + '/'.join(self.folder.getPhysicalPath()[2:]) # skip portal but add leading slash
        self.portal_path = '/'

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None, **kw):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or contributecontent.Assignment(**kw)
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer).__of__(context)

    def test_add_with_permission(self):
        r = self.renderer(self.portal, folder=self.folder_path, types=set(['Document', 'News Item']))
        r.update()
        
        self.assertEquals(True, r.available)
        
        addable = r.addable_types()
        self.assertEquals(2, len(addable))
        
        # sorted on title (Document = Page)
        self.assertEquals(self.folder.absolute_url() + '/createObject?type_name=News+Item', addable[0]['action'])
        self.assertEquals(self.folder.absolute_url() + '/createObject?type_name=Document', addable[1]['action'])

    def test_add_extra_types(self):
        r = self.renderer(self.portal, folder=self.folder_path, types=set(['Document', 'News Item', 'Topic']))
        r.update()
        
        self.assertEquals(True, r.available)
        
        addable = r.addable_types()
        self.assertEquals(2, len(addable))
        
        # sorted on title (Document = Page)
        self.assertEquals(self.folder.absolute_url() + '/createObject?type_name=News+Item', addable[0]['action'])
        self.assertEquals(self.folder.absolute_url() + '/createObject?type_name=Document', addable[1]['action'])
        
    def test_add_without_permission(self):
        r = self.renderer(self.portal, folder=self.portal_path, types=set(['Document', 'News Item']))
        r.update()
        
        self.assertEquals(False, r.available)
        
        addable = r.addable_types()
        self.assertEquals(0, len(addable))
        
    def test_add_current_folder(self):
        r = self.renderer(self.portal, current_folder=True, types=set(['Document', 'News Item']))
        r.update()
        
        self.assertEquals(False, r.available)
        self.assertEquals(0, len(r.addable_types()))
        
        r = self.renderer(self.folder, current_folder=True, types=set(['Document', 'News Item']))
        r.update()
        
        self.assertEquals(True, r.available)
        
        addable = r.addable_types()
        self.assertEquals(2, len(addable))
        
        # sorted on title (Document = Page)
        self.assertEquals(self.folder.absolute_url() + '/createObject?type_name=News+Item', addable[0]['action'])
        self.assertEquals(self.folder.absolute_url() + '/createObject?type_name=Document', addable[1]['action'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
