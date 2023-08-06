"""
Configuration of LDAPConnection unit tests.
"""

LDAP_SETTINGS = {
    'url': 'ldap://localhost',
    'base_dn': 'ou=people,dc=localhost,dc=localdomain',
    'bind_dn': 'cn=Manager,dc=localhost,dc=localdomain',
    'bind_pwd': 'test',
    'network_timeout': 5,
    'op_timeout': -1,}
