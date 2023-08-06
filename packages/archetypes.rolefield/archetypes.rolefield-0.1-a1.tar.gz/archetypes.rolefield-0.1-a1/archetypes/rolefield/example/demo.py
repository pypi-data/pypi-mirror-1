from Products.Archetypes import public as atapi
from archetypes.rolefield import RoleField

from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeBaseSchema

class RoleFieldDemoContent(ATCTContent):
    """ A demo content type using RoleField.
    """
    meta_type = 'RoleFieldDemoContent'
    portal_type = 'RoleFieldDemoContent'


    schema = ATContentTypeBaseSchema.copy() + atapi.Schema((
        RoleField(
            'team',
            role = 'Owner',
            widget = atapi.MultiSelectionWidget(
                label = 'Team',
            ),
        ),
    ))


atapi.registerType(RoleFieldDemoContent, 'archetypes.rolefield')