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
from tempest import api

from cinnamon_role import module_magic
from cinnamon_role.unit import base


class TestModuleMagic(base.BaseTestCase):
    @mock.patch.object(module_magic, '_import_packages')
    @mock.patch.object(module_magic, '_import_modules')
    @mock.patch.object(module_magic, '_get_classes')
    def test_get_all_tempest_api_tests(self, mock_gc, mock_mod, mock_pack):
        packages = ['foo', 'bar']
        mods = ['foo1', 'bar1']
        classes = ['Foo', 'Bar']
        mock_pack.return_value = packages
        mock_mod.return_value = mods
        mock_gc.return_value = classes

        actual_classes = module_magic.get_all_tempest_api_tests()

        mock_pack.assert_called_once_with(api)
        mock_mod.assert_called_once_with(set(packages))
        mock_gc.assert_called_once_with(set(mods))
        self.assertEqual(set(classes), actual_classes)
