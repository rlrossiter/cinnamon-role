import sys

from tempest import config

from cinnamon_role import credentials_factory
from cinnamon_role import role_set
from cinnamon_role import utils

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest

CONF = config.CONF
RSP = role_set.RoleSetProvider(CONF.cinnamon.role_sets_file)


class for_each_role_set(object):
    def __init__(self, module):
        self.mod = module

    def __call__(self, cls):
        name = cls.__name__
        role_sets = get_role_sets()
        test_cases = []

        for rs in role_sets:
            new_name, new_cls = self._generate_class(name, (cls, ), rs)
            setattr(sys.modules[self.mod], new_name, new_cls)
            test_cases.append(new_cls)

        def load_tests(loader, standard_tests, pattern):
            suite = unittest.TestSuite()
            for test_class in test_cases:
                tests = loader.loadTestsFromTestCase(test_class)
                suite.addTests(tests)

            return suite

        setattr(sys.modules[self.mod], 'load_tests',
                load_tests)

        return cls

    def _generate_class(self, name, supers, rs):
        new_name = '%s_%s' % (name, rs.name)
        new_cls = type(new_name, supers, {})
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
    super(cls, cls).setup_credentials()
    attr = 'os_roles_%s' % cls.credentials[0][0]
    cls.os = cls.manager = getattr(cls, attr)
