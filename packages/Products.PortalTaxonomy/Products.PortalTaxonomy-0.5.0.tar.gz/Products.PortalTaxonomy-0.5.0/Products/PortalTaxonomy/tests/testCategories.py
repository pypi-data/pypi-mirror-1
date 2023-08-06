"""
# Test PortalTaxonomy.py
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PortalTaxonomy.tests import TestCase

from Testing import ZopeTestCase

class TestCategories(TestCase.PortalTaxonomyTestCase):

    def testAddCategory(self):
        ''' Test that a category can be added
        '''
        self.login('manager')
        self.pc.invokeFactory('Category', id='c1', title='C 1')
        self.assertEqual(self.pc['c1'].title, 'C 1')

    def testAddSubCategory(self):
        ''' Test that a sub category can be added
        '''
        self.login('manager')
        self.pc.invokeFactory('Category', id='p1', title='Parent 1')
        self.assertEqual(self.pc['p1'].title, 'Parent 1')
        self.pc['p1'].invokeFactory('Category', id='c1', title='Child 1')
        self.assertEqual(self.pc['p1']['c1'].title, 'Child 1')

    def testCategoryAlphaSorting(self):
        ''' Test that categories are sorted alphabeticaly
            NOTE: This test is known to fail.  Need to add alpha sorting
        '''
        self.login('manager')
        self.pc.invokeFactory('Category', id='bc', title='B Cat')
        self.pc.invokeFactory('Category', id='cc', title='C Cat')
        self.pc.invokeFactory('Category', id='acat', title='A Cat Long Title')
        self.pc['acat'].setTypes(('TaxonomyType:categories1',))
        self.pc['bc'].setTypes(('TaxonomyType:categories1',))
        self.pc['cc'].setTypes(('TaxonomyType:categories1',))
        self.folder.invokeFactory('TaxonomyType', id = 'tt1', Title = 'TT 1')
        self.tt1 = self.folder['tt1']
        # Note: getVocab is returning () here
        self.cv = self.pc.getVocab(self.tt1.schema['categories1'], self.tt1)
        titles = tuple([x['Title'] for x in self.cv])

        self.assertEqual(titles, ('Cat A Long Title', 'Cat B', 'Cat C'))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCategories))
    return suite

if __name__ == '__main__':
    framework()
