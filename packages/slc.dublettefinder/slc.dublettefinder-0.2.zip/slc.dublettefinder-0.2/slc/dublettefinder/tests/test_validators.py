from zope.component import getUtility

from Products.ATContentTypes.content.file import ATFile
from Products.validation import validation as validationService

from slc.dublettefinder.interfaces import IDubletteFinderConfiguration
from slc.dublettefinder.tests.base import DubletteFinderTestCase

class TestValidation(DubletteFinderTestCase):

    def test_validators(self):
        portal = self.portal
        v = validationService.validatorFor('isUniqueFileName')
        f = open('src/slc.dublettefinder/slc/dublettefinder/tests/file.txt')
        portal._setObject('file', ATFile('file'))
        file = portal._getOb('file')
        file.setFile(f)
        f = file.getFile()
        self.failUnlessEqual(v(f, **{'instance':file}), 1)

        # Create files
        self.setRoles(('Manager',))
        self.portal.invokeFactory('File', 'file1')
        f = open('src/slc.dublettefinder/slc/dublettefinder/tests/file.txt')
        file = getattr(self.portal, 'file1')
        file.setTitle('FileTitle')
        file.setFile(f)
        file.reindexObject()

        # Validation for unique filename should now fail
        v = validationService.validatorFor('isUniqueFileName')
        f = open('src/slc.dublettefinder/slc/dublettefinder/tests/file.txt')
        portal._setObject('file3', ATFile('file'))
        file = portal._getOb('file')
        file.setFile(f)
        f = file.getFile()
        self.failUnlessEqual(type(v(f, **{'instance':file})), str)

        # Validation for unique file size should not fail, deviance is 0
        v = validationService.validatorFor('isUniqueFileSize')
        f = open('src/slc.dublettefinder/slc/dublettefinder/tests/file2.txt')
        portal._setObject('file4', ATFile('file'))
        file = portal._getOb('file')
        file.setFile(f)
        f = file.getFile()
        self.failUnlessEqual(v(f, **{'instance':file}), 1)

        dfsettings = getUtility(IDubletteFinderConfiguration, name='dublettefinder_config')
        dfsettings.allowable_size_deviance = 17
        # Test for unique file size should now fail
        v = validationService.validatorFor('isUniqueFileSize')
        f = open('src/slc.dublettefinder/slc/dublettefinder/tests/file2.txt')
        portal._setObject('file5', ATFile('file'))
        file = portal._getOb('file')
        file.setFile(f)
        f = file.getFile()
        self.failUnlessEqual(type(v(f, **{'instance':file})), str)

        # Test for unique object Title size should fail
        v = validationService.validatorFor('isUniqueObjectName')
        f = open('src/slc.dublettefinder/slc/dublettefinder/tests/file2.txt')
        portal._setObject('file6', ATFile('file'))
        file = portal._getOb('file')
        self.failUnlessEqual(type(v('FileTitle', **{'instance':file})), str)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestValidation))
    return suite

