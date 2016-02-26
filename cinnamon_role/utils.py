import functools
import inspect

from tempest_lib import exceptions as lib_exc
from tempest import config

from cinnamon_role import expected_results

CONF = config.CONF


def wrap_success(f):
    return f


def wrap_unauthorized(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except lib_exc.Forbidden:
            pass
    return wrapper


def find_tests(cls):
    all_functions = inspect.getmembers(cls,
        predicate=lambda x: inspect.ismethod(x) or inspect.isfunction(x))
    function_names = [f[0] for f in all_functions]
    test_functions = [f for f in function_names if f.startswith('test_')]
    return test_functions

def wrap_for_role_set(f, full_name, role_set):
    results_file = CONF.cinnamon.expected_results_file
    erp = expected_results.ExpectedResultsProvider(results_file)
    er = erp.get_result(full_name, role_set.name)

    # Make the default assumption to pass
    if er.is_expected_fail():
        return wrap_unauthorized(f)
    else:
        return wrap_success(f)
