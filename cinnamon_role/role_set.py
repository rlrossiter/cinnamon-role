import yaml

from tempest import exceptions


def read_role_sets_yaml(path):
    try:
        with open(path, 'r') as yaml_file:
            role_sets = yaml.safe_load(yaml_file)
    except IOError:
        raise exceptions.InvalidConfiguration(
            ('The path for the role sets file: %s '
             'could not be found.') % path)
    return role_sets


class RoleSetProvider(object):
    def __init__(self, role_sets_file):
        super(RoleSetProvider, self).__init__()
        role_sets = read_role_sets_yaml(role_sets_file)
        self.role_sets = []
        for name, roles in role_sets.items():
            self.role_sets.append(RoleSet(name, roles))
        self.role_sets = [RoleSet(n, r) for n, r in role_sets.items()]

    def get_role_sets(self):
        return self.role_sets


class RoleSet(object):
    def __init__(self, set_name, roles):
        self._name = set_name
        self._roles = roles

    @property
    def name(self):
        return self._name

    @property
    def roles(self):
        return self._roles
