"""
------------------------------------------------------------------------------
Name:         __init__.py
Purpose:      Zope product init file
Author:       Jeremy Stark <jeremy@deximer.com>
Copyright:    (c) 2004 by Deximer, Inc.
Licence:      GNU General Public Licence (GPL) Version 2 or later
------------------------------------------------------------------------------
"""

from Globals import package_home
from Products.CMFCore import utils, DirectoryView
try:
    from Products.CMFCore import CMFCorePermissions
except:
    from Products.CMFCore import permissions as CMFCorePermissions
from Products.Archetypes.public import *
from Products.Archetypes import listTypes
from Products.Archetypes.utils import capitalize

import os, os.path

try:
    import CustomizationPolicy
except:
    print "Could not import CustomizationPolicy.  Maybe Plone >= 3?"

from ContentInitHack import separateTypesByPerm
from Permissions import ContentPermissionMap

PROJECTNAME = "PortalTaxonomy"

product_globals=globals()

DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/PortalTaxonomy', product_globals)

def initialize(context):
    from  Products.PortalTaxonomy.content import CategoryManager \
                                               , Category \
                                               , AttributeManager \
                                               , AttributeCollection \
                                               , Attribute
    import fields
    import widgets
    import examples

    the_types = listTypes(PROJECTNAME)
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    tools=[ CategoryManager
	  , AttributeManager
          ]
    utils.ToolInit( PROJECTNAME+' Tools'
                  , tools = tools
                  , product_name = PROJECTNAME
                  , icon='tool.gif'
                   ).initialize( context )

    type_map = separateTypesByPerm(
        the_types,
	content_types,
	constructors,
	ContentPermissionMap
	)

    i=0
    for permission in type_map:
        factory_info = type_map[ permission ]
        content_types = tuple([fi[0] for fi in factory_info])
        constructors  = tuple([fi[1] for fi in factory_info])

        utils.ContentInit( PROJECTNAME + ' Content %d' % i
                         , content_types = content_types
                         , permission = permission
                         , extra_constructors = constructors
                         , fti = ftis
                         ).initialize(context)

#    if CustomizationPolicy and hasattr(CustomizationPolicy,'register'):
#        CustomizationPolicy.register(context)
