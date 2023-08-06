# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 by Gustavo Narea <http://gustavonarea.net/>
#
# This file is part of PyACL <http://code.gustavonarea.net/pyacl/>
#
# PyACL is freedomware: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or any later version.
#
# PyACL is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyACL. If not, see <http://www.gnu.org/licenses/>.

"""
Test utilities for PyACL source adapters.

"""

from acl.exc import SourceError, ExistingGroupError, NonExistingGroupError, \
                    UserPresentError, UserNotPresentError

__all__ = ['GroupsAdapterTester', 'ReadOnlyGroupsAdapterTester']


class _ReadOnlyBaseAdapterTester(object):
    """Base test case for read-only adapters"""
    
    def _get_all_users(self):
        all_users = set()
        for users in self.all_groups.values():
            all_users |= users
        return all_users
    
    def _get_user_groups(self, user):
        return set([n for (n, s) in self.all_groups.items() if user in s])
    
    def test_retrieving_all_groups(self):
        self.assertEqual(self.adapter._get_all_groups(), self.all_groups)
    
    def test_getting_group_users(self):
        for group_name, users in self.all_groups.items():
            self.assertEqual(self.adapter._get_group_users(group_name),
                             users)
    
    def test_checking_existing_group(self):
        for group_name in self.all_groups.keys():
            assert self.adapter._group_exists(group_name), \
                   'group "%s" does NOT exist' % group_name
    
    def test_checking_non_existing_group(self):
        group_name = u'i_dont_exist'
        assert not self.adapter._group_exists(group_name), \
               'group "%s" DOES exist' % group_name
    
    def test_checking_user_inclusion(self):
        for group_name, users in self.all_groups.items():
            for user in self.adapter._get_group_users(group_name):
                assert self.adapter._user_is_included(group_name, user), \
                       'User "%s" must be included in group "%s"' % \
                       (user, group_name)
    
    def test_checking_excluded_user_inclusion(self):
        excluded_user = self.new_users.pop()
        for group_name, users in self.all_groups.items():
            assert not self.adapter._user_is_included(group_name,
                                                      excluded_user), \
                   'User "%s" must not included in group "%s"' % \
                       (user, group_name)
    
    def test_checking_group_existence(self):
        for group_name in self.all_groups.keys():
            assert self.adapter._group_exists(group_name), \
                   'group "%s" must exist' % group_name
    
    def test_checking_non_existing_group_existence(self):
        invalid_group = u'designers'
        assert not self.adapter._group_exists(invalid_group), \
                   'group "%s" must not exist' % invalid_group

    def test_sets_if_it_writable(self):
        assert hasattr(self.adapter, 'writable'), \
               "The adapter doesn't have the 'writable' attribute; " \
               "please call its parent's constructor too"


class _BaseAdapterTester(_ReadOnlyBaseAdapterTester):
    """Base test case for read & write adapters"""
    
    def test_adding_many_users_to_group(self):
        for group_name, users in self.all_groups.items():
            self.adapter._include_users(group_name, self.new_users)
            final_users = users | self.new_users
            assert self.adapter._get_group_users(group_name)==final_users, \
                   '"%s" does not include %s' % (group_name, self.new_users)
    
    def test_creating_group(self):
        group = u'cool-group'
        self.adapter._create_group(group)
        assert group in self.adapter._get_all_groups().keys(), \
               'group "%s" could not be added' % group
    
    def test_editing_group(self):
        old_group = self.all_groups.keys()[0]
        new_group = u'cool-group'
        self.adapter._rename_group(old_group, new_group)
        assert new_group in self.adapter._get_all_groups().keys() and \
               old_group not in self.adapter._get_all_groups().keys(), \
               'group "%s" was not renamed to "%s"' % (old_group,
                                                         new_group)

    def test_deleting_group(self):
        group = self.all_groups.keys()[0]
        self.adapter._delete_group(group)
        assert group not in self.adapter._get_all_groups().keys(), \
               'group "%s" was not deleted' % group


class ReadOnlyGroupsAdapterTester(_ReadOnlyBaseAdapterTester):
    """
    Test case for read-only groups source adapters.
    
    The groups source used for the tests must only contain the following
    groups (aka "groups") and their relevant users (aka "users"; if any):
    
    * admins
       * rms
    * developers
       * rms
       * linus
    * trolls
       * sballmer
    * python
    * php
    
    .. attribute:: adapter
    
        An instance of the :term:`group adapter` to be tested.
    
    For example, a test case for the mock group adapter
    ``FakeReadOnlyGroupSourceAdapter`` may look like this::
    
        from acl.testutil.adapters import ReadOnlyGroupsAdapterTester
        
        class TestReadOnlyGroupsAdapterTester(ReadOnlyGroupsAdapterTester, 
                                              unittest.TestCase):
            def setUp(self):
                super(TestReadOnlyGroupsAdapterTester, self).setUp()
                self.adapter = FakeReadOnlyGroupSourceAdapter()
    
    .. note::
        
        :class:`GroupsAdapterTester` extends this test case to check write
        operations.
    
    """
    
    new_users = set((u'guido', u'rasmus'))
    
    def setUp(self):
        self.all_groups = {
            u'admins': set((u'rms', )),
            u'developers': set((u'rms', u'linus')),
            u'trolls': set((u'sballmer', )),
            u'python': set(),
            u'php': set()
        }
    
    def test_finding_groups_of_authenticated_user(self):
        for userid in self._get_all_users():
            self.assertEqual(self.adapter._find_groups(userid),
                             self._get_user_groups(userid))
    
    def test_finding_groups_of_non_existing_user(self):
        user = u'gustavo'
        self.assertEqual(self.adapter._find_groups(user), set())


class GroupsAdapterTester(ReadOnlyGroupsAdapterTester, _BaseAdapterTester):
    """
    Test case for groups source adapters.
    
    This test case extends :class:`ReadOnlyGroupsAdapterTester` to test
    write operations in read & write adapters and it should be set up the same
    way as its parent. For example, a test case for the mock group adapter
    ``FakeGroupSourceAdapter`` may look like this::
    
        from acl.testutil.adapters import GroupsAdapterTester
        
        class TestGroupsAdapterTester(GroupsAdapterTester, unittest.TestCase):
            def setUp(self):
                super(TestGroupsAdapterTester, self).setUp()
                self.adapter = FakeGroupSourceAdapter()
    
    """
    
    def test_removing_many_users_from_group(self):
        group = u'developers'
        users = (u'rms', u'linus')
        self.adapter._exclude_users(group, users)
        assert self.adapter._get_group_users(group)==set(), \
               '"%s" still includes %s' % (group, users)
