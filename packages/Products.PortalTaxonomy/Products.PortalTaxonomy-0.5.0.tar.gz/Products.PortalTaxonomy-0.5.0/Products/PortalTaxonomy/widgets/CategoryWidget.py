"""
------------------------------------------------------------------------------
Name:         CategoryWidget.py
Purpose:      Use in conjunction with CategoryField
Author:       Jeremy Stark <jeremy@deximer.com>
Copyright:    (c) 2005 by Deximer
Licence:      GNU General Public Licence (GPL) Version 2 or later
------------------------------------------------------------------------------
"""
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.Registry import registerWidget
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class CategoryWidget(MultiSelectionWidget):
    ''' Displays a heirachy of categories from CategoryManager vocab
    '''
    security = ClassSecurityInfo()
    _properties = MultiSelectionWidget._properties.copy()
    _properties.update({ 'macro' : 'category_widget'
                       , 'helper_css' : ('category_widget.css',)
                       , 'helper_js'  : ('category_widget.js',)
                      })

InitializeClass(CategoryWidget)

registerWidget( CategoryWidget
              , title='Category'
              , description="Widget for the Category field."
              , used_for=('Products.PortalTaxonomy.fields.CategoryField',)
              )
