"""
------------------------------------------------------------------------------
Name:         CategoryField.py
Purpose:      Displays a vocabulary provided by portal_categories.  Causes the
              type to be available in a categories type selector
Author:       Jeremy Stark <jeremy@deximer.com>
Copyright:    (c) 2005 by Deximer
Licence:      GNU General Public Licence (GPL) Version 2 or later
------------------------------------------------------------------------------
"""

from Products.Archetypes.Registry import registerField, registerPropertyType
from Products.Archetypes.Field import LinesField
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.PortalTaxonomy.widgets import CategoryWidget

class CategoryField(LinesField):
    """ Field that links up with Category
    """
    security = ClassSecurityInfo()

    _properties = LinesField._properties.copy()
    _properties.update({ 'type' : 'category'
                       , 'widget' : CategoryWidget
                      })

    def Vocabulary(self, instance):
        ''' Ask Category what should be displayed
        '''
        return getToolByName(self, 'portal_categories').getVocab(self, instance)

    def getSubCategories(self):
        ''' Ask Category what should be displayed
        '''
        return getToolByName(self, 'portal_categories').getSubCategories(self)

InitializeClass(CategoryField)

registerField( CategoryField
             , title="Category Field"
             , description="Displays appropriate items from Category"
             )
