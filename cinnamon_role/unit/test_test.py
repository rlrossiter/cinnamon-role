import mock

from cinnamon_role.unit import base


class TestForEachRoleSet(base.BaseTestCase):
    def setUp(self):
        super(TestForEachRoleSet, self).setUp()
        self.conf_patcher = mock.patch('tempest.config')
        self.rs_patcher = mock.patch('cinnamon_role.role_set')
        self.conf_patcher.start()
        self.mock_rs = self.rs_patcher.start()
        self.addCleanup(self._stop_patcher)
        from cinnamon_role import test
        self.cr_test = test

    def _stop_patcher(self):
        self.conf_patcher.stop()
        self.rs_patcher.stop()

    def test_for_each_role_set_decorator(self):
        self._test_decorator()

    def test_for_each_role_set_with_test_module(self):
        self._test_decorator(use_test_module=True)

    def _test_decorator(self, use_test_module=False):
        fanout = mock.Mock()
        mock_class = mock.Mock()
        mock_class.__module__ = 'foo'

        with mock.patch.object(self.cr_test, 'TestGenerator') as mock_tg:
            mock_tg.return_value.fan_out = fanout
            kwargs = {'test_module': 'test_mod'} if use_test_module else {}
            actual_return = self.cr_test.for_each_role_set(mock_class,
                                                           **kwargs)

        expected_test_module = 'test_mod' if use_test_module else 'foo'
        mock_tg.assert_called_once_with(
            'foo', test_module=expected_test_module)
        fanout.assert_called_once_with(mock_class)
        self.assertEqual(fanout.return_value, actual_return)
