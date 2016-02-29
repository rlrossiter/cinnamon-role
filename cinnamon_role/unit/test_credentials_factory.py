import mock

from cinnamon_role import credentials_factory as creds
from cinnamon_role.unit import base


class TestCredentialsFactory(base.BaseTestCase):
    def test_with_role_matching_credentials(self, mock_gcm, mock_ara,
                                            mock_gcp):
        pass

    def test_get_credentials_provider(self):
        pass

    def test_get_credentials_provider_already_has_attr(self):
        pass

    def test_are_roles_available(self):
        pass

    def test_are_roles_available_not_on_cred_provider(self):
        pass

    def test_get_client_manager(self):
        pass

    def test_get_client_manager_without_roles(self):
        pass

    def test_get_credentials_provider(self):
        pass

    def test_get_credentials_provider_no_accounts_file(self):
        pass
