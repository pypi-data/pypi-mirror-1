'''
------------------------------------------------------------------------------
Name:         CategoryManager.py
Purpose:      CategoryManager provides a treeish category structure to
              assoiate objects to.  The tree is made up of folderish Category
              node objects, which provide recursive functions.
Author:       Jeremy Stark <jeremy@deximer.com>
              Joseph Zicarelli <jdz@deximer.com>
Copyright:    (c) 2005 by Deximer
Licence:      GNU General Public Licence (GPL) Version 2 or later
------------------------------------------------------------------------------
'''

from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
try:
    from Products.CMFCore import CMFCorePermissions
except:
    from Products.CMFCore import permissions as CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.Archetypes import listTypes
from Products.ATContentTypes.atct import ATFolder, ATCTContent

from Products.PortalTaxonomy.content.schemata import CategorySchema

from sets import Set

class CategoryManager(PloneBaseTool, ATCTContent):
    portal_type = meta_type = archetype_name = 'CategoryManager' 
    security        = ClassSecurityInfo()
    schema          = ATCTContent.schema.copy()
    tool_icon       = 'categorymanager.gif'
    typeDescription = 'Category Manager'
    typeDescMsgId   = 'description_edit_categorymanager'

    def __init__(self):
        ATCTContent.__init__(self, 'portal_categories')
        self.setTitle('Category Tool')

    def recurseTypes(self):
        ''' Stopper function: this is the bottom.  Simply return.
            NOTE: Not needed?  CategoryManager no longer top of tree
        '''
        return []

    def getSubCategories(self, type=None):
        ''' Lists all Category objects directly within this Category
            NOTE: This should do a catalog query for isRootCategory Categories
        '''
        cats = getToolByName(self, \
            'portal_url').getPortalObject().objectValues(['Category',])
        if type is None:
            return cats
        result = []
        type_name = type.getTypeInfo().Metatype() + ':' + type.getName()
        for cat in cats:
            if cat.testTypes(type_name):
                result.append(cat)
        return result

    def getVocab(self, field, instance, depth=None):
        ''' Return a treeish vocab suitable for a CategoryField
        '''
        pc = getToolByName(self,'portal_catalog')

        instance_type = getattr(instance.aq_explicit, 'meta_type', None)
        if instance_type:
            type_restriction = '%s:%s' %(instance_type,field.getName())

        query = {}
        portal_path = self.portal_url.getPortalPath()
        query['path'] = portal_path
        query['portal_type'] = 'Category'
        query['review_state'] = 'published'
        query['recurseTypes'] = type_restriction

        categories = {}
        results = pc.searchResults(query)

        if not results:
            return [], []

        cats = [cat for cat in results]
        cats.sort(lambda x, y: cmp(len(x.getPath()), len(y.getPath())))

        for result in cats:
            path_str = result.getPath()
            path = path_str.split('/')
            parent_path = path[:-1]
            parent_path_str = '/'.join(parent_path)
            data = {'UID': result.UID,
                'Title': result.Title,
                'children': [],
            }

            if categories.has_key(parent_path_str):
                categories[parent_path_str]['children'].append(path_str)

            categories[path_str] = data

        # Get Parent Categories
        vocab = []
        for path in categories.keys():
            parent_path = '/'.join(path.split('/')[:-1])
            if categories.has_key(parent_path):
                continue
            data = categories.get(path)
            children = self.getAllChildren(categories,data['children'])
            children.sort(lambda x, y: cmp(x[1], y[1]))
            vocab.append((data['UID'],data['Title'],children))
        display_list = DisplayList()
        for c in results:
            display_list.add(c.UID, c.Title)
        return vocab, display_list

    def getAllChildren(self,categories,child_paths):
        children = []
        for child_path in child_paths:
            child = categories.get(child_path,None)
            grandkids = self.getAllChildren(categories,child['children'])
            grandkids.sort(lambda x, y: cmp(x[1], y[1]))
            children.append((child['UID'],child['Title'],grandkids))
        return children

    def testTypes(self, type):
        """
        types -- list from the types restriction field
        type -- the type of an object we're testing agenst

        return True if:
         * types is empty (or null)
         * type is in types -- a match!
        """
        types = self.getTypes()
        if not types or type in types:
            return True
        return False

    factory_type_information={
        'allowed_content_types':('Category', ),
        'content_icon':'categorymanager.gif',
        'global_allow':0,
        'filter_content_types':1
        }

