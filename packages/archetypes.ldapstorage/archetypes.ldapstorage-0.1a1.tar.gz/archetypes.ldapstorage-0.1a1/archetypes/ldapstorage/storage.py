#  -*- coding: utf8 -*-
#  Copyright (c) 2007 Eurotux Informática S.A.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
An Archetypes storage that stores field values in LDAP directory.
"""

__author__  = 'Ricardo Alves <rsa at eurotux dot com>'
__docformat__ = 'plaintext'

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.config import TOOL_NAME
from Products.Archetypes.Storage import StorageLayer
from Products.Archetypes.Registry import registerStorage
from Products.Archetypes.interfaces.storage import ISQLStorage
from Products.Archetypes.interfaces.layer import ILayer
from Products.Archetypes.public import AttributeStorage, BaseUnit
from Products.Archetypes.utils import shasattr
from Products.Archetypes.Field import File, Image
from exceptions import MissingRDNError, InvalidRDNError
from DateTime import DateTime
from random import random
import ldap
from log import log

_marker = ''


class LDAPStorage(StorageLayer, AttributeStorage):
    """ An Archetypes storage that stores field values in LDAP directory.
    """

    # FIXME: implementing ISQLStorage (marker interface from Archetypes) to
    # allow the mapping with content types in archetype_tool.
    __implements__ = (ISQLStorage, ILayer)

    def __init__(self, rdn_attr, rdn_map, attr, default_attrs={},
        required_attrs=[]):
        # LDAP rdn attribute
        self._rdn_attr = rdn_attr
        # AT field mapped to rdn. This field shall not me stored with 
        # this storage.
        self._rdn_map = rdn_map
        # Attribute to store
        self._attr = attr
        # The values in default_attrs will be used in initialization
        self._default_attrs = default_attrs
        # Required attributes in the LDAP schema used.
        self._required_attrs = required_attrs

    def getDN(self, instance):
        """ Returns the dn for a specific instance.
        """
        connection = self._getConnection(instance)
        return '%s=%s,%s' % (self._rdn_attr, 
            self.getRDN(instance), connection._base_dn)

    def getRDN(self, instance):
        """ Return the value of rdn for a specific instance.
        Uses the key defined in '_rdn_map' to get the value.
        The key '_rdn_map' may be a callable method, an attribute or an 
        AT field.
        """
        if not self.is_initialized(instance):
            # not initialized yet. if the RDN is an AT Field, we need to get
            # a value to use during initialization.
            f = instance.getField(self._rdn_map)
            if f and f.getStorage().__class__ == self.__class__:
                # it is an AT field and uses LDAP storage.
                if f.getStorage()._attr != self._rdn_attr:
                    # check definition to avoid bugs that are really 
                    # hard to track.
                    raise InvalidRDNError, ("Invalid RDN definition: "
                        "'rdn_attr' must be the same as 'attr' for "
                        "an LDAP-stored RDN map.")
                value  = self.getDefaultValue(instance, self._rdn_map)
                if value:
                    instance._ldap_rdn_value = value
                    instance._p_changed = 1
                    return value

        if hasattr(instance.aq_base, self._rdn_map):
            method = getattr(instance, self._rdn_map)
            if callable(method):
                return method()
            else:
                return method
        else:
            f = instance.getField(self._rdn_map)
            if f and f.getStorage().__class__ == self.__class__:
                if shasattr(instance, '_ldap_rdn_value'):
                    return instance._ldap_rdn_value
        raise MissingRDNError, 'Unable to obtain RDN.'

    def prepare_value(self, instance, name, value):
        """ Prepare value to write in LDAP.
        """
        if not value:
            return ''

        def decode_value(value):
            if type(value) != type(u''):
                try:
                    # FIXME: should we care?
                    return value.decode(instance.getCharset())
                except UnicodeDecodeError:
                    # FIXME: should we let it go?
                    pass
            return value

        if isinstance(value, BaseUnit):
            value = [value.getRaw()]

        if type(value) in (File, Image):
            value = value.data

        if type(value) not in (type([]), type(())):
            value = [value]

        value = [decode_value(v) for v in value]

        field = instance.getField(name)
        f_storage = field.getStorage()

        if self._default_attrs.has_key(f_storage._attr):
            default_value = self._default_attrs[f_storage._attr]
            if type(default_value) == type(''):
                # default value must be an attribute (maybe callable) in
                # instance
                if shasattr(aq_base(instance), default_value):
                    method = getattr(instance, default_value)
                    if callable(method):
                        default_value = [method()]
                    else:
                        default_value = [method]

            value = default_value + \
                [v for v in value if v not in default_value]

        return value

    def getDefaultValue(self, instance, name):
        """ Returns the default value for a specific field.
        """
        field = instance.getField(name)

        try:
            # Try to get a value from the request
            f_value = instance.REQUEST.get(field.getName(),
                field.getDefault(instance))
        except AttributeError:
            f_value = field.getDefault(instance)

        if (not f_value) and (field.getStorage()._attr in \
            self._required_attrs or name == self._rdn_map):
            # this is a required attribute in LDAP schema, or the field
            # mapped to RDN attribute. Use a temporary/random value. 
            # FIXME: this only works for text fields.
            # TODO: document this feature!
            if self._rdn_map == name and shasattr(instance, '_ldap_rdn_value'):
                # If the rdn was already calculated return the same value.
                return instance._ldap_rdn_value
            now=DateTime()
            time = '%s.%s' % \
                (now.strftime('%Y-%m-%d'), str(now.millis())[7:])
            rand = str(random())[2:6]
            f_value = name + time + rand
        return f_value


    def getDefaultValues(self, instance):
        """ Returns a dict with default values for LDAP attributes to use in
        layer initialization.
        """
        ldap_fields = [f for f in instance.Schema().fields() if \
            f.getStorage().__class__ == self.__class__]

        attribute_dict = {}
        for field in ldap_fields:
            f_storage = field.getStorage()
            f_value = self.getDefaultValue(instance, field.getName())
            attribute_dict[f_storage._attr] = \
                self.prepare_value(instance, field.getName(), f_value)

        for key in self._default_attrs.keys():
            if key not in attribute_dict.keys():
                attribute_dict[key] = self._default_attrs[key]
            # TODO: should we concatenate default_attrs and default_values
            # if already defined?

        if not attribute_dict.has_key(self._rdn_attr):
            # add rdn if not there
            attribute_dict[self._rdn_attr] = self.getRDN(instance)

        return attribute_dict


    def is_initialized(self, instance):
        """ Test if the storage layer is already initialized in instance.
        """
        try:
            return self.getName() in instance._initializedStorage
        except AttributeError:
            return False

    def is_cleaned(self, instance):
        """ Test if the storage layer is cleaned in instance.
        """
        try:
            return self.getName() in instance._cleanedStorage
        except AttributeError:
            return False

    def entry_exists(self, instance, dn=None):
        """ Test if the entry already exists.
        """
        if dn is None:
            dn = self.getDN(instance)
        connection = self._getConnection(instance)
        return bool(connection.search(dn))


    def initializeInstance(self, instance, item=None, container=None,
        swallow_exceptions=True):
        """ Implementation of 'initializeInstance' for StorageLayer.
        """

        is_new_object = not getattr(instance, '_v_old_rdn', None)
        
        if instance.isTemporary():
            # It is a temporary object from portal factory. Don't use LDAP
            # yet.
            log('Is a temporary object from portal factory. Dont use LDAP')
            return

        if self.is_initialized(instance) or \
            getattr(instance, '_at_is_fake_instance', _marker):
            # Already intialized or fake instance
            log('Already intialized or fake instance. not initializing')
            return

        dn = self.getDN(instance)

        if self.entry_exists(instance, dn) and is_new_object:
            # Entry already exists.
            log('Entry already exists.  not initializing')
            return
            
        log('initializing %s' % dn)

        # construct attribute_list with current values of fields using 
        # this storage.
        attribute_list = self.getDefaultValues(instance)
        log('Adding with default values: ' + repr(attribute_list))

        connection = self._getConnection(instance)

        if is_new_object:
            # This is really a new object.
            try:
                # create new entry
                connection.addEntry(dn, attribute_list)
            except ldap.OBJECT_CLASS_VIOLATION, e:
                # couldn't initialize (add) due to schema violation.
                log("couldn't initialize due to schema violation: \n %s" % e)
                if not swallow_exceptions:
                    raise e
                # initialization failed but ignore it.
                # initialization will be called again by field mutators, but
                # without swallow_exceptions.
                return
        else:
            # This object was moved. Perform rename operation if RDN is
            # different.
            old_rdn_value = instance._v_old_rdn
            new_rdn_value = self.getRDN(instance)
            if old_rdn_value != new_rdn_value:
                # rdn changed. perform rename operation
                old_dn = u'%s=%s,%s' % (self._rdn_attr, old_rdn_value,
                    connection._base_dn)
                new_rdn = u'%s=%s' % (self._rdn_attr, new_rdn_value)
                connection.modifyDN(old_dn, new_rdn)

        # mark initialized
        try:
            instance._initializedStorage += (self.getName(),)
        except AttributeError:
            instance._initializedStorage = (self.getName(),)

        log('initialized %s' % dn)

        try:
            del instance._cleanedStorage
        except AttributeError:
            pass


    def _getConnection(self, instance):
        """ Return the connection object to be used by this storage.
        """
        at_tool = getToolByName(instance, TOOL_NAME)
        connection_id = at_tool.getConnFor(instance)
        return getattr(instance, connection_id) 


    def set(self, name, instance, value, **kwargs):
        """ Mutator for field value. What may happen:

        * there is no value: do nothing;

        * this field is the rdn map:

            - the instance is not initialized: store the value in
            self._ldap_rdn_value

            - the instance is initialized: store the value in
            self._ldap_rdn_value and in LDAP

            - if the value changes: perform rename operation in LDAP;

        * this is not a field in AT schema (probably an image scale): use
        AttributeStorage to store the value.
            
        """

        log('ldapstorage: mutator for %s' % name)

        if not value:
            return

        connection = self._getConnection(instance)

        if name == self._rdn_map:
            # This field is used to map the LDAP RDN attribute.
            # The value must also be stored in the ZODB.
            # If this value changes, we need to perform a rename in
            # LDAP
            log('ldapstorage: %s is rdn_map, store value' % name)
            if instance._ldap_rdn_value != value:
                # RDN changed. need to perform a rename
                log('ldapstorage: RDN changed, renaming')
                old_dn = u'%s=%s,%s' % (self._rdn_attr,
                    instance._ldap_rdn_value, connection._base_dn)
                new_rdn = u'%s=%s' % (self._rdn_attr, value)
                results = connection.search(old_dn)
                log('ldapstorage: ' + repr(results))
                connection.modifyDN(old_dn, new_rdn)
            # store value in the ZODB
            instance._ldap_rdn_value = value
            instance._p_changed = 1
        
        if not self.is_initialized(instance):
            # not initialized. try to initialize, but without
            # swallow_exceptions.
            log('not initialized. try to initialize')
            self.initializeInstance(instance, swallow_exceptions=False)

        # It is initialized. Do the storage work.

        if not instance.getField(name):
            # Not a field in AT schema. It is probably an image scale.
            # Use AttributeStorage instead.
            return AttributeStorage.set(self, name, instance, value, **kwargs)

        dn = self.getDN(instance)

        value = self.prepare_value(instance, name, value)

        connection.modifyEntry(dn, {self._attr: value})


    def unset(self, name, instance, **kwargs):
        if not instance.getField(name):
            # Not a field in AT schema. It is probably an image scale.
            # Use AttributeStorage instead.
            return AttributeStorage.unset(self, name, instance, **kwargs)

        connection = self._getConnection(instance)
        dn = self.getDN(instance)

        connection.modifyEntry(dn, {self._attr: []})

    def get(self, name, instance, **kwargs):
        """ Accessor for field value. What may happen:

        * instance is not initialized: there is nothing to get;

        * it fails to retrieve the DN:

            - if this field is the RDN map, return the rdn value. else
            raise exception

        * we have a dn: get the value (a list):

            - check if this field is multivalued, or lines, to return a list
              or only the first element.
            
        """

        if name == self._rdn_map:
            # This field is used to map the LDAP RDN attribute.
            # Return the value stored in the ZODB.
            if shasattr(instance, '_ldap_rdn_value'):
                return instance._ldap_rdn_value

        if not self.is_initialized(instance):
            log("not initialized: don't get, but return default value")
            return instance.getField(name).getDefault(instance)

        connection = self._getConnection(instance)
        dn = self.getDN(instance)

        log('search dn: ' + dn)
        results = connection.search(dn, ldap.SCOPE_BASE, attrlist=[self._attr])
        log('search results: ' + repr(results))

        if results:
            log('return: ' + repr(results[0][1].get(self._attr, _marker)))
            value = results[0][1].get(self._attr, _marker)
        else:
            value = _marker

        # handle list and non-list values
        field = instance.getField(name)
        if value and type(value) == type([]):
            if field.type == 'lines' or field.multiValued:
                return value
            else:
                # TODO: we should log a warning message when a 
                # single-valued AT field has multiple values in LDAP
                return value[0]

        return value


    def initializeField(self, instance, field):
        pass


    def cleanupField(self, instance, field):
        pass


    def cleanupInstance(self, instance, item=None, container=None):
        """ Cleanup instance when deleted.
        """
        if self.is_cleaned(instance) or getattr(instance.aq_base,
            '_at_is_fake_instance', None):
            # Already cleaned or fake instance.
            log('Already cleaned or fake instance. dont clean')
            return

        dn = self.getDN(instance)

        log('Cleaning up instance %s' % dn)

        if getattr(instance, '_v_cp_refs', None):
            # Object is beeing moved. Do not remove the entry and mark the
            # old rdn.
            instance._v_old_rdn = self.getRDN(instance)
        else:
            # object is really going away. Remove entry from LDAP.
            conn = self._getConnection(instance)
            conn.deleteEntry(dn)
            

        # marked cleaned
        try:
            instance._cleanedStorage += (self.getName(),)
        except AttributeError:
            instance._cleanedStorage = (self.getName(),)

        log('Cleaned instance %s' % dn)

        try:
            del instance._initializedStorage
        except AttributeError:
            pass


registerStorage(LDAPStorage)
