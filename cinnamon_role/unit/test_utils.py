import mock
from tempest.lib import exceptions as lib_exc

from cinnamon_role import expected_results
from cinnamon_role import role_set
from cinnamon_role.unit import base
from cinnamon_role import utils


class TestUtils(base.BaseTestCase):
    def test_wrap_success(self):
        my_func = mock.Mock()
        my_func.__name__ = 'foo'

        wrapped_func = utils.wrap_success(my_func)

        self.assertEqual(my_func, wrapped_func)

    def test_wrap_success_test_fails(self):
        my_func = mock.Mock()
        my_func.__name__ = 'foo'
        my_func.side_effect = lib_exc.Forbidden

        wrapped_func = utils.wrap_success(my_func)

        self.assertRaises(lib_exc.Forbidden, wrapped_func)

    def test_wrap_unauthorized_expected_fail(self):
        my_func = mock.Mock()
        my_func.__name__ = 'foo'
        my_func.side_effect = lib_exc.Forbidden

        wrapped_func = utils.wrap_unauthorized(my_func)

        try:
            wrapped_func()
        except Exception:
            self.fail("The test should've passed when Forbidden was raised")

    def test_wrap_unauthorized_test_succeeds(self):
        my_func = mock.Mock()
        my_func.__name__ = 'foo'

        wrapped_func = utils.wrap_unauthorized(my_func)

        # Test expecting unauthorized should raise
        # an AssertionError instead of passing
        self.assertRaises(AssertionError, wrapped_func)

    def test_wrap_unauthorized_unexpected_fail(self):
        my_func = mock.Mock()
        my_func.__name__ = 'foo'
        my_func.side_effect = lib_exc.NotFound

        wrapped_func = utils.wrap_unauthorized(my_func)

        self.assertRaises(lib_exc.NotFound, wrapped_func)

    def test_find_tests(self):
        pass

    def test_wrap_for_role_set(self):
        self._do_wrap_test()

    def test_wrap_for_role_set_unauthorized(self):
        self._do_wrap_test(unauthorized=True)

    @mock.patch('cinnamon_role.utils.CONF')
    @mock.patch.object(expected_results, 'ExpectedResultsProvider')
    @mock.patch.object(utils, 'wrap_success')
    @mock.patch.object(utils, 'wrap_unauthorized')
    def _do_wrap_test(self, mock_unauth, mock_succ, mock_erp,
                      mock_conf, unauthorized=False):
        mock_conf.cinnamon.expected_results_file = 'foo.yaml'
        mock_provider = mock.Mock()
        mock_get = mock.Mock()
        mock_result = mock.Mock()
        mock_provider.get_result = mock_get
        mock_erp.return_value = mock_provider
        mock_result.is_expected_fail.return_value = unauthorized
        mock_get.return_value = mock_result
        mock_unauth.return_value = 'unauth'
        mock_succ.return_value = 'success'

        my_func = mock.Mock()
        full_name = 'path.to.my.test'
        rs = role_set.RoleSet('user1', ['role1', 'role2'])

        wrapped = utils.wrap_for_role_set(my_func, full_name, rs)

        expected_return = 'unauth' if unauthorized else 'success'
        self.assertEqual(expected_return, wrapped, "Wrapped the function "
                         "incorrectly")
        mock_erp.assert_called_once_with('foo.yaml')
        mock_get.assert_called_once_with(full_name, rs.name)
        if unauthorized:
            mock_unauth.assert_called_once_with(my_func)
        else:
            mock_succ.assert_called_once_with(my_func)
