"""
Taken from some code off the internet.  Need to get proper attribution info here.
"""

#################################
# utility functions                
class ContentPermMap(dict): 

    def __setitem__(self, key, value):
        if key in self:
            values = self[key]
            if isinstance( values, str):
                values = [values]
            elif isinstance(values, tuple):
                values = list(value)

            if value is None or values is None:
                values = None
            elif isinstance(value, str ):
                values.append( value )
            elif isinstance(value, (list, tuple)):
                values.extend( list(value ) )
            else:
                raise SyntaxError("Unknown %r %r%"(values, value))
            value = values
                
        super(ContentPermMap, self).__setitem__(key, value)
        

def separateTypesByPerm( at_types,
                         content_types,
                         constructors,
                         permission_map ):

    res = {}

    default_perm = None
    used_types = []
    

    for permission in permission_map:
        portal_types = permission_map[ permission ]

        if portal_types is None:
            # default perm
            default_perm = permission
            continue

        types_for_perm = res.setdefault( permission, [])

        for idx, atype in enumerate(at_types):
            pt = atype['klass'].portal_type
            if pt in portal_types:
                assert pt not in used_types
                types_for_perm.append(
                    ( content_types[idx],
                      constructors[idx] )
                    )
                used_types.append( pt )
                

    if not default_perm:
        return res

    # handle default add permission 
    types_for_perm = res.setdefault( default_perm , [] )
        
    for idx, atype in enumerate(at_types ):
        pt = atype['klass'].portal_type
        if not pt in used_types:
            types_for_perm.append(
                ( content_types[idx],
                  constructors[idx] )                
                )

    return res

#################################
# initialize function in __init__ Module

def initialize( context ):
    my_types = atapi.listTypes(config.PROJECTNAME)
    content_types, constructors, ftis = atapi.process_types( my_types,
                                                             config.PROJECTNAME)
    
    # separate out the content types so we can register them in groups
    # based on permissions

    type_map = utils.separateTypesByPerm(
        my_types,
        content_types,
        constructors,
        permissions.ContentPermissionMap
        )

    for permission in type_map:
        factory_info = type_map[ permission ]
        content_types = tuple([fi[0] for fi in factory_info])
        constructors  = tuple([fi[1] for fi in factory_info])
        
        cmf_utils.ContentInit(
            config.PROJECTNAME + ' Content',
            content_types      = content_types,
            permission         = permission,
            extra_constructors = constructors,
            fti                = ftis,
            ).initialize(context)
    

