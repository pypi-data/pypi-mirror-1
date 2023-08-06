##############################################################################
#
# Copyright (c) 2008 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" test_connection: Tests for the LDAPConnection class

$Id: test_connection.py 1485 2008-06-04 16:08:38Z jens $
"""

import unittest

from dataflake.ldapconnection.tests.dummy import DummyLDAPObjectFactory

class ConnectionTests(unittest.TestCase):
    def _getTargetClass(self):
        from dataflake.ldapconnection.connection import LDAPConnection
        return LDAPConnection

    def _makeOne(self, *args, **kw):
        conn = self._getTargetClass()(*args, **kw)
        return conn

    def _makeSimple(self):
        conn = self._makeOne('host', 636, 'ldap', DummyLDAPObjectFactory)
        return conn

    def test_ctor(self):
        conn = self._makeSimple()
        self.assertEqual(conn.server['host'], 'host')
        self.assertEqual(conn.server['port'], 636)
        self.assertEqual(conn.server['protocol'], 'ldap')
        self.assertEqual(conn.server['conn_timeout'], -1)
        self.assertEqual(conn.server['op_timeout'], -1)

    def test_connect_initial_noargs(self):
        conn = self._makeSimple()
        conn = conn.connect()
        self.assertEqual(conn.binduid, '')
        self.assertEqual(conn.bindpwd, '')
        self.assertEqual(conn.searched, True)

    def test_connect_initial_bind_dn_not_None(self):
        conn = self._makeSimple()
        conn = conn.connect('foo', '')
        self.assertEqual(conn.binduid, 'foo')
        self.assertEqual(conn.bindpwd, '')
        self.assertEqual(conn.searched, True)

    def test_connect_initial_bindpwd_not_None(self):
        conn = self._makeSimple()
        conn = conn.connect(None, 'pass')
        self.assertEqual(conn.binduid, '')
        self.assertEqual(conn.bindpwd, 'pass')
        self.assertEqual(conn.searched, True)

    def test_connect_non_initial(self):
        conn = self._makeSimple()
        conn.conn = DummyLDAPObjectFactory('conn_string')
        conn = conn.connect(None, 'pass')
        self.assertEqual(conn.conn_string, 'conn_string')

    def test_search_simple(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {'a': 'a', 'dn': 'dn'})

    def test_search_bad_results(self):
        # Make sure the resultset omits "useless" entries that may be
        # emitted by some servers, notable Microsoft ActiveDirectory.
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'})
                 , ('dn2',['thisvalueisuseless']) 
                 , ('dn3','anotheruselessvalue')
                 , ('dn4', ('morebadstuff',))
                 ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {'a': 'a', 'dn': 'dn'})

    def test_search_partial_results(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.partial = (None, [('dn', {'a':'a'})])
        import ldap
        of.search_exc = (ldap.PARTIAL_RESULTS, '')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {'a': 'a', 'dn': 'dn'})

    def test_search_referral(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        import ldap
        of.search_exc = ( ldap.REFERRAL
                        , {'info':'please go to ldap://otherhost:1389'}
                        )
        def factory(conn_string):
            of.conn_string = conn_string
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
        self.assertEqual(of.conn_string, 'ldap://otherhost:1389')

    def test_search_binaryattribute(self):
        # A binary value will remain untouched, no transformation 
        # to and from UTF-8 will happen.
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'objectGUID':u'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {'objectGUID': u'a', 'dn': 'dn'})

    def test_insert(self):
        attributes = { 'cn' : 'jens'
                     , 'multivaluestring' : 'val1;val2;val3'
                     , 'multivaluelist' : ['val1', 'val2']
                     }
        of = DummyLDAPObjectFactory('conn_string')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.insert('dc=localhost', 'cn=jens', attrs=attributes)
        self.failUnless(of.added)
        self.assertEqual(len(of.added_values.keys()), 1)
        dn, values = of.added_values.items()[0]
        self.assertEqual(dn, 'cn=jens' + ',' + 'dc=localhost')
        self.assertEqual(values['cn'], ['jens'])
        self.assertEqual(values['multivaluestring'], ['val1','val2','val3'])
        self.assertEqual(values['multivaluelist'], ['val1','val2'])

    def test_insert_readonly(self):
        of = DummyLDAPObjectFactory('conn_string')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory, read_only=True)
        self.assertRaises(RuntimeError, conn.insert, 'dc=localhost', 'cn=jens')

    def test_insert_referral(self):
        of = DummyLDAPObjectFactory('conn_string')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        import ldap
        of.add_exc = ( ldap.REFERRAL
                     , {'info':'please go to ldap://otherhost:1389'}
                     )
        def factory(conn_string):
            of.conn_string = conn_string
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.insert('dc=localhost', 'cn=jens', attrs={'cn':['jens']})
        self.assertEqual(of.conn_string, 'ldap://otherhost:1389')
        self.failUnless(of.added)
        self.assertEqual(len(of.added_values.keys()), 1)
        dn, values = of.added_values.items()[0]
        self.assertEqual(dn, 'cn=jens' + ',' + 'dc=localhost')
        self.assertEqual(values['cn'], ['jens'])

    def test_insert_binary(self):
        of = DummyLDAPObjectFactory('conn_string')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.insert('dc=localhost', 'cn=jens', {'myvalue;binary' : u'a'})
        self.failUnless(of.added)
        self.assertEqual(len(of.added_values.keys()), 1)
        dn, values = of.added_values.items()[0]
        self.assertEqual(values['myvalue'], u'a')

    def test_modify_explicit_add(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        import ldap
        conn.modify('dn', mod_type=ldap.MOD_ADD, attrs={'b':'b'})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'dn')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        self.assertEqual(mode, ldap.MOD_ADD)
        self.assertEqual(key, 'b')
        self.assertEqual(values, ['b'])

        # Trying to add an empty new value should not cause more operations
        conn.modify('dn', mod_type=ldap.MOD_ADD, attrs={'c':''})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_explicit_modify(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        import ldap
        conn.modify('dn', mod_type=ldap.MOD_REPLACE, attrs={'a':'y'})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'dn')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        self.assertEqual(mode, ldap.MOD_REPLACE)
        self.assertEqual(key, 'a')
        self.assertEqual(values, ['y'])

        # Trying to modify a non-existing key with an empty value should
        # not result in more operations
        conn.modify('dn', mod_type=ldap.MOD_REPLACE, attrs={'b':''})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_explicit_delete(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        import ldap
        conn.modify('dn', mod_type=ldap.MOD_DELETE, attrs={'a':'y'})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'dn')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        self.assertEqual(mode, ldap.MOD_DELETE)
        self.assertEqual(key, 'a')

        # Tryng to modify the record by providing an empty non-existing key
        # should not result in more operations.
        conn.modify('dn', mod_type=ldap.MOD_DELETE, attrs={'b':''})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_implicit_add(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.modify('dn', attrs={'b':'b'})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'dn')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        import ldap
        self.assertEqual(mode, ldap.MOD_ADD)
        self.assertEqual(key, 'b')
        self.assertEqual(values, ['b'])

        # Trying to add an empty new value should not cause more operations
        conn.modify('dn', attrs={'c':''})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_implicit_modify(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.modify('dn', attrs={'a':'y'})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'dn')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        import ldap
        self.assertEqual(mode, ldap.MOD_REPLACE)
        self.assertEqual(key, 'a')
        self.assertEqual(values, ['y'])

        # Trying to modify a non-existing key should
        # not result in more operations
        conn.modify('dn', attrs={'b':'z'})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_implicit_delete(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.modify('dn', attrs={'a':''})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'dn')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        import ldap
        self.assertEqual(mode, ldap.MOD_DELETE)
        self.assertEqual(key, 'a')

        # Trying to modify the record by providing an empty non-existing key
        # should not result in more operations.
        conn.modify('dn', attrs={'b':''})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_readonly(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory, read_only=True)
        self.assertRaises(RuntimeError, conn.modify, 'dn', {})

    def test_modify_binary(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.modify('dn', attrs={'a;binary':u'y'})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'dn')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        self.assertEqual(key, 'a')
        self.assertEqual(values, u'y')

    def test_modify_modrdn(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('a=oldvalue,dc=localhost', {'a':'oldvalue'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory, rdn_attr='a')
        conn.modify('a=oldvalue,dc=localhost', attrs={'a':'newvalue'})
        self.failUnless(of.modified_rdn)
        self.assertEqual(of.old_dn, 'a=oldvalue,dc=localhost')
        self.assertEqual(of.new_rdn, 'a=newvalue')
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'a=newvalue,dc=localhost')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        self.assertEqual(key, 'a')
        self.assertEqual(values, ['newvalue'])

    def test_modify_referral(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        import ldap
        of.mod_exc = ( ldap.REFERRAL
                     , {'info':'please go to ldap://otherhost:1389'}
                     )
        def factory(conn_string):
            of.conn_string = conn_string
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.modify('dn', attrs={'a':'y'})
        self.assertEqual(of.conn_string, 'ldap://otherhost:1389')
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'dn')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        self.assertEqual(mode, ldap.MOD_REPLACE)
        self.assertEqual(key, 'a')
        self.assertEqual(values, ['y'])

    def test_delete(self):
        of = DummyLDAPObjectFactory('conn_string')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.delete('dn')
        self.failUnless(of.deleted)
        self.assertEqual(of.deleted_dn, 'dn')

    def test_delete_readonly(self):
        of = DummyLDAPObjectFactory('conn_string')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory, read_only=True)
        self.assertRaises(RuntimeError, conn.delete, 'dn')

    def test_delete_referral(self):
        of = DummyLDAPObjectFactory('conn_string')
        import ldap
        of.del_exc = ( ldap.REFERRAL
                     , {'info':'please go to ldap://otherhost:1389'}
                     )
        def factory(conn_string):
            of.conn_string = conn_string
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.delete('dn')
        self.assertEqual(of.conn_string, 'ldap://otherhost:1389')
        self.failUnless(of.deleted)
        self.assertEqual(of.deleted_dn, 'dn')


def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])

