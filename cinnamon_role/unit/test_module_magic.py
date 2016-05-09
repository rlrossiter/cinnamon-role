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
