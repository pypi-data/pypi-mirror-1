from Products.ATContentTypes.atct import ATFolder, ATCTContent
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.Archetypes.public import Schema, LinesField, MultiSelectionWidget, ImageField

AttributeManagerSchema = ATFolder.schema.copy()

AttributeCollectionSchema = ATFolder.schema.copy() + Schema((
        LinesField( 'type_restrictions'
          , widget = MultiSelectionWidget(
                size = 10
              , label = "Type Restriction"
              , description = "Select the default type restrictions for "
                              "attributes in this collection"
            )
          , vocabulary = "getTypesVocab"
          , enforceVocabulary = True
        )
    ),)

AttributeSchema = ATCTContent.schema.copy() + Schema((
        ImageField( 'image'
                  , original_size = (32, 32)
                  , sizes = {'small' : (16, 16)
                            ,'medium': (24, 24)
                            ,'large' : (32, 32)}
        ),
    ))

CategorySchema = ATFolder.schema.copy() + Schema((
        LinesField(
            'Types'
          , widget = MultiSelectionWidget( size = 6
          , description = 'Select the content types allowed in this Category. '
                          'Associating a type with a category causes the  '
                          'category (and sub-categories) to become available '
                          'for selection in the category field of that type.'
                          '<br>\n <i>Note: selecting nothing is a special case'
                          ' - if you select no types, this category will '
                          'inherit types from parent categories.</i>'
              , label = 'Type Associations'
            )
          , vocabulary = 'getTypesVocab'
          , mutator = 'setTypes'
          , enforceVocabulary = True
        ),
    ),)

finalizeATCTSchema(CategorySchema)
finalizeATCTSchema(AttributeManagerSchema)
finalizeATCTSchema(AttributeCollectionSchema)
finalizeATCTSchema(AttributeSchema)
