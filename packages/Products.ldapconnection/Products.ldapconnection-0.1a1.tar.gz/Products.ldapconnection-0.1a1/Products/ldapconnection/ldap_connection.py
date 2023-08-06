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
Class to be used in connections to LDAP servers.
"""

__author__  = 'Ricardo Alves <rsa at eurotux dot com>'
__docformat__ = 'plaintext'


from Globals import Persistent, InitializeClass
from AccessControl.Role import RoleManager
from OFS import SimpleItem
from Acquisition import Implicit, aq_base
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import ldap
import ldap.modlist
from DateTime import DateTime
from exceptions import LDAPReadOnlyError
from tm import Connection
from lib.Shared import getResource

import logging
from log import log

DEFAULT_NETWORK_TIMEOUT = 5
DEFAULT_OP_TIMEOUT = -1

class LDAPConnection(Persistent, RoleManager, SimpleItem.Item, Implicit):
    """ LDAP connection manager.
    """

    meta_type = 'LDAP Connection'

    # zmi tabs
    manage_options = (
        {'label': 'Status', 'action': 'manage_main'},
        {'label': 'Settings', 'action': 'manage_properties'},
        {'label': 'Search', 'action': 'manage_search'},
        ) + RoleManager.manage_options + SimpleItem.Item.manage_options


    manage_main = PageTemplateFile('www/connectionStatus', globals())
    manage_properties = PageTemplateFile('www/connectionEdit', globals())
    manage_search = PageTemplateFile('www/connectionSearch.zpt', globals())

    # TODO: find a better way to add this connection to the list in
    # archetype_tool
    _isAnSQLConnection = 1

    def __init__(self, id, title, url='', base_dn='', scope='', bind_dn='',
        bind_pwd='', network_timeout=5, op_timeout=-1, read_only=False):
        self.id = id
        self.title = title
        self._url = url
        self._base_dn = base_dn
        self._bind_dn = bind_dn
        self._bind_pwd = bind_pwd
        self._scope = ldap.SCOPE_SUBTREE
        self._network_timeout = network_timeout
        self._op_timeout = op_timeout
        self._read_only = bool(read_only)
        # FIXME: configurable encoding
        self._encoding = 'utf-8'

        self.connect()

    def Title(self):
        """ Return title value
        """
        return self.title

    def getProperty(self, propid, default=''):
        """ Returns property value.
        """
        return getattr(aq_base(self), propid, default)

    def encodeValue(self, value):
        """ Encode list of values in configured encoding.
        """
        if type(value) == type([]):
            encoded_value = []
            for v in value:
                if type(v) == type(u''):
                    encoded_value.append(v.encode(self._encoding))
                elif type(v) == type(''):
                    encoded_value.append(v)
            return encoded_value
        elif type(value) == type(u''):
            return value.encode(self._encoding)
        else:
            return value

    def getConnection(self):
        """ Returns the connection object.
        """
        connection = getResource(
            '_connection_', 
            Connection,
            (self._url, self._bind_dn, self._bind_pwd, 
                self._network_timeout, self._op_timeout,),
        )
        return connection


    def connect(self):
        """ Establish a connection.
        """

        # initialize connection
        # TODO: check url first

        connection = self.getConnection()

        self.bind()

        return connection

    def connected(self):
        """ Tests if the connection is open.
        """
        connection = getResource('_connection_', str, ())
        if type(connection) == type(''):
            return False
        return True

    def bind(self):
        """ Perform bind in LDAP server.
        """
        self.getConnection().bind()

    def addEntry(self, dn, attribute_dict):
        """ Adds new entry.
        """

        if self._read_only:
            msg = ("LDAP connection is in read only mode. Can't perform "
                "write operations.")
            log(msg, severity=logging.ERROR)
            raise LDAPReadOnlyError, msg

        log('Adding new entry %s' % repr(attribute_dict))

        conn = self.connect()

        # encode values
        for k, v in attribute_dict.items():
            attribute_dict[k] = self.encodeValue(v)

        modlist = ldap.modlist.addModlist(attribute_dict)
        conn.add(self.encodeValue(dn), modlist)


    def modifyEntry(self, dn, attribute_dict):
        """ Modify an existing entry.
        """

        if self._read_only:
            msg = ("LDAP connection is in read only mode. Can't perform "
                "write operations.")
            log(msg, severity=logging.ERROR)
            raise LDAPReadOnlyError, msg

        log('Modifying entry %s - %s' % (dn, repr(attribute_dict)))

        conn = self.connect()

        result = self.search(dn=dn, scope=ldap.SCOPE_BASE)
        if not result:
            raise ldap.NO_SUCH_OBJECT, dn

        # encode values
        for k, v in attribute_dict.items():
            attribute_dict[k] = self.encodeValue(v)

        entry_dn, entry = result[0]

        modlist = []
        for key, values in attribute_dict.items():
            if entry.has_key(key):
                if values in ([], ''):
                    modlist.append((ldap.MOD_DELETE, key, None))
                elif entry[key] != values:
                    modlist.append((ldap.MOD_REPLACE, key, values))
            else:
                if values in ([], ''):
                    continue
                else:
                    modlist.append((ldap.MOD_ADD, key, values))

        if not modlist:
            return

        conn.modify(self.encodeValue(dn), modlist)

    def deleteEntry(self, dn):
        """ Delete an entry from directory.
        """

        if self._read_only:
            msg = ("LDAP connection is in read only mode. Can't perform "
                "write operations.")
            log(msg, severity=logging.ERROR)
            raise LDAPReadOnlyError, msg

        log('Deleting entry %s' % dn)

        conn = self.connect()
        conn.delete(self.encodeValue(dn))

    def modifyDN(self, dn, new_rdn):
        """ Perform the modify RDN operation.
        """

        conn = self.connect()

        log('Modifying DN: %s -> %s' % (dn, new_rdn))
        conn.rename(self.encodeValue(dn), self.encodeValue(new_rdn))
        

    def search(self, dn=None, scope=None, filter='objectClass=*',
        attrlist=None):
        """ Performs a search in directory.
        """
        conn = self.connect()

        if dn is None:
            dn = self._base_dn

        if scope is None:
            scope = self._scope

        try:
            return conn.search(self.encodeValue(dn), scope, filterstr=filter,
                attrlist=attrlist)
        except ldap.NO_SUCH_OBJECT:
            return []

    def manage_openConnection(self, REQUEST=None):
        """ Open connection.
        """
        self.connect()
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)

    def manage_editConnection(self, REQUEST=None):
        """ Edit connection properties.
        """
        if REQUEST is not None:
            self.title = REQUEST.get('title', self.title)
            self._url = REQUEST.get('url', self._url)
            self._base_dn = REQUEST.get('base_dn', self._base_dn)
            self._scope = int(REQUEST.get('scope', self._scope))
            self._bind_dn = REQUEST.get('bind_dn', self._bind_dn)
            self._bind_pwd = REQUEST.get('bind_pwd', self._bind_pwd)
            self._read_only = bool(REQUEST.get('read_only', False))
            self._network_timeout = \
                int(REQUEST.get('network_timeout', self._network_timeout))
            self._op_timeout = int(REQUEST.get('op_timeout', self._op_timeout))
            
            self.connect()

        if REQUEST is not None:
            return self.manage_main(self, REQUEST)
    
    def manage_searchConnection(self, filter, REQUEST=None):
        """ Edit connection properties.
        """
        results = self.search(filter=filter)
        if REQUEST is not None:
            return self.manage_search(self, results=results, filter=filter,
                REQUEST=REQUEST)
        return results


def manage_addLDAPConnection(self, id, title, url='', base_dn='',
    scope=ldap.SCOPE_SUBTREE, bind_dn= '', bind_pwd='', read_only=False,
    network_timeout=DEFAULT_NETWORK_TIMEOUT, op_timeout=DEFAULT_OP_TIMEOUT,
    REQUEST=None):
    """ Add a new LDAP connnection.
    """
    ldap_conn = LDAPConnection(id, title,
        url = url,
        base_dn = base_dn,
        scope = scope,
        bind_dn = bind_dn,
        bind_pwd = bind_pwd,
        read_only = bool(read_only),
        network_timeout = int(network_timeout or DEFAULT_NETWORK_TIMEOUT),
        op_timeout = int(op_timeout or DEFAULT_OP_TIMEOUT),
    )
    self._setObject(id, ldap_conn)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


manage_addLDAPConnectionForm = \
    PageTemplateFile('www/addLDAPConnection', globals())

InitializeClass(LDAPConnection)
