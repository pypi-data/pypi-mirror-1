'''
------------------------------------------------------------------------------
Name:         TaxonomyType.py
Purpose:      Example type that uses CategoryManager and AttributeManager.
              Uncomment the #import examples line in __init__.py to use this
Author:       Jeremy Stark <jeremy@deximer.com>
Copyright:    (c) 2005 by Deximer
Licence:      GNU General Public Licence (GPL) Version 2 or later
------------------------------------------------------------------------------
'''

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.PortalTaxonomy.fields import AttributeField, CategoryField

class TaxonomyType(BaseContent):
    security = ClassSecurityInfo()
    portal_type = meta_type = archetype_name = 'TaxonomyType' 

    schema=BaseSchema + Schema((
        CategoryField('categories'),
        AttributeField('attributes1'),
        AttributeField('attributes2')
    ),)

    factory_type_information={
        'allowed_content_types':() ,
        'immediate_view':'base_view',
        'global_allow':1,
        'filter_content_types':0,
        }

    actions=()

registerType(TaxonomyType)
