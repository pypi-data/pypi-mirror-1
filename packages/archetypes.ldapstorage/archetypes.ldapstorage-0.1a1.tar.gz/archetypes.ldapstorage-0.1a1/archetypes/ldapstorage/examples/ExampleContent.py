"""
An example content type using LDAPStorage.
"""

from Products.Archetypes import public as atapi
from archetypes.ldapstorage import LDAPStorage
from archetypes.ldapstorage import config

attr_mapping = {
    # at field: ldap attr
    'lastname': 'sn',
    'address': 'homePostalAddress',
    'photo': 'jpegPhoto',
}

def get_storage(field_id):
    return LDAPStorage(
        'uid',
        'getId',
        attr_mapping[field_id],
        default_attrs = {
            'objectClass': ['inetOrgPerson'], 
            'cn': ['test name'],
        },
        required_attrs = ['sn', 'cn'],
    )

schema = atapi.BaseSchema + atapi.Schema((
    atapi.StringField(
        'lastname',
        default = 'Test lastname',
        required = 1,
        # It is also required in LDAP, so it must have a default value.
        storage = get_storage('lastname'),
    ),
    atapi.TextField(
        'address',
        storage = get_storage('address'),
    ),
    atapi.ImageField(
        'photo',
        storage = get_storage('photo'),
    ),
))


class ExampleContent(atapi.BaseContent):
    """ An example content type using LDAPStorage.
    """

    portal_type = meta_type = 'ExampleContent'
    archetype_name = 'Example Content'

    schema = schema

    _at_rename_after_creation = True

atapi.registerType(ExampleContent, config.PROJECT_NAME)
