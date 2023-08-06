##############################################################################
#
# Copyright (c) 2008-2010 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" test_connection_delete: Tests for the LDAPConnection delete method

$Id: test_connection_delete.py 1873 2010-01-26 11:45:11Z jens $
"""

import unittest

from dataflake.ldapconnection.tests.base import LDAPConnectionTests
from dataflake.ldapconnection.tests.dummy import DummyLDAPObjectFactory
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_ENCODED
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_UTF8

class ConnectionDeleteTests(LDAPConnectionTests):

    def test_delete_noauthentication(self):
        conn = self._makeSimple()
        conn.delete('cn=foo')
        connection = conn._getConnection()
        self.assertEqual(connection.binduid, u'')
        self.assertEqual(connection.bindpwd, '')

    def test_delete_authentication(self):
        conn = self._makeSimple()
        bind_dn_apiencoded = 'cn=%s,dc=localhost' % ISO_8859_1_ENCODED
        bind_dn_serverencoded = 'cn=%s,dc=localhost' % ISO_8859_1_UTF8
        conn.delete('cn=foo', bind_dn=bind_dn_apiencoded, bind_pwd='foo')
        connection = conn._getConnection()
        self.assertEqual(connection.binduid, bind_dn_serverencoded)
        self.assertEqual(connection.bindpwd, 'foo')

    def test_delete(self):
        conn = self._makeSimple()
        conn.delete('cn=foo')
        connection = conn._getConnection()
        self.failUnless(connection.deleted)
        self.assertEqual(connection.deleted_dn, 'cn=foo')

    def test_delete_readonly(self):
        conn = self._makeOne('host', 636, 'ldap', self._factory, read_only=True)
        self.assertRaises(RuntimeError, conn.delete, 'cn=foo')

    def test_delete_referral(self):
        of = DummyLDAPObjectFactory('conn_string')
        import ldap
        of.del_exc = ( ldap.REFERRAL
                     , {'info':'please go to ldap://otherhost:1389'}
                     )
        def factory(conn_string, who='', cred=''):
            of.conn_string = conn_string
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.delete('cn=foo')
        self.assertEqual(of.conn_string, 'ldap://otherhost:1389')
        self.failUnless(of.deleted)
        self.assertEqual(of.deleted_dn, 'cn=foo')


def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])

