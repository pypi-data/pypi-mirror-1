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
Transaction resource manager to perform transaction-aware operations in 
LDAP connection.
"""

__author__  = 'Ricardo Alves <rsa at eurotux dot com>'
__docformat__ = 'plaintext'

from Shared.DC.ZRDB.TM import TM
from ZODB.PersistentMapping import PersistentMapping
import ldap
from log import log

class Connection(TM):
    """ Manages the LDAP connection transaction.
    """

    def __init__(self, url, bind_dn, bind_pwd, network_timeout, op_timeout):
        self._changes = []
        self.url = url
        self.bind_dn = bind_dn
        self.bind_pwd = bind_pwd
        self.network_timeout = network_timeout
        self.op_timeout = op_timeout
        self.connect()

    def connect(self):
        """ Establish a connection to LDAP server.
        """
        log('Connecting to %s' % repr(self.url))

        self.connection = ldap.initialize(self.url)
        self.connection.set_option(ldap.OPT_PROTOCOL_VERSION,
            ldap.VERSION3)

        if self.network_timeout > 0:
            self.connection.set_option(ldap.OPT_NETWORK_TIMEOUT,
                self.network_timeout)
        if self.op_timeout > 0:
            self.connection.timeout = self.op_timeout

    def bind(self, retry=True):
        try:
            self.connection.simple_bind_s(self.bind_dn, self.bind_pwd)
        except ldap.SERVER_DOWN:
            if retry:
                self.connect()
                # retry only once!
                self.bind(retry=False)
            else:
                raise

    def add(self, dn, modlist):
        self._register()
        self.connection.add_s(dn, modlist)
        self._changes.append(('add', (dn, modlist)))

    def delete(self, dn):
        self._register()
        results = self.connection.search_s(dn, ldap.SCOPE_BASE)
        if results:
            attribute_values = results[0][1]

        self.connection.delete_s(dn)
        self._changes.append(('delete', (dn, attribute_values)))


    def modify(self, dn, modlist):
        self._register()
        results = self.connection.search_s(dn, scope=ldap.SCOPE_BASE,
            attrlist=[a[1] for a in modlist])
        if results:
            attribute_values = results[0][1]

        self.connection.modify_s(dn, modlist)
        self._changes.append(('modify', (dn, modlist, attribute_values)))


    def rename(self, dn, newrdn):
        self._register()
        self.connection.rename_s(dn, newrdn)
        self._changes.append(('rename', (dn, newrdn)))

    def search(self, dn, scope, filterstr='', attrlist=None):
        return self.connection.search_s(dn, scope, filterstr=filterstr,
            attrlist=attrlist)

    def _begin(self):
        log('transaction begin')
        self._changes = []

    def _finish(self):
        log('transaction finish')

    def _abort(self):
        log('transaction abort')
        # cleanup changes history.
        self._undoChanges(self._changes)

    def _undoChanges(self, changes):
        """ Try to undo the changes, since the transaction is being 
        aborted.
        """
        log('Undo changes')
        changes.reverse()
        for op, values in changes:

            if op == 'add':
                try:
                    self.connection.delete_s(values[0])
                except ldap.LDAPError:
                    log('Failled to abort add operation: %s' % values[0])

            elif op == 'modify':
                modlist = values[1]
                attribute_values = values[2]
                revert_modlist = []
                # create a revert modlist
                for op, key, value in modlist:
                    if op == ldap.MOD_DELETE:
                        revert_modlist.append((ldap.MOD_ADD, key,
                            attribute_values[key]))
                    elif op == ldap.MOD_ADD:
                        revert_modlist.append((ldap.MOD_DELETE, key, None))
                    elif op == ldap.MOD_REPLACE:
                        revert_modlist.append((ldap.MOD_REPLACE, key,
                            attribute_values[key]))
                # modify to revert changes.
                try:
                    self.connection.modify_s(values[0], revert_modlist)
                except ldap.LDAPError:
                    log('Failled to abort modify operation: %s - %s' % \
                        (values[0], repr(revert_modlist)))

            elif op == 'delete':
                modlist = ldap.modlist.addModlist(values[1])
                try:
                    self.connection.add_s(values[0], modlist)
                except ldap.LDAPError:
                    log('Failled to abort delete operation: %s - %s' % \
                        (values[0], repr(modlist)))

            elif op == 'rename':
                old_rdn = ','.join(values[0].split(',')[:1])
                base_dn = ','.join(values[0].split(',')[1:])
                dn = '%s,%s' % (values[1], base_dn)
                try:
                    self.connection.rename_s(dn, old_rdn)
                except ldap.LDAPError:
                    log('Failled to abort rename operation: %s - %s' % \
                        (dn, old_rdn))

