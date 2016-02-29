import yaml

from tempest import exceptions


def read_expected_results_yaml(path):
    # reads the file with the expected testing results
    try:
        with open(path, 'r') as yaml_file:
            expected_results = yaml.safe_load(yaml_file)
    except IOError:
        raise exceptions.InvalidConfiguration(
            "The path for the expected results file: %s "
            "could not be found." % path)
    return expected_results


class ExpectedResultsProvider(object):
    """Holds the information for expected test results."""
    def __init__(self, expected_results_file):
        super(ExpectedResultsProvider, self).__init__()
        expected_results = read_expected_results_yaml(expected_results_file)
        self.expected_results = {}
        for name, results in expected_results.items():
            passing_results = results.get('pass', [])
            failing_results = results.get('fail', [])
            self.expected_results[name] = {}
            for role_set in passing_results:
                self.expected_results[name][role_set] = ExpectedResult(True)
            for role_set in failing_results:
                self.expected_results[name][role_set] = ExpectedResult(False)

    def get_result(self, name, role_set):
        # Gets the result for the given test for the given role set
        # if no test defined, assume pass
        test_results = self.expected_results.get(name)
        if not test_results:
            return ExpectedResult(True)

        # if role set unlisted, assume pass
        set_result = test_results.get(role_set) or ExpectedResult(True)
        return set_result


class ExpectedResult(object):
    """An object to hold the result of a test."""
    def __init__(self, is_success):
        self.is_success = is_success

    def is_expected_fail(self):
        return not self.is_success

    def is_expected_pass(self):
        return self.is_success
