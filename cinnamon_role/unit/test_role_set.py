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
from tempest import exceptions

from cinnamon_role import role_set
from cinnamon_role.unit import base


class TestRoleSetProvider(base.BaseTestCase):
    @mock.patch('cinnamon_role.role_set.open')
    @mock.patch('yaml.safe_load')
    def test_read_role_sets_yaml(self, mock_load, mock_open):
        mock_file = mock.MagicMock(spec=file)
        mock_sets = mock.Mock()
        mock_open.return_value = mock_file
        mock_load.return_value = mock_sets
        path = 'foo/bar.yaml'

        sets = role_set.read_role_sets_yaml(path)

        mock_open.assert_called_once_with(path, 'r')
        read_file = mock_file.__enter__.return_value
        mock_load.assert_called_once_with(read_file)
        self.assertEqual(mock_sets, sets)

    @mock.patch('cinnamon_role.role_set.open')
    def test_read_role_sets_yaml_no_file(self, mock_open):
        mock_open.side_effect = IOError

        self.assertRaises(exceptions.InvalidConfiguration,
                          role_set.read_role_sets_yaml, 'foo')

    @mock.patch.object(role_set, 'read_role_sets_yaml')
    def test_get_role_sets(self, mock_read):
        sets = {'user1': ['role1'], 'user2': ['role1', 'role2']}
        mock_read.return_value = sets

        rsp = role_set.RoleSetProvider('foo.yaml')
        actual_sets = rsp.get_role_sets()

        rs1 = role_set.RoleSet('user1', ['role1'])
        rs2 = role_set.RoleSet('user2', ['role1', 'role2'])
        expected_sets = [rs1, rs2]
        self.assertEqual(2, len(actual_sets))
        for rs in expected_sets:
            actual_rs = [s for s in expected_sets if s.name == rs.name][0]
            self.assertEqual(rs.name, actual_rs.name)
            self.assertEqual(rs.roles, actual_rs.roles)


class TestRoleSet(base.BaseTestCase):
    def test_role_set(self):
        name = 'fooset'
        roles = ['role1', 'role2']

        rs = role_set.RoleSet(name, roles)

        self.assertEqual(name, rs.name)
        self.assertEqual(roles, rs.roles)
