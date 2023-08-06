import unittest
from zope.component import getUtility
from zope.interface import alsoProvides

from Products.CMFPlone.utils import _createObjectByType

from collective.contentsync.tests.ContentSyncTestCase import ContentSyncTestCase
from collective.contentsync.browser.interfaces import ISynchronizer, ISynchronizedObject

class TestSync(ContentSyncTestCase):

    def afterSetUp(self):
        ContentSyncTestCase.afterSetUp(self) 

        # Create a few trees. For the sake of simplicity we assume the tree is binary.

        # Case 1: source to empty target
        """
                a1              a1
             b1    b2
          c1
        """
        case1_source = _createObjectByType('Folder', self.portal, 'case1_source')
        case1_target = _createObjectByType('Folder', self.portal, 'case1_target')

        a1 = _createObjectByType('Folder', case1_source, 'a1')
        b1 = _createObjectByType('Folder', a1, 'b1')
        b2 = _createObjectByType('Folder', a1, 'b2')
        c1 = _createObjectByType('Folder', b1, 'c1')
        self.case1_source = a1

        a1 = _createObjectByType('Folder', case1_target, 'a1')
        self.case1_target = a1

        # Case 2: source to non-empty target
        """
                 a1              a1
              b1    b2        b1
           c1              c1
        d1
        """
        case2_source = _createObjectByType('Folder', self.portal, 'case2_source')
        case2_target = _createObjectByType('Folder', self.portal, 'case2_target')

        a1 = _createObjectByType('Folder', case2_source, 'a1')
        b1 = _createObjectByType('Folder', a1, 'b1')
        b2 = _createObjectByType('Folder', a1, 'b2')
        c1 = _createObjectByType('Folder', b1, 'c1')
        d1 = _createObjectByType('Folder', c1, 'd1')
        self.case2_source = a1

        a1 = _createObjectByType('Folder', case2_target, 'a1')
        b1 = _createObjectByType('Folder', a1, 'b1')
        c1 = _createObjectByType('Folder', b1, 'c1')
        self.case2_target = a1

        # Case 3: source to non-empty target, but items have been deleted
        # from source and still exist in target. BUT those items in target
        # were not created by a sync so they may not be deleted.
        """
                 a1                     a1
              b1    b2              b1     b3       b4
           c1                   c1            c4
        d1
        """
        case3_source = _createObjectByType('Folder', self.portal, 'case3_source')
        case3_target = _createObjectByType('Folder', self.portal, 'case3_target')

        a1 = _createObjectByType('Folder', case3_source, 'a1')
        b1 = _createObjectByType('Folder', a1, 'b1')
        b2 = _createObjectByType('Folder', a1, 'b2')
        c1 = _createObjectByType('Folder', b1, 'c1')
        d1 = _createObjectByType('Folder', c1, 'd1')
        self.case3_source = a1

        a1 = _createObjectByType('Folder', case3_target, 'a1')
        b1 = _createObjectByType('Folder', a1, 'b1')
        b3 = _createObjectByType('Folder', a1, 'b3')
        b4 = _createObjectByType('Folder', a1, 'b4')
        c1 = _createObjectByType('Folder', b1, 'c1')
        c4 = _createObjectByType('Folder', b3, 'c4')
        self.case3_target = a1

        # Case 4: source to non-empty target, but items (b3, b4) have been deleted
        # from source and still exist in target. b3 and b4 in target
        # were created by a sync so they may be deleted.
        # There is also a top level b3 so we can test that acquisition is not
        # tripping us.
        """
                 a1                     a1                      b3
              b1    b2              b1     b3*       b4*  
           c1                   c1            c4
        d1
        """
        case4_source = _createObjectByType('Folder', self.portal, 'case4_source')
        case4_target = _createObjectByType('Folder', self.portal, 'case4_target')

        a1 = _createObjectByType('Folder', case4_source, 'a1')
        b1 = _createObjectByType('Folder', a1, 'b1')
        b2 = _createObjectByType('Folder', a1, 'b2')
        c1 = _createObjectByType('Folder', b1, 'c1')
        d1 = _createObjectByType('Folder', c1, 'd1')
        self.case4_source = a1

        a1 = _createObjectByType('Folder', case4_target, 'a1')
        b1 = _createObjectByType('Folder', a1, 'b1')
        b3 = _createObjectByType('Folder', a1, 'b3')
        alsoProvides(b3, ISynchronizedObject)
        b4 = _createObjectByType('Folder', a1, 'b4')
        alsoProvides(b4, ISynchronizedObject)
        c1 = _createObjectByType('Folder', b1, 'c1')
        c4 = _createObjectByType('Folder', b3, 'c4')
        self.case4_target = a1

        b3 = _createObjectByType('Folder', case4_source, 'b3')

        # Case 5: complex test
        """
                 a1                             a1
              b1    b2              b1     b3*       b4*    b5
           c1                   c1            c4
        d1
        """
        case5_source = _createObjectByType('Folder', self.portal, 'case5_source')
        case5_target = _createObjectByType('Folder', self.portal, 'case5_target')

        a1 = _createObjectByType('Folder', case5_source, 'a1')
        b1 = _createObjectByType('Folder', a1, 'b1')
        b2 = _createObjectByType('Folder', a1, 'b2')
        c1 = _createObjectByType('Folder', b1, 'c1')
        d1 = _createObjectByType('Folder', c1, 'd1')
        self.case5_source = a1

        a1 = _createObjectByType('Folder', case5_target, 'a1')
        b1 = _createObjectByType('Folder', a1, 'b1')
        b3 = _createObjectByType('Folder', a1, 'b3')
        alsoProvides(b3, ISynchronizedObject)
        b4 = _createObjectByType('Folder', a1, 'b4')
        alsoProvides(b4, ISynchronizedObject)
        b5 = _createObjectByType('Folder', a1, 'b5')
        c1 = _createObjectByType('Folder', b1, 'c1')
        c4 = _createObjectByType('Folder', b3, 'c4')
        self.case5_target = a1

        # Case 6: source to non-empty target. b1 in source has been renamed.
        """
                 a1              a1
              b1*   b2        b1
           c1              c1
        d1
        """
        case6_source = _createObjectByType('Folder', self.portal, 'case6_source')
        case6_target = _createObjectByType('Folder', self.portal, 'case6_target')

        a1 = _createObjectByType('Folder', case6_source, 'a1')
        b1 = _createObjectByType('Folder', a1, 'b1')
        b1.setTitle('A title')
        b2 = _createObjectByType('Folder', a1, 'b2')
        c1 = _createObjectByType('Folder', b1, 'c1')
        d1 = _createObjectByType('Folder', c1, 'd1')
        self.case6_source = a1

        a1 = _createObjectByType('Folder', case6_target, 'a1')
        b1 = _createObjectByType('Folder', a1, 'b1')
        c1 = _createObjectByType('Folder', b1, 'c1')
        self.case6_target = a1

    def testCase1(self):
        """
        """
        utility = getUtility(ISynchronizer)
        result = utility.synchronize(source=self.case1_source, 
                    targets=[self.case1_target])

        self.case1_target.unrestrictedTraverse('a1/b1/c1')
        self.case1_target.unrestrictedTraverse('a1/b2')

        # Confirm that marker interface was applied
        ob = self.case1_target.unrestrictedTraverse('a1/b1/c1')
        self.assertEquals(ISynchronizedObject.isImplementedBy(ob), True)

    def testCase2(self):
        """
        """
        utility = getUtility(ISynchronizer)
        result = utility.synchronize(source=self.case2_source, 
                    targets=[self.case2_target])

        self.case2_target.unrestrictedTraverse('a1/b1/c1/d1')
        self.case2_target.unrestrictedTraverse('a1/b2')

    def testCase3(self):
        """
        """
        utility = getUtility(ISynchronizer)
        result = utility.synchronize(source=self.case3_source, 
                    targets=[self.case3_target])

        self.case3_target.unrestrictedTraverse('a1/b1/c1/d1')
        self.case3_target.unrestrictedTraverse('a1/b3/c4')
        self.case3_target.unrestrictedTraverse('a1/b4')

    def testCase4(self):
        """
        """
        utility = getUtility(ISynchronizer)
        result = utility.synchronize(source=self.case4_source, 
                    targets=[self.case4_target]) 

        self.case4_target.unrestrictedTraverse('a1/b1/c1/d1')

        self.case4_target.unrestrictedTraverse('a1/b2')

        try:
            self.case4_target.unrestrictedTraverse('a1/b3')
        except AttributeError:
            pass
        else:
            raise AssertionError, "b3 must be deleted"

        try:
            self.case4_target.unrestrictedTraverse('a1/b4')
        except AttributeError:
            pass
        else:
            raise AssertionError, "b4 must be deleted"

    def testCase5(self):
        """
        """
        utility = getUtility(ISynchronizer)
        result = utility.synchronize(source=self.case5_source, 
                    targets=[self.case5_target])
        
        self.case5_target.unrestrictedTraverse('a1/b1/c1/d1')

        self.case5_target.unrestrictedTraverse('a1/b2')

        try:
            self.case5_target.unrestrictedTraverse('a1/b3')
        except AttributeError:
            pass
        else:
            raise AssertionError, "b3 must be deleted"

        try:
            self.case5_target.unrestrictedTraverse('a1/b4')
        except AttributeError:
            pass
        else:
            raise AssertionError, "b4 must be deleted"

        self.case5_target.unrestrictedTraverse('a1/b5')

    def testCase6(self):
        """
        """
        utility = getUtility(ISynchronizer)
        result = utility.synchronize(source=self.case6_source, 
                    targets=[self.case6_target])

        self.case6_target.unrestrictedTraverse('a1/b1/c1/d1')
        self.case6_target.unrestrictedTraverse('a1/b2')

        # Check the rename
        self.assertEqual(self.case6_source.a1.b1.title, self.case6_target.a1.b1.title)

def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestSync))
    return suite
