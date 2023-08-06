# Importing module dependencies
from Products.CMFCore import DirectoryView as cmfdirview
from Products.CMFCore import utils as cmfutils
from Products.CMFCore import permissions as cmfcp
from Products.Archetypes import public as atapi

from field import RoleField

GLOBALS = globals()

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    import example.demo
    project_name = 'archetypes.rolefield'

    # Process the project's types
    content_types, constructors, ftis = \
        atapi.process_types(atapi.listTypes(project_name), project_name)

    cmfutils.ContentInit(
        meta_type           = project_name + ' Content',
        content_types       = content_types,
        permission          = cmfcp.AddPortalContent,
        extra_constructors  = constructors,
        fti                 = ftis,
    ).initialize(context)
