from tempest.common import preprov_creds
from tempest_lib import exceptions as lib_exc


class ExactRoleMatchingPreProvisionedCredentialProvider(
    preprov_creds.PreProvisionedCredentialProvider):

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
                temp_hashes = set(temp_hashes) - set(users_to_remove)

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
