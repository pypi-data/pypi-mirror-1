"""
An example content type using LDAPStorage.
"""

from Products.Archetypes import public as atapi
from archetypes.ldapstorage import LDAPStorage
from archetypes.ldapstorage import config

attr_mapping = {
    # at field: ldap attr
    'name': 'cn',
    'surname': 'sn',
}

def get_storage(field_id):
    return LDAPStorage(
        'cn',
        'name',
        attr_mapping[field_id],
        default_attrs = {
            'objectClass': ['inetOrgPerson'], 
        },
        required_attrs = ['sn', 'cn'],
    )
    

schema = atapi.BaseSchema + atapi.Schema((
    atapi.StringField(
        'name',
        #default = 'My Name',
        storage=get_storage('name'),
    ),
    atapi.StringField(
        'surname',
        #default = 'My Surname',
        storage=get_storage('surname'),
    ),
))

class ExampleContent2(atapi.BaseContent):
    """ Another example content type using LDAPStorage.
    """
    portal_type = meta_type = 'ExampleContent2'
    archetype_name = 'Example Content 2'

    schema = schema

    _at_rename_after_creation = True

atapi.registerType(ExampleContent2, config.PROJECT_NAME)
