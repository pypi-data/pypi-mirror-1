Preamble

  Since writing PortalTaxonomy several products have come along to fill the need for more advanced taxonomy management than is available out of the box with Plone.  PT's niche, I think, is that it is very easy to integrate into a Plone site that wants to expose it's taxonomy as navigational elements.  Also, I find the CategoryWidget and AttributeWidget interfaces helpful for providing clients with an easy inteface for entering taxonomy information.

  The main motivation was to have a centralized, recursive, categorization
  structure that could be associated with groups of content types.  The
  current Plone KeyWord system allows for only a 1 to 1 mapping of keyword lists to types.  KeyWords are also a flat list and I needed something that was
  treeish.

PortalTaxonomy

  PortalTaxonomy provides two new primary content types: Categories and Attributes.  Categories are heirarchical taxonomy nodes.  You create a Category tree and then associate parts (or all) of the tree with various content types.  By associating sections of the Category tree with a type, the types CategoryField will render that section of the Category tree in it's widget and allow users to select nodes in the tree with which to associate the content.

  Attributes are grouped within a content type called AttributeCollection.  An AttributeCollection is than associated with one or more content types.  Content types associated with an AttributeCollection will have the Attributes within the Collection available as selection options within their AttributeField.  You may specify how the AttributeWidget renders the selection options: as checkboxes; radio buttons; or selection lists.  Each AttributeCollection is wrapped in in own grouping from which a user makes selections.

  Categories

    Categories allow site planners to create a treeish category structures and then associate content types with parts of the tree.  Content types that use the provided CategoryField may be associated with categories within the tree.

  To create an association between part of the Category tree and a content type, select the category that you want to associate.  You will see a field called "Type Associations" that lists all the content types that have a CategoryField in their schema.  Select the fields you want to associate with this section of the tree.  The associated category and all sub categories will be available for selection in the types field.

  Attribute Manager

    This tool allows site planners to create "attribute collections" and than
    associate those collections with types by including an AttributeField in
    the content types schema.  Attribute field is in the fields module
    included with PortalTaxonomy.

    The AttributeWidget has several options available for rendering the attribute collections: as checkboxes; as radio buttons; and as selection lists.

    Checkboxes allow a user to select as many attributes as they like from all associated Attributes.  Selection lists do the same thing but present a multi selection list for each attribute collection associated with the field.  Radio boxes allow a user to select one attribute from all available attributes.

    To select a Checkbox, set the format property of AttributeWidget to "checkbox":

    format="checkbox"

    To select radio boxes, set the format property of AttributeWidget to "checkbox" and the box_type property to "radio":

    format="checkbox",
    box_type="radio"

    To select selection lists, set the format attribute of AttrivuteWidget to "select":

    format="select"

Installation

  Put the PortalTaxonomy folder in Zope's Products directory and restart Zope.  Create a Plone site.  Go to Plone Setup->Add/Remove Products.  Select PortalTaxonomy from the list and click the install button.

  An example type called TaxonomyType is automatically installed so you cna get started testing your taxonomy.

  If you do not want the example type TaxonomyType to be installed, comment the
  line:

  import example

  in __init__.py

More on Usage

  Both Category Manager and Attribute Manager look for Archetypes that use the
  CategoryField and AttributeField, respectivly, in their schemas.
  Archetypes that use these fields will appear in a Categories or Attribute
  Collections "type restrictions" selection box.  If no archetypes use those
  fields then the type restirctions selection box will be empty.  To add a
  sample type, uncomment the #import example line in __init__.py, restart Zope
  and reinstall PortalTaxonomy (or install the TaxonomyType manually through
  the portal_types tool).  This will give you a quick type to start playing
  with.

  Category Manager

    Create an Archetype that uses the PortalTaxonomy.fields.CategoryField field.  Add categories and sub categories in your portal as needed, associating at least some of them with your new Archetype.  Publish the Categories. Add a new instance of your Archetype.  A category field selector should be available.  Click on the categories to tree out sub categories. The category selector uses a modified nested pick list designed by Christian Heilman (http://icant.co.uk).

  AttributeManager

    Create an Archetype that uses the PortalTaxonomy.fields.AttributeField.  Add attribute collections to AttributeManager and associate at least some of them with your new Archetype.  Publish your AtributeCollections and Attributes.  Add an instance of your new archetype and check desired attributes.

  Catalog Indexes

  Don't forget to add indexes to portal_catalog that corespond to your
  Category and Attribute fields.  There is a helper method called getContent
  in both Attribute and Category manager.  It is hard coded to indexes that
  are called 'categories' and 'attribs' respectivly.  You can either name
  your fields after these, modify the method or use catalog queries in your
  page templates instead of the helper method.

  Take a look in the skins directory for some example page templates,
  specificaly: category_listing.pt, category_recursive.pt, list_view.pt, 
  category_content.pt and category_content_recursive.pt.  Also look at the
  scripts getCategorizedContent.py and getSubcategoryUIDs.py.

Integrating Categories With a Site

  I added two templates as examples for getting content associated with a category:

  category_content.pt
  category_content_recursive.pt

  Also two scripts used by the templates as examples for doing the actual queries:

  getCategorizedContent.py
  getSubcategoryUIDs.py

Remember you need catalog indexes for your CategoryFields. e.g. if you
have a CategoryField called "foobar" add "getFoobar" as a
portal_catalog index of type KeywordIndex.

Contacting Me

  If you have any comments regarding this product, please drop me an e-mail: jeremy@deximer.com.  Thanks :)
