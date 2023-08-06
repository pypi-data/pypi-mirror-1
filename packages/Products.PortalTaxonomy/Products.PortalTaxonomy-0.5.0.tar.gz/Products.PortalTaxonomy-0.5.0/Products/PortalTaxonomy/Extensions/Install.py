from Products.CMFCore.utils import getToolByName,manage_addTool
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.ExternalMethod.ExternalMethod import ExternalMethod

from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes import listTypes
from Products.PortalTaxonomy import PROJECTNAME,product_globals

from StringIO import StringIO
import sys

def install(self):
    portal=getToolByName(self,'portal_url').getPortalObject()
    out = StringIO()

    # Install dependancies
    installDependencies(self, out)

    # Install and configure portal tools
    installCategoryManager(self, portal, out)
    installAttributeManager(self, portal, out)

    classes=listTypes(PROJECTNAME)
    installTypes(self, out, classes, PROJECTNAME)

    installIndexes(self, portal, out)

    installWorkflows(self)

    print >> out, "Successfully installed %s." % PROJECTNAME
    sr = PloneSkinRegistrar('skins', product_globals)
    print >> out,sr.install(self,position='custom',mode='after',layerName=PROJECTNAME)

    #register folderish classes in use_folder_contents
    props=getToolByName(self,'portal_properties').site_properties
    use_folder_tabs=list(props.use_folder_tabs)
    print >> out, 'adding classes to use_folder_tabs:'
    for cl in classes:
        print >> out,  'type:',cl['klass'].portal_type
        if cl['klass'].isPrincipiaFolderish and not cl['klass'].portal_type in []:
            use_folder_tabs.append(cl['klass'].portal_type)

    props.use_folder_tabs=tuple(use_folder_tabs)

    # Associate types with proper catalogs
    setupTypeCataloging(self, out)

    # Use PortalFactory creation process for designated types
    registerWithPortalFactory(self)

    return out.getvalue()

def installIndexes(self, portal, out):
    ct = getToolByName(self, 'portal_catalog')

    if 'recurseTypes' not in ct.indexes():
        print >> out, ct.addIndex('recurseTypes', 'KeywordIndex')
    else:
        print >> out, 'recurseTypes index already exists in portal_catalog'

    if 'getCategories' not in ct.indexes():
        print >> out, ct.addIndex('getCategories', 'KeywordIndex')
    else:
        print >> out, 'getCategories index already exists in portal_catalog'

    # Note: I wanted to use getAttributes here but that name seems to conflict
    # with something in Plone, hence the less than desirable getAttribs

    if 'getAttributes1' not in ct.indexes():
        print >> out, ct.addIndex('getAttributes1', 'KeywordIndex')
    else:
        print >> out, 'getAttributes1 index already exists in portal_catalog'
    if 'getAttributes2' not in ct.indexes():
        print >> out, ct.addIndex('getAttributes2', 'KeywordIndex')
    else:
        print >> out, 'getAttributes2 index already exists in portal_catalog'

    if 'isRootCategory' not in ct.indexes():
        print >> out, ct.addIndex('isRootCategory', 'FieldIndex')
    else:
        print >> out, 'isRootCategory index already exists in portal_catalog'

    if 'UID' not in ct.indexes():
        print >> out, ct.addIndex('UID', 'FieldIndex')
    else:
        print >> out, 'UID index already ixists in portal_catalog'

    # UID is needed in the metadata to build the CategoryWidget vocabulary
    try:
        ct.addColumn('UID')
    except:
        print 'UID metadata column already exists'

def installCategoryManager(self, portal, out):
    if hasattr(self, 'portal_categories'):
        print >> out, 'CategoryManager already installed, passing'
        return
    portal.manage_addProduct[PROJECTNAME].manage_addTool('CategoryManager')
    print >> out, 'CategoryManager successfully installed'

def installAttributeManager(self, portal, out):
    if hasattr(self, 'portal_attributes'):
        print >> out, 'AttributeManager already installed, passing'
        return
    portal.manage_addProduct[PROJECTNAME].manage_addTool('AttributeManager')
    print >> out, 'AttributeManager successfully installed'

def setupTypeCataloging(self, out):
    """ Register types with appropriate catalog
    """
    #at = getToolByName(self, 'archetype_tool')
    #at.setCatalogsByType('Category', ['uid_catalog',])
    pass

def registerWithPortalFactory(self):
    """ Registers types with portal factory
    """
    pf = getToolByName(self, 'portal_factory')
    types = pf.getFactoryTypes()
    types['Category'] = 1
    types['Attribute'] = 1
    types['AttributeCollection'] = 1
    pf.manage_setPortalFactoryTypes(listOfTypeIds=types)

def installDependencies(self, out):
    ''' Install products that PortalTaxonomy depends on
    '''
    qi = getToolByName(self, 'portal_quickinstaller')
    qi.installProduct('Archetypes')

def installWorkflows(self):
    ''' Setup workdlow info
    '''
    wft = getToolByName(self, 'portal_workflow')
    wft.setChainForPortalTypes( ('CategoryManager',), '')
    wft.setChainForPortalTypes( ('AttributeManager',), '')

