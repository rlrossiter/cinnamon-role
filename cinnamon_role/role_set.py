# Copyright (c) 2016 Ryan Rossiter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import yaml

from tempest import exceptions


def read_role_sets_yaml(path):
    # Reads in the role sets to use
    try:
        with open(path, 'r') as yaml_file:
            role_sets = yaml.safe_load(yaml_file)
    except IOError:
        raise exceptions.InvalidConfiguration(
            ('The path for the role sets file: %s '
             'could not be found.') % path)
    return role_sets


class RoleSetProvider(object):
    """A class used to provide the role sets to be used."""
    def __init__(self, role_sets_file):
        super(RoleSetProvider, self).__init__()
        role_sets = read_role_sets_yaml(role_sets_file)
        self.role_sets = []
        for name, roles in role_sets.items():
            self.role_sets.append(RoleSet(name, roles))
        self.role_sets = [RoleSet(n, r) for n, r in role_sets.items()]

    def get_role_sets(self):
        """Gets the role sets to be used."""
        return self.role_sets


class RoleSet(object):
    """An object used to hold the group of roles under a classificiation.

    This associates a name to a group of OpenStack-defined roles. These
    users are used to map to successes or failures in the test listing
    file.
    """
    def __init__(self, set_name, roles):
        self._name = set_name
        self._roles = roles

    @property
    def name(self):
        return self._name

    @property
    def roles(self):
        return self._roles
