import sys

from tempest import config

from cinnamon_role import role_set

CONF = config.CONF
RSP = role_set.RoleSetProvider(CONF.cinnamon.role_sets_file)


class for_each_role_set(object):
    def __init__(self, module):
        self.mod = module

    def __call__(self, cls):
        name = cls.__name__
        role_sets = get_role_sets()

        for role_set in role_sets[1:]:
            new_name, new_cls = self._generate_class(name, (cls, ), role_set)
            setattr(sys.modules[self.mod], new_name, new_cls)

        _, cls = self._generate_class(name, tuple(cls.mro()), role_sets[0])
        return cls

    def _generate_class(self, name, supers, role_set):
        new_name = '%s_%s' % (name, role_set.name)
        creds = [role_set.name]
        creds.extend(role_set.roles)
        new_cls = type(new_name, supers, {'credentials': [creds]})
        return new_name, new_cls


def get_role_sets():
    return RSP.get_role_sets()
