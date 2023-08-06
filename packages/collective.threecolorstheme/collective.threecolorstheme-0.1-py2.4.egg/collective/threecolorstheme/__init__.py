# patch collective phantasy config
import phantasyconfig
from Products.CMFCore.utils import ContentInit
from Products.Archetypes.public import process_types, listTypes
from config import PROJECTNAME
from permissions import permissions, wireAddPermissions
import content
wireAddPermissions()   


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    type_list = listTypes(PROJECTNAME)
    content_types, constructors, ftis = process_types(type_list, PROJECTNAME)

    # Assign an own permission to all content types
    all_types = zip(content_types, constructors)
    for atype, constructor in all_types:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        errors=[]
        ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permissions[atype.portal_type],
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)  
