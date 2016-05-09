# Copyright (c) 2016 Ryan Rossiter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
from tempest.lib import exceptions as lib_exc

from cinnamon_role import preprov_creds as ppc
from cinnamon_role.unit import base


class TestExactMatchingProvider(base.BaseTestCase):
    def test_get_match_hash_list(self):
        prov = self._get_provider()
        roles_wanted = ['role1', 'role2']
        # the role hashes are set up with the roles as keys, and the users
        # with that role in a list as the value
        # This dict is structured with the users/roles as follows:
        #   user1: ['role1', 'role2']
        #   user2: ['role1', 'role3']
        #   user3: ['role1', 'role2', role3']
        # We should only get user1, because that is the only user with
        # an exact match in roles
        role_hashes = {'role1': ['user1', 'user2', 'user3'],
                       'role2': ['user1', 'user3'],
                       'role3': ['user2', 'user3']}
        prov.hash_dict['roles'] = role_hashes
        expected_users = ['user1']

        with mock.patch('cinnamon_role.preprov_creds.super') as mock_sup:
            supers_users = ['user1', 'user3']
            mock_get = mock.Mock()
            mock_get.return_value = supers_users
            mock_sup.return_value._get_match_hash_list = mock_get
            actual_users = prov._get_match_hash_list(roles=roles_wanted)

        self.assertEqual(expected_users, actual_users)

    def test_get_match_hash_list_without_roles(self):
        prov = self._get_provider()
        hashes = mock.Mock()
        match_hash_list = mock.Mock()
        match_hash_list.return_value = hashes

        with mock.patch('cinnamon_role.preprov_creds.super') as mock_sup:
            mock_sup.return_value._get_match_hash_list = match_hash_list
            actual_hashes = prov._get_match_hash_list()

        self.assertEqual(hashes, actual_hashes)
        match_hash_list.assert_called_once_with(roles=None)

    def test_get_match_hash_list_no_users_available(self):
        prov = self._get_provider()
        roles_wanted = ['role1', 'role2']
        # user1: ['role1']
        # user2: ['role1', 'role3']
        # user3: ['role1', 'role2', 'role3']
        role_hashes = {'role1': ['user1', 'user2', 'user3'],
                       'role2': ['user3'],
                       'role3': ['user2', 'user3']}
        prov.hash_dict['roles'] = role_hashes

        with mock.patch('cinnamon_role.preprov_creds.super') as mock_sup:
            supers_users = ['user3']
            mock_get = mock.Mock()
            mock_get.return_value = supers_users
            mock_sup.return_value._get_match_hash_list = mock_get

            self.assertRaises(lib_exc.InvalidCredentials,
                              prov._get_match_hash_list,
                              roles=roles_wanted)

    def test_are_roles_available(self):
        prov = self._get_provider()

        with mock.patch.object(prov, '_get_match_hash_list') as mock_get:
            mock_get.return_value = ['user1', 'user2']
            are_available = prov.are_roles_available(['role1'])

        self.assertTrue(are_available)
        mock_get.assert_called_once_with(roles=['role1'])

    def test_are_roles_available_no_hashes(self):
        prov = self._get_provider()

        with mock.patch.object(prov, '_get_match_hash_list') as mock_get:
            mock_get.return_value = []
            are_available = prov.are_roles_available(['role1'])

        self.assertFalse(are_available)
        mock_get.assert_called_once_with(roles=['role1'])

    def test_are_roles_available_invalid_credentials(self):
        prov = self._get_provider()

        with mock.patch.object(prov, '_get_match_hash_list') as mock_get:
            mock_get.side_effect = lib_exc.InvalidCredentials

            roles_available = prov.are_roles_available(['role1'])

        self.assertFalse(roles_available)

    def _get_provider(self):
        return ppc.ExactRoleMatchingPreProvisionedCredentialProvider(
            'v3', None, None)
