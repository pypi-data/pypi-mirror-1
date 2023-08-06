import logging
from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from slc.dublettefinder.browser.portlets import possible_dupes
from slc.dublettefinder.interfaces import IDubletteFinderConfiguration
from slc.dublettefinder.tests.base import DubletteFinderTestCase

log = logging.getLogger('tests.test_portlet_possible_dupes.py')

class TestPortlet(DubletteFinderTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name="syslab.PossibleFileDuplications")
        self.assertEquals(portlet.addview, "syslab.PossibleFileDuplications")

    def testInterfaces(self):
        portlet = possible_dupes.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='syslab.PossibleFileDuplications')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # This is a NullAddForm - calling it does the work
        addview()

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], possible_dupes.Assignment))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, 
                             name='plone.rightcolumn', 
                             context=self.portal)
        assignment = possible_dupes.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), 
                                   IPortletRenderer)

        self.failUnless(isinstance(renderer, possible_dupes.Renderer))


class TestRenderer(DubletteFinderTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('File', 'file1')
        f = open('src/slc.dublettefinder/slc/dublettefinder/tests/file.txt')
        file = getattr(self.portal, 'file1')
        file.setTitle('File1')
        file.setFile(f)
        file.reindexObject()

        self.portal.invokeFactory('File', 'file2')
        f = open('src/slc.dublettefinder/slc/dublettefinder/tests/file2.txt')
        file = getattr(self.portal, 'file2')
        file.setTitle('File2')
        file.setFile(f)
        file.reindexObject()


    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, 
                                        name='plone.rightcolumn', 
                                        context=self.portal)
        assignment = assignment or possible_dupes.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment), 
                               IPortletRenderer)


    def test_deviance(self):
        dfsettings = getUtility(IDubletteFinderConfiguration, name='dublettefinder_config')
        dfsettings.allowable_size_deviance = 17
        r = self.renderer(context=self.portal.file1, 
                          assignment=possible_dupes.Assignment())

        dupes = r.getPossibleDupes()
        self.assertEquals(1, len(dupes))
        self.assertEquals('file2', dupes[0].id)

        dfsettings.allowable_size_deviance = 5
        r = self.renderer(context=self.portal.file1, 
                          assignment=possible_dupes.Assignment())

        dupes = r.getPossibleDupes()
        self.assertEquals(0, len(dupes))

        self.portal.invokeFactory('Folder', 'files')
        self.portal.files.invokeFactory('File', 'file2')
        f = open('src/slc.dublettefinder/slc/dublettefinder/tests/file2.txt')
        file = getattr(self.portal.files, 'file2')
        file.setFile(f)
        file.reindexObject()

        dfsettings.allowable_size_deviance = 0
        r = self.renderer(context=self.portal.file2, 
                          assignment=possible_dupes.Assignment())

        dupes = r.getPossibleDupes()
        self.assertEquals(1, len(dupes))
        self.assertEquals('file2', dupes[0].id)


    def test_title_matching(self):
        r = self.renderer(context=self.portal.file1, 
                          assignment=possible_dupes.Assignment())

        dupes = r.getPossibleDupes()
        self.assertEquals(0, len(dupes))
    
        file = getattr(self.portal, 'file1')
        file.setTitle('File')
        file.reindexObject()

        file = getattr(self.portal, 'file2')
        file.setTitle('File')
        file.reindexObject()

        r = self.renderer(context=self.portal.file1, 
                          assignment=possible_dupes.Assignment())

        dupes = r.getPossibleDupes()
        self.assertEquals(1, len(dupes))
        self.assertEquals('file2', dupes[0].id)

        # Restore filenames
        file = getattr(self.portal, 'file1')
        file.setTitle('File1')
        file.reindexObject()

        file = getattr(self.portal, 'file2')
        file.setTitle('File2')
        file.reindexObject()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite

