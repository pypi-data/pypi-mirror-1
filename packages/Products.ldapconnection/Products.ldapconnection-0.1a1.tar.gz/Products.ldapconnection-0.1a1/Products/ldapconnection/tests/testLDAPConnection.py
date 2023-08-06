#  -*- coding: utf8 -*-
"""
Test suit for LDAPConnection.
"""

__author__  = 'Ricardo Alves <rsa at eurotux dot com>'
__docformat__ = 'plaintext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest

from Products.ldapconnection import LDAPConnection
from Products.ldapconnection.exceptions import LDAPReadOnlyError
from config import LDAP_SETTINGS
import ldap
import transaction


class TestLDAPConnetion(unittest.TestCase):
    """ Test suit for LDAPConnection.
    """

    def connect(self):
        conn = LDAPConnection('example_connection', 'Example Connection', 
            **LDAP_SETTINGS)
        conn.connect()
        return conn

    def _addEntries(self, conn):
        """ Add entries to directory. """
        dn = 'ou=testentry,%s' % LDAP_SETTINGS['base_dn']
        attribute_dict = {
            'objectClass': 'organizationalUnit',
            'ou': 'testentry',
            'businessCategory': 'finnance',
        }
        try:
            conn.addEntry(dn, attribute_dict)
        except ldap.ALREADY_EXISTS:
            pass

    def _delEntries(self, conn):
        """ Delete de entries added. """
        dn = 'ou=testentry,%s' % LDAP_SETTINGS['base_dn']
        try:
            conn.deleteEntry(dn)
        except ldap.NO_SUCH_OBJECT:
            pass

    def testConnect(self):
        conn = self.connect()
        self.failUnless(conn.connected())

    def testVersion(self):
        conn = self.connect()
        self.assertEquals(
            conn.getConnection().connection.get_option(
                ldap.OPT_PROTOCOL_VERSION), ldap.VERSION3
        )

    def testAddEntries(self):
        conn = self.connect()
        self._addEntries(conn)
        dn = 'ou=testentry,%s' % LDAP_SETTINGS['base_dn']
        results = conn.search(dn, ldap.SCOPE_BASE)
        self.failUnless(results)
        self.failUnlessEqual(results[0][1]['ou'], ['testentry'])        
        self._delEntries(conn)

    def testSearchEntries(self):
        conn = self.connect()
        self._addEntries(conn)
        dn = 'ou=testentry,%s' % LDAP_SETTINGS['base_dn']
        self.failUnless(conn.search(dn, ldap.SCOPE_BASE))
        self._delEntries(conn)

    def testDelEntries(self):
        conn = self.connect()
        self._addEntries(conn)
        dn = 'ou=testentry,%s' % LDAP_SETTINGS['base_dn']
        conn.deleteEntry(dn)
        self.failUnlessEqual(conn.search(dn, ldap.SCOPE_BASE), [])

    def testModify(self):
        conn = self.connect()
        self._addEntries(conn)
        dn = 'ou=testentry,%s' % LDAP_SETTINGS['base_dn']
        attribute_dict = {
            'businessCategory': 'sports',
        }
        conn.modifyEntry(dn, attribute_dict)
        results = conn.search(dn, ldap.SCOPE_BASE)
        if results:
            self.failUnlessEqual(results[0][1]['businessCategory'], ['sports'])
        self._delEntries(conn)

    def testReadOnly(self):
        conn = self.connect()
        conn._read_only = True
        self.assertRaises(LDAPReadOnlyError, self._addEntries, conn)

    def testTransactionalBehavior(self):
        conn = self.connect()
        self._addEntries(conn)
        transaction.abort()
        dn = 'ou=testentry,%s' % LDAP_SETTINGS['base_dn']
        self.failUnlessEqual(conn.search(dn, ldap.SCOPE_BASE), [])
        


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( TestLDAPConnetion ) )
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
