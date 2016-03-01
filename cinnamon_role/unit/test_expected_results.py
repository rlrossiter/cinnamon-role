import mock
from tempest import exceptions

from cinnamon_role import expected_results
from cinnamon_role.unit import base


class TestExpectedResultsProvider(base.BaseTestCase):
    @mock.patch('cinnamon_role.expected_results.open')
    @mock.patch('yaml.safe_load')
    def test_read_expected_results_yaml(self, mock_load, mock_open):
        mock_file = mock.MagicMock(spec=file)
        mock_results = mock.Mock()
        mock_open.return_value = mock_file
        mock_load.return_value = mock_results
        path = 'foo/bar.yaml'

        er = expected_results.read_expected_results_yaml(path)

        mock_open.assert_called_once_with(path, 'r')
        read_file = mock_file.__enter__.return_value
        mock_load.assert_called_once_with(read_file)
        self.assertEqual(mock_results, er)

    @mock.patch('cinnamon_role.expected_results.open')
    def test_read_expected_results_yaml_no_file(self, mock_open):
        mock_open.side_effect = IOError

        self.assertRaises(exceptions.InvalidConfiguration,
                          expected_results.read_expected_results_yaml,
                          'foo')

    @mock.patch.object(expected_results, 'read_expected_results_yaml')
    def test_get_result(self, mock_read):
        results = {'test.foo.test_foobar': {'pass': ['user1'],
                                            'fail': ['user2']}}
        mock_read.return_value = results

        erp = expected_results.ExpectedResultsProvider('foo.yaml')
        success_result = erp.get_result('test.foo.test_foobar', 'user1')
        fail_result = erp.get_result('test.foo.test_foobar', 'user2')

        self.assertTrue(success_result.is_expected_pass())
        self.assertTrue(fail_result.is_expected_fail())

    @mock.patch.object(expected_results, 'read_expected_results_yaml')
    def test_get_result_no_test_listed(self, mock_read):
        # No tests means there is no tests that came back from expected
        # results. Because it isn't found, it is defaulted to pass
        results = {}
        mock_read.return_value = results

        erp = expected_results.ExpectedResultsProvider('foo.yaml')
        success_result = erp.get_result('test.foo.test_foobar', 'user1')

        self.assertTrue(success_result.is_expected_pass())

    @mock.patch.object(expected_results, 'read_expected_results_yaml')
    def test_get_result_no_user_listed(self, mock_read):
        # Test an unlisted user. If the user is not present, it is an
        # assumed pass
        results = {'test.foo.test_foobar': {'pass': ['user1']}}
        mock_read.return_value = results

        erp = expected_results.ExpectedResultsProvider('foo.yaml')
        success_result = erp.get_result('test.foo.test_foobar', 'not_user')

        self.assertTrue(success_result.is_expected_pass())


class TestExpectedResults(base.BaseTestCase):
    def test_expected_fail(self):
        er = expected_results.ExpectedResult(False)
        self.assertTrue(er.is_expected_fail())
        self.assertFalse(er.is_expected_pass())

    def test_expected_pass(self):
        er = expected_results.ExpectedResult(True)
        self.assertTrue(er.is_expected_pass())
        self.assertFalse(er.is_expected_fail())
