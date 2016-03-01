import functools
import inspect

from tempest import config
from tempest_lib import exceptions as lib_exc

from cinnamon_role import expected_results

CONF = config.CONF


def wrap_success(f):
    """Wrap a function to handle a successful test."""
    # Do nothing because we'll just let a success roll
    return f


def wrap_unauthorized(f):
    """Wrap a function to expect an unauthorized failure."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except lib_exc.Forbidden:
            pass
        else:
            raise AssertionError("The test was expected to be forbidden from "
                                 "performing an action, but was "
                                 "unrestricted.")
    return wrapper


def find_tests(cls):
    """Find all tests on the given class."""
    all_functions = inspect.getmembers(
        cls, predicate=lambda x: inspect.ismethod(x) or inspect.isfunction(x))

    # Grab all of the functions that start with 'test_' in the class
    function_names = [f[0] for f in all_functions]
    test_functions = [f for f in function_names if f.startswith('test_')]
    return test_functions


def wrap_for_role_set(f, full_name, role_set):
    """Wrap the function on the class based on what the expected results.

    If a test or user is not defined in the class, it is assumed that the
    test (or the user) will pass.
    """
    results_file = CONF.cinnamon.expected_results_file
    erp = expected_results.ExpectedResultsProvider(results_file)
    er = erp.get_result(full_name, role_set.name)

    # Make the default assumption to pass
    if er.is_expected_fail():
        return wrap_unauthorized(f)
    else:
        return wrap_success(f)