class Category(ATFolder):
    ''' A Category type for PortalTaxonomy
    '''
    portal_type = meta_type = archetype_name = 'Category' 
    security              = ClassSecurityInfo()
    schema                = CategorySchema
    immediate_view        = 'folder_contents'
    content_icon          = 'category.gif'
    typeDescription       = 'Building block for site taxonomy trees'
    typeDescMsgId         = 'description_edit_category'
    default_view          = 'folder_contents'
    suppl_views           = ()
    allowed_content_types = ('Category',)
    filter_content_types  = 1
    global_allow          = 1
    _at_rename_after_creation = True

    def at_post_edit_script(self):
        ''' Recatalog subcategories
        '''
        pc = getToolByName(self, 'portal_catalog')

        query = {}
        query['path'] = '/'.join(self.getPhysicalPath())
        query['portal_type'] = 'Category'

        results = pc.searchResults(query)
        for category in results:
            category.getObject().reindexObject()
        
    def setTypes(self, value, parent=None):
        ''' Recursive mutator to update category types.
            This is needed because of dynamic vocabularies
        '''
        value = [x for x in value if x]  # remove None values
        self.Types = value  # store the new value

        if value:
            parent = value
        if not parent:
            return

        for cat in self.getSubCategories():
            cat.setTypes(Set(parent).intersection(cat.getTypes()), parent)

    def recurseTypes(self):
        ''' Two cases:
             -types is empty: ask parent
             -types is not empty: return types
        '''
        myTypes = self.getTypes()
        if myTypes:
            return myTypes
        else:
            if hasattr(self.aq_parent, 'recurseTypes'):
                return self.aq_parent.recurseTypes()
            else:
                return []

    def getTypesVocab(self):
        ''' Wrapper for recursive recurseTypes(), compares to AvailableTypes
        '''
        parentTypes = []
        if hasattr(self.aq_parent, 'recurseTypes'):
            parentTypes = self.aq_parent.recurseTypes()
        if parentTypes:
            return parentTypes
        else:
            return self.getAvailableTypes()

    def getAvailableTypes(self):
        ''' Return types that have a CategoryField in their schema
        '''
        result = []
        portalTypes = getToolByName(self, 'portal_types').listTypeInfo()
        pt = [t.Metatype() for t in portalTypes]
        types = [t for t in listTypes() if t['klass'].meta_type in pt]
        for type in types:
            schema = type['klass'].schema
            for field in schema.values():
                if field.getType()[-13:] == 'CategoryField':
                    result.append(type['klass'].meta_type + ':' + field.getName())
        return DisplayList([(x, x) for x in result])

    def getSubCategories(self, type=None):
        ''' Lists all Category objects directly within this Category
        '''
        cats = self.listFolderContents()
        if type is None:
            return cats
        result = []
        type_name = type.getTypeInfo().Metatype()
        for cat in cats:
            if cat.testTypes(type_name):
                result.append(cat)
        return result

    def getContent(self, review_state = 'published'):
        ''' Returns published site content assoiated with this Category
        '''
        catalog = getToolByName(self, 'portal_catalog')
        return catalog.searchResults(
            getCategories = self.UID()
          , review_state = review_state
          )

    def getVocabTree(self, instance, depth=None, path=''):
        ''' Recursevly lists Categories up to `depth' Categories deep.
            Output tailored for creation of a DisplayList.
        '''
        cats = []
        type_field = instance.meta_type + ':' + instance.getName()
        if (depth is None) or (depth > 0):
            if depth is not None:
                depth -= 1
            for cat in self.getSubCategories():
                if cat.testTypes(type_field):
                    guid = cat.UID()
                    title = cat.title
                    localPath = path + title
                    cats.append([guid, localPath])
                    cats += list(cat.getVocabTree(instance, depth, localPath + '/'))
        return cats

    def getVocab(self, instance, depth=None):
        ''' Wrapper for getVocabTree(), returns DisplayList for vocabs
            NOTE: This may need to look at instance.metatype
        '''
        return DisplayList(self.getVocabTree(instance, depth=depth))

    def testTypes(self, type):
        """
        types -- list from the types restriction field
        type -- the type of an object we're testing agenst

        return True if:
         * types is empty (or null)
         * type is in types -- a match!
        """
        types = self.getTypes()
        if not types or type in types:
            return True
        return False

    def isRootCategory(self):
        ''' Returns True if this is a root node
        '''
        return not hasattr(self.aq_parent, 'isRootCategory')

    actions=(
    { 'id': 'category_utilities'
    , 'name': 'Utilities'
    , 'action': 'category_utilities'
    , 'visible': 1
    , 'permissions': (CMFCorePermissions.ManagePortal,)
    , 'category': 'object'
    },
    )

registerType(CategoryManager)
registerType(Category)
registerType(ATFolder)
