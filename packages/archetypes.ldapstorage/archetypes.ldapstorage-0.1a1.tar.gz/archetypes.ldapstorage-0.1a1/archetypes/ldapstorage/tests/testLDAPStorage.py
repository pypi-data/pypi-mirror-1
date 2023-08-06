#  -*- coding: utf8 -*-
"""
Test suit for LDAPStorage.
"""

__author__  = 'Ricardo Alves <rsa at eurotux dot com>'
__docformat__ = 'plaintext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from archetypes.ldapstorage import config as product_config
product_config.DEBUG_MODE = 1

import config as tests_config

import transaction
from Globals import InitializeClass, package_home
from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.CMFPlone.utils import base_hasattr
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.ldapconnection import LDAPConnection
import ldap
import os.path

ZopeTestCase.installProduct('ldapconnection')

@onsetup
def setup_package():
    import archetypes.ldapstorage
    zcml.load_config('configure.zcml', archetypes.ldapstorage)
    ZopeTestCase.installPackage('archetypes.ldapstorage')

setup_package()

PloneTestCase.setupPloneSite(extension_profiles=['archetypes.ldapstorage:example'])

PACKAGE_HOME = package_home(globals())

class TestLDAPStorage(PloneTestCase.PloneTestCase):
    """ Test suit for LDAPStorage.
    """

    def afterSetUp(self):
        self.setupConnection()

    def setupConnection(self):
        """ Create and configure an LDAP connection.
        """
        # create new connection
        self.portal.manage_addProduct['ldapconnection'].\
            manage_addLDAPConnection('ldap_connection',
                'Test LDAP Connection', **tests_config.LDAP_SETTINGS)
        # set connection for portal types
        self.portal.archetype_tool.setConnForPortalTypes(
            ['ExampleContent', 'ExampleContent2'], 'ldap_connection')

    def test_contentCreation(self):
        self.folder.invokeFactory(id='content1', type_name='ExampleContent')
        self.failUnless(base_hasattr(self.folder, 'content1'))

        # search LDAP for created entry
        conn = self.portal.ldap_connection
        results = conn.search('uid=content1,%s' % \
            tests_config.LDAP_SETTINGS['base_dn'])
        self.failUnless(results)

        self.folder.manage_delObjects(['content1'])

    def test_variableRDN(self):
        self.folder.invokeFactory(id='contentb', type_name='ExampleContent2')
        self.failUnless(base_hasattr(self.folder, 'contentb'))
        obj = self.folder.contentb

        # test RDN value
        rdn_value = obj._ldap_rdn_value
        self.failUnlessEqual(rdn_value.encode(obj.getCharset()), obj.getName())

        # search LDAP for created entry
        conn = self.portal.ldap_connection
        results = conn.search('cn=%s,%s' % (rdn_value, 
            tests_config.LDAP_SETTINGS['base_dn']))
        self.failUnless(results)

        # compare rdn value
        self.failUnlessEqual(rdn_value, results[0][1]['cn'][0])

        # test edition
        obj.edit(name='Césare', surname='Your surname')

        self.failUnlessEqual('Césare', obj.getName())
        self.failUnlessEqual('Your surname', obj.getSurname())

        # test RDN value again
        rdn_value = obj._ldap_rdn_value
        self.failUnlessEqual(rdn_value.encode(obj.getCharset()), obj.getName())

        results = conn.search('cn=%s,%s' % (rdn_value,
            tests_config.LDAP_SETTINGS['base_dn']))

        # compare rdn value
        self.failUnlessEqual(rdn_value.encode(obj.getCharset()), 
            results[0][1]['cn'][0])

        self.folder.manage_delObjects(['contentb'])

    #def test_objectClassViolation(self):
    #    pass

    #def test_invalidRDN(self):
    #    pass

    def test_contentEdit(self):
        self.folder.invokeFactory(id='content1', type_name='ExampleContent')
        obj = getattr(self.folder, 'content1')

        # read image file
        photo_file = open(os.path.join(PACKAGE_HOME, 'input', 'photo.png'), 
            'rb')
        obj.edit(address='15th Avenue, 50', lastname='New Last Name', 
            photo=photo_file.read())

        # test values through accessors
        self.failUnlessEqual(obj.getAddress(), '15th Avenue, 50')
        self.failUnlessEqual(obj.getLastname(), 'New Last Name')

        # test values in LDAP
        conn = self.portal.ldap_connection
        dn = 'uid=content1,%s' % tests_config.LDAP_SETTINGS['base_dn']
        results = conn.search(dn, ldap.SCOPE_BASE)
        self.failUnlessEqual(results[0][1]['homePostalAddress'][0], 
            '15th Avenue, 50')
        self.failUnlessEqual(results[0][1]['sn'][0], 'New Last Name')

        # cleanup
        self.folder.manage_delObjects(['content1'])

        # test if was deleted in LDAP
        self.assertEqual(conn.search(dn, ldap.SCOPE_BASE), [])

    def test_contentMove(self):
        self.folder.invokeFactory(id='content1', type_name='ExampleContent')
        obj = getattr(self.folder, 'content1')

        # pass flag to the transaction savepoint method to indicate
        # that databases without savepoint support should be tolerated.
        transaction.savepoint(1)

        self.folder.manage_renameObject('content1', 'content2')

        old_dn = 'uid=content1,%s' % tests_config.LDAP_SETTINGS['base_dn']
        new_dn = 'uid=content2,%s' % tests_config.LDAP_SETTINGS['base_dn']

        conn = self.portal.ldap_connection
        self.assertEqual(conn.search(old_dn, ldap.SCOPE_BASE), [])

        results = conn.search(new_dn, ldap.SCOPE_BASE)
        self.failUnless(results)

        obj = getattr(self.folder, 'content2')
        self.assertEqual(obj.getLastname(), 'Test lastname')
        self.assertEqual(results[0][1]['sn'][0], 'Test lastname')

        # cleanup
        self.folder.manage_delObjects(['content2'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLDAPStorage))
    return suite

if __name__ == '__main__':
    framework()
