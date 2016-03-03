import sys

from tempest import config

from cinnamon_role import credentials_factory
from cinnamon_role import role_set
from cinnamon_role import utils

import unittest2 as unittest

CONF = config.CONF
RSP = role_set.RoleSetProvider(CONF.cinnamon.role_sets_file)


def for_each_role_set(cls):
    gen = TestGenerator(cls.__module__)
    return gen.fan_out(cls)


class TestGenerator(object):
    """Fans out the test case for all role sets.

    This class takes all user types (role sets) that are defined in the
    role sets file. It then creates a new test class for each role set.
    This test class is then placed on the module containing the original
    test case. This decorator also generates a load_tests() function for the
    module, so when the tests for the module are loaded, it only finds the
    tests that were generated for each user type, and it hides the original
    test class (because those tests are not intended to be run in this
    setting.
    """
    def __init__(self, mod):
        self.mod = mod

    def fan_out(self, cls):
        name = cls.__name__
        role_sets = get_role_sets()
        test_cases = []

        # Generate a new test class for each role set and place it in the
        # module
        for rs in role_sets:
            new_name, new_cls = self._generate_class(name, (cls, ), rs)
            setattr(sys.modules[self.mod], new_name, new_cls)
            test_cases.append(new_cls)

        # this is the custom load_tests function that will be set on the
        # module so when tests are loaded, it gets only the tests generated
        # by this decorator
        # TODO(rlrossit): Right now this will overwrite any existing
        # load_tests() function that is already on the module.
        # because of this, only one test class can be defined per module.
        # This should be changed over to "inherit" from the existing
        # load_tests so it groups all together and returns all tests
        def load_tests(loader, standard_tests, pattern):
            suite = unittest.TestSuite()
            for test_class in test_cases:
                subsuite = unittest.TestSuite()
                tests = loader.loadTestsFromTestCase(test_class)
                subsuite.addTests(tests)
                suite.addTests(subsuite)

            return suite

        setattr(sys.modules[self.mod], 'load_tests',
                load_tests)

        # We give back the original class because we don't want to do anything
        # to it
        return cls

    def _generate_class(self, name, supers, rs):
        """Generate a new test class.

        :param name: The name of the original test class
        :param supers: The tuple to use as the super classes for these new
                       test classes (should contain at least the original test
                       class)
        :param rs: The role set the test class will be testing against
        """
        new_name = '%s_%s' % (name, rs.name)
        # Empty dictionary in type() means inherit the dict from the super
        # classes
        new_cls = type(new_name, supers, {})
        # We also need to decorate this new class so it uses the credentials
        # provider that exactly matches roles on users
        new_cls = credentials_factory.with_role_matching_credentials(new_cls)
        creds = [rs.name]
        creds.extend(rs.roles)
        new_cls.credentials = [creds]
        new_cls.setup_credentials = setup_credentials

        # wrap test functions for expected passes or failures
        for f in utils.find_tests(new_cls):
            full_name = '%s.%s.%s' % (self.mod, name, f)
            func = getattr(new_cls, f)
            setattr(new_cls, f,
                    utils.wrap_for_role_set(func, full_name, rs))

        return new_name, new_cls


def get_role_sets():
    return RSP.get_role_sets()


@classmethod
def setup_credentials(cls):
    # The new setup_credentials that will be used on the classes.
    # It overwrites their existing manager to use the user credentials
    # we found when making client requests.
    super(cls, cls).setup_credentials()
    attr = 'os_roles_%s' % cls.credentials[0][0]
    cls.os = cls.manager = getattr(cls, attr)
