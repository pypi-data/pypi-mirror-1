"""
------------------------------------------------------------------------------
Name:         AttributeField.py
Purpose:      Displays a vocabulary provided by portal_attributes.  Causes the
              type to be available in the AttributeCollection type selector
Author:       Jeremy Stark <jeremy@deximer.com>
Copyright:    (c) 2005 by Deximer
Licence:      GNU General Public Licence (GPL) Version 2 or later
------------------------------------------------------------------------------
"""

from Products.Archetypes.Registry import registerField, registerPropertyType
from Products.Archetypes.Field import LinesField
from Products.Archetypes.Widget import MultiSelectionWidget
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.PortalTaxonomy.widgets import AttributeWidget

class AttributeField(LinesField):
    """ Field that links up with AttributeManager
    """
    security = ClassSecurityInfo()

    _properties = LinesField._properties.copy()
    _properties.update({ 'type' : 'attribute'
                       , 'widget' : AttributeWidget
                      })

    def Vocabulary(self, key):
        ''' Ask AttributeManager what should be displayed
        '''
        return getToolByName(self, 'portal_attributes').getVocab(self)

    def getFlatVocab(self, key):
        ''' Ask AttributeManager what should be displayed
        '''
        return getToolByName(self, 'portal_attributes').getFlatVocab(self)

InitializeClass(AttributeField)

registerField( AttributeField
             , title="Attribute Field"
             , description="Displays appropriate items from AttributeManager"
             )
