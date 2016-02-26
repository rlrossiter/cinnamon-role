import sys

from tempest import config

from cinnamon_role import role_set
from cinnamon_role import utils

CONF = config.CONF
RSP = role_set.RoleSetProvider(CONF.cinnamon.role_sets_file)


class for_each_role_set(object):
    def __init__(self, module):
        self.mod = module

    def __call__(self, cls):
        name = cls.__name__
        role_sets = get_role_sets()

        for rs in role_sets:
            new_name, new_cls = self._generate_class(name, (cls, ), rs)
            setattr(sys.modules[self.mod], new_name, new_cls)

        return cls

    def _generate_class(self, name, supers, rs):
        new_name = '%s_%s' % (name, rs.name)
        new_cls = type(new_name, supers, {})
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
    my_base = cls.__bases__[0]
    original_creds = my_base.credentials
    my_base.credentials = cls.credentials
    cls.__bases__[0].setup_credentials()

    attr = 'os_roles_%s' % cls.credentials[0][0]
    cls.os = cls.manager = getattr(cls, attr)

    my_base.credentials = original_creds
