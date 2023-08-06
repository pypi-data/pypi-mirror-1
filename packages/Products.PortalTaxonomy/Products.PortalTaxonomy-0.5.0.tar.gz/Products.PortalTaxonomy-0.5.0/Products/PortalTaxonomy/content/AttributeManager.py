'''
------------------------------------------------------------------------------
Name:         AttributeManager.py
Purpose:      Attributes are keyword like objects that may be associated
              with several portal types.
Author:       Jeremy Stark <jeremy@deximer.com>
Copyright:    (c) 2005 by Deximer
Licence:      GNU General Public Licence (GPL) Version 2 or later
------------------------------------------------------------------------------
'''

from sets import Set

from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
try:
    from Products.CMFCore import CMFCorePermissions
except:
    from Products.CMFCore import permissions as CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.base import ATCTContent

from Products.PortalTaxonomy.fields import AttributeField, CategoryField
from Products.PortalTaxonomy.content.schemata import AttributeManagerSchema, \
    AttributeSchema, AttributeCollectionSchema

class AttributeManager(ATFolder, PloneBaseTool, UniqueObject):
    ''' Control tool for portal_attributes
    '''
    portal_type     = meta_type = archetype_name = 'AttributeManager' 
    security        = ClassSecurityInfo()
    schema          = AttributeManagerSchema
    content_icon    = 'attributemanager.gif'
    typeDescription = 'Attribute Manager'
    typeDescMsgId   = 'description_edit_attributemanager'
    global_allow          = 0
    allowed_content_types = ('AttributeCollection', )
    filter_content_types  = 1
    immediate_view        = 'folder_contents'

    def __init__(self):
        ''' This is a portal tool so just set the id and other object attributes
        '''
        BaseFolder.__init__(self, 'portal_attributes')
        self.setTitle('Attributes')

    def getAttributesFor(self, instance):
        ''' Get attributes for the instance type
            NOTE: Need to write
        '''
        pass

    def getAvailableTypes(self):
        ''' Return types that are linked to Attributes
        '''
        result = []
        portalTypes = getToolByName(self, 'portal_types').listTypeInfo()
        pt = [t.Metatype() for t in portalTypes]
        types = [t for t in listTypes() if t['klass'].meta_type in pt]
        for type in types:
            schema = type['klass'].schema
            for field in schema.values():
                if field.getType()[-14:] == 'AttributeField' or \
                   field.getType()[-24:] == 'AttributeCollectionField':
                    result.append(type['klass'].meta_type + ':' + field.getName())
        return DisplayList([(x, x) for x in result])

    def getVocab(self, instance):
        ''' return a vocab for a calling object
        '''
        result = {}
        type = instance.getTypeInfo().Metatype() + ':' + instance.getName()
        collections = self.listFolderContents()
        for c in collections:
            if type in c.type_restrictions:
                result[c.title] = DisplayList([(a.UID(), a.title_or_id()) for a in c.listFolderContents()])
        return result

    def getFlatVocab(self, instance):
        ''' return a vocab for a calling object
        '''
        attribs = DisplayList()
        type = instance.getTypeInfo().Metatype() + ':' + instance.getName()
        collections = self.listFolderContents()
        for c in collections:
            if type in c.type_restrictions:
                for a in c.listFolderContents():
                    attribs.add(a.UID(), c.title_or_id() + ' : ' + a.title_or_id())
        return attribs


class AttributeCollection(ATFolder):
    ''' Holds groups of attributes and assigns them to content types
    '''
    portal_type = meta_type = 'AttributeCollection' 
    archetype_name  = 'Attribute Collection'
    security        = ClassSecurityInfo()
    schema          = AttributeCollectionSchema
    content_icon    = 'attributecollection.gif'
    typeDescription = 'A container for grouping attributes'
    typeDescMsgId   = 'description_edit_attributecollection'
    global_allow          = 0
    allowed_content_types = ('Attribute',)
    filter_content_types  = 1
    immediate_view        = 'base_view'
    _at_rename_after_creation = True

    def canSetDefaultPage(self):
        ''' No dynamic views
        '''
        return False

    def getTypesVocab(self):
        ''' return types associated with AttributeManager
        '''
        return getToolByName(self, 'portal_attributes').getAvailableTypes()

    actions = ({ 'id': 'attribute_utilities'
               , 'name': 'Utilities'
               , 'action': 'attribute_utilities'
               , 'visible': 1
               , 'permissions': (CMFCorePermissions.ManagePortal,)
               , 'category': 'object'
              },)

class Attribute(ATCTContent):
    ''' Individualy selectable items contained in an attribute collection
    '''
    portal_type = meta_type = archetype_name = 'Attribute' 
    security        = ClassSecurityInfo()
    schema          = AttributeSchema
    content_icon    = 'attribute.gif'
    typeDescription = 'An attribute'
    typeDescMsgId   = 'description_edit_attribute'
    global_allow    = 0
    _at_rename_after_creation = True

    def getContent(self, review_state = 'published'):
        '''Returns published site content associated with this Attribute
        '''
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.searchResults(
            getAttributes = self.UID()
          , review_state = review_state)

registerType(AttributeManager)
registerType(AttributeCollection)
registerType(Attribute)

