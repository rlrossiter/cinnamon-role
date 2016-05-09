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

from tempest.common import preprov_creds
from tempest.lib import exceptions as lib_exc


class ExactRoleMatchingPreProvisionedCredentialProvider(
    preprov_creds.PreProvisionedCredentialProvider):
    """Credentials provider that exactly matches roles on users.

    It uses most of the existing preprov creds provider, but adds more
    restrictiveness. The existing provider checks to see if the desired
    roles are a subset of any user. This provider changes that to be an
    exact match of roles on the user.
    """

    def _get_match_hash_list(self, roles=None):
        temp_hashes = super(
            ExactRoleMatchingPreProvisionedCredentialProvider,
            self)._get_match_hash_list(roles=roles)

        if roles:
            # search through the roles we don't want because if we find a user
            # in those roles, we don't want the user. We need to make an exact
            # match
            unwanted_roles = set(self.hash_dict['roles'].keys()) - set(roles)
            for role in unwanted_roles:
                unwanted_users = self.hash_dict['roles'].get(role)
                users_to_remove = set(temp_hashes) & set(unwanted_users)
                temp_hashes = list(set(temp_hashes) - set(users_to_remove))

            if not temp_hashes:
                raise lib_exc.InvalidCredentials(
                    "No credentials with exact roles %s specified in the "
                    "accounts file" % roles)

        return temp_hashes

    def are_roles_available(self, roles):
        try:
            hashes = self._get_match_hash_list(roles=roles)
        except lib_exc.InvalidCredentials:
            return False

        if hashes:
            return True
        else:
            return False
