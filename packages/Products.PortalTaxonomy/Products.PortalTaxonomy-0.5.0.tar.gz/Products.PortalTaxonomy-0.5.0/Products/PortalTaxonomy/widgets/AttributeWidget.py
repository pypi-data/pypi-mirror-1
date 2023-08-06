"""
------------------------------------------------------------------------------
Name:         AttributeWidget.py
Purpose:      Use in conjunction with AttributeField
Author:       Jeremy Stark <jeremy@deximer.com>
Copyright:    (c) 2005 by Deximer
Licence:      GNU General Public Licence (GPL) Version 2 or later
------------------------------------------------------------------------------
"""

from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.Registry import registerWidget
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class AttributeWidget(MultiSelectionWidget):
    ''' Display attrbute type things
    '''
    security = ClassSecurityInfo()
    _properties = MultiSelectionWidget._properties.copy()
    _properties.update({ 'format' : 'checkbox'
                       , 'box_type' : 'checkbox'
                       , 'macro'  : 'attribute_widget'
                      })

InitializeClass(AttributeWidget)

registerWidget( AttributeWidget
              , title='Attribute'
              , description="Widget for the Attribute field."
              , used_for=('Products.PortalTaxonomy.fields.AttributeField',)
              )