def uninstall(self):
    out = StringIO()
    classes=listTypes(PROJECTNAME)

    #uninstallPortalAds(self, out)
    #uninstallCategoryManager(self, out)

    #unregister folderish classes in use_folder_contents
    props=getToolByName(self,'portal_properties').site_properties
    use_folder_tabs=list(props.use_folder_tabs)
    print >> out, 'removing classes from use_folder_tabs:'
    for cl in classes:
        print >> out,  'type:', cl['klass'].portal_type
        if cl['klass'].isPrincipiaFolderish and not cl['klass'].portal_type in []:
            if cl['klass'].portal_type in use_folder_tabs:
                use_folder_tabs.remove(cl['klass'].portal_type)

    props.use_folder_tabs=tuple(use_folder_tabs)

def uninstallCategoryManager(self, out):
    cp = getToolByName(self, 'portal_categories')
    if hasattr(self, 'portal_categories'):
        self.manage_delObjects(['portal_categories'])
        print >> out, "CategoryManager successfully uninstalled"
	return

    print >> out, "CategoryManager does not exist, passing uninstall"

def uninstallHideInNav(self, out, t):
    try:
        self.portal_properties.navtree_properties.metaTypesNotToList=list(self.portal_properties.navtree_properties.metaTypesNotToList)
        self.portal_properties.navtree_properties.metaTypesNotToList.remove(t)
    except ValueError:
        pass
    except:
        raise

class PloneSkinRegistrar:
    """
    Controls (un)registering of a layer in the skins tool:
     - the layer in the content of the skin tool
     - the layer in the path of all skins
    @author: U{Gilles Lenfant <glenfant@bigfoot.com>}
    @version: 0.1.0
    @ivar _layer: Name of the Product's subdirectory that contains
        the various layers for the Product.
    @type _layer: string
    @ivar _prodglobals: Globals from this Product.
    @type _propglobals: mapping object
    """

    def __init__(self, skinsdir, prodglobals):
        """Constructor
        @param skinsdir: Name of the Product's subdirectory that
            contains the various layers for the Product.
        @type skinsdir: string
        @param prodglobals: Globals from this Product.

            should be provided by Product's C{__init__.py} like this:

            C{product_globals = globals()}

        @type propglobals: mapping object
        @return: None
        """

        self._skinsdir = skinsdir
        self._prodglobals = prodglobals
        return

    def install(self, aq_obj,position=None,mode='after',layerName=None):
        """Installs and registers the skin resources
        @param aq_obj: object from which cmf site object is acquired
        @type aq_obj: any Zope object in the CMF
        @return: Installation log
        @rtype: string
        """

        rpt = '=> Installing and registering layers from directory %s\n' % self._skinsdir
        skinstool = getToolByName(aq_obj, 'portal_skins')

        # Create the layer in portal_skins

        try:
            if self._skinsdir not in skinstool.objectIds():
                addDirectoryViews(skinstool, self._skinsdir, self._prodglobals)
                rpt += 'Added "%s" directory view to portal_skins\n' % self._skinsdir
            else:
                rpt += 'Warning: directory view "%s" already added to portal_skins\n' % self._skinsdir
        except:
            # ugh, but i am in stress
            rpt += 'Warning: directory view "%s" already added to portal_skins\n' % self._skinsdir


        # Insert the layer in all skins
        # XXX FIXME: Actually assumes only one layer directory with the name of the Product
        # (should be replaced by a smarter solution that finds individual Product's layers)

        if not layerName:
            layerName = self._prodglobals['__name__'].split('.')[-1]

        skins = skinstool.getSkinSelections()

        for skin in skins:
            layers = skinstool.getSkinPath(skin)
            layers = [layer.strip() for layer in layers.split(',')]
            if layerName not in layers:
                try:
                    pos=layers.index(position)
                    if mode=='after': pos=pos+1
                except ValueError:
                    pos=len(layers)

                layers.insert(pos, layerName)

                layers = ','.join(layers)
                skinstool.addSkinSelection(skin, layers)
                rpt += 'Added "%s" to "%s" skin\n' % (layerName, skin)
            else:
                rpt += '! Warning: skipping "%s" skin, "%s" is already set up\n' % (skin, type)
        return rpt

    def uninstall(self, aq_obj):
        """Uninstalls and unregisters the skin resources
        @param aq_obj: object from which cmf site object is acquired
        @type aq_obj: any Zope object in the CMF
        @return: Uninstallation log
        @rtype: string
        """

        rpt = '=> Uninstalling and unregistering %s layer\n' % self._skinsdir
        skinstool = getToolByName(aq_obj, 'portal_skins')

        # Removing layer from portal_skins
        # XXX FIXME: Actually assumes only one layer directory with the name of the Product
        # (should be replaced by a smarter solution that finds individual Product's layers)

        if not layerName:
            layerName = self._prodglobals['__name__'].split('.')[-1]

        if layerName in skinstool.objectIds():
            skinstool.manage_delObjects([layerName])
            rpt += 'Removed "%s" directory view from portal_skins\n' % layerName
        else:
            rpt += '! Warning: directory view "%s" already removed from portal_skins\n' % layerName

        # Removing from skins selection

        skins = skinstool.getSkinSelections()
        for skin in skins:
            layers = skinstool.getSkinPath(skin)
            layers = [layer.strip() for layer in layers.split(',')]
            if layerName in layers:
                layers.remove(layerName)
                layers = ','.join(layers)
                skinstool.addSkinSelection(skin, layers)
                rpt += 'Removed "%s" to "%s" skin\n' % (layerName, skin)
            else:
                rpt += 'Skipping "%s" skin, "%s" is already removed\n' % (skin, layerName)
        return rpt
# /class PloneSkinRegistrar


