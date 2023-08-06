"""
Permission map for ContentInitHack.

If you want seperate permisions for Attrbutes and Categories, uncomment the lines.
"""

from ContentInitHack import ContentPermMap
try:
    from Products.CMFCore import CMFCorePermissions as CMFPerms
except:
    from Products.CMFCore import permissions as CMFPerms

#ADD_CATEGORY   = 'PortalTaxonomy: Add Category'
#ADD_ATTRIBUTE = 'PortalTaxonomy: Add Attribute'

ContentPermissionMap = ContentPermMap()
#ContentPermissionMap[ ADD_CATEGORY ] = 'Category'
#ContentPermissionMap[ ADD_ATTRIBUTE ] = 'AttributeCollection'
#ContentPermissionMap[ ADD_ATTRIBUTE ] = 'Attribute'

# our way of saying all the other content types should get this permission
ContentPermissionMap[ CMFPerms.AddPortalContent ] =  None

