"""
# testAttributes.py
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PortalTaxonomy.tests import TestCase

from Testing import ZopeTestCase

class TestAttributes(TestCase.PortalTaxonomyTestCase):

    def testAddAttributeCollection(self):
        ''' Add an attribute collection
        '''
        self.login('manager')
        self.pa.invokeFactory('AttributeCollection',id = 'ac1', title = 'AC 1')
        self.assertEqual(self.pa['ac1'].title, 'AC 1')

    def testAddAttribute(self):
        ''' Add an attribute to an attribute collection
        '''
        self.login('manager')
        self.pa.invokeFactory('AttributeCollection',id = 'pac1', title = 'AC 1')
        self.assertEqual(self.pa['pac1'].title, 'AC 1')
        self.pa['pac1'].invokeFactory('Attribute', id = 'a1', title = 'A 1')
        self.assertEqual(self.pa['pac1']['a1'].title, 'A 1')

    def testAddTaxonomyType(self):
        self.login('manager')
        self.folder.invokeFactory('TaxonomyType', id = 'tt1', Title = 'TT 1')

    def testEditAttributeCollection(self):
        ''' Testing editing of AttributeCollections
        '''
        self.login('manager')
        self.pa.invokeFactory('AttributeCollection',id = 'ac1', title = 'AC 1')
        self.ac1 = getattr(self.pa, 'ac1')
        
        self.ac1.setTitle('Test title')
        self.ac1.setDescription('Test description')
        self.ac1.setType_restrictions(['TaxonomyType:attributes1',])

        self.assertEqual(self.ac1.Title(), 'Test title')
        self.assertEqual(self.ac1.Description(), 'Test description')
        self.assertEqual(self.ac1.getType_restrictions(),('TaxonomyType:attributes1',))

    def testEditAttribute(self):
        ''' Testing editing of Attributes
        '''
        self.login('manager')
        self.pa.invokeFactory('AttributeCollection',id = 'ac1', title = 'AC 1')
        self.ac1 = getattr(self.pa, 'ac1')
        self.ac1['ac1'].invokeFactory('Attribute', id = 'a1', title = 'A 1')
        self.a1 = getattr(self.pa['ac1'], 'a1')
        
        self.a1.setTitle('Test title')
        self.a1.setDescription('Test description')

        self.assertEqual(self.a1.Title(), 'Test title')
        self.assertEqual(self.a1.Description(), 'Test description')

    def testEditTaxonomyType(self):
        ''' Test assigning vocab items to TaxonomyType
        '''
        self.login('manager')
        self.pa.invokeFactory('AttributeCollection',id = 'ac1', title = 'AC 1')
        self.ac1 = self.pa['ac1']
        self.ac1.setType_restrictions(['TaxonomyType:attributes1',])
        self.folder.invokeFactory('TaxonomyType', id = 'tt1', Title = 'TT 1')
        self.tt1 = self.folder['tt1']
        self.tt1.setAttributes1(('ac1',))
        # This should really fail as we have not assigned ac1 to this field...
        self.tt1.setAttributes2(('ac1',))

        self.assertEqual(self.tt1.getAttributes1(), ('ac1',))

    def testAttributeCollectionTypeRestrictions(self):
        ''' Test AttributeCollection.getType_restrictions
        '''
        self.login('manager')
        self.pa.invokeFactory('AttributeCollection',id = 'ac1', title = 'AC 1')
        self.ac1 = getattr(self.pa, 'ac1')
        self.assertEqual(self.ac1.getType_restrictions(), ())

    def testAttributeManagerVocab(self):
        ''' Test AttributeManger.getAvailableTypes
        '''
        self.login('manager')
        self.assertEqual(self.pa.getAvailableTypes(), self.acv)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAttributes))
    return suite

if __name__ == '__main__':
    framework()
