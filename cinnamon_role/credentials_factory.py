from tempest.common import credentials_factory
from tempest import config

from cinnamon_role import preprov_creds as ppc

CONF = config.CONF


def with_role_matching_credentials(cls):
    @classmethod
    def _get_credentials_provider(cls):
        if (not hasattr(cls, '_creds_provider') or not cls._creds_provider or
                not cls._creds_provider.name == cls.__name__):
            force_tenant_isolation = getattr(cls, 'force_tenant_isolation',
                                             False)

            cls._creds_provider = get_credentials_provider(
                name=cls.__name__, network_resources=cls.network_resources,
                force_tenant_isolation=force_tenant_isolation,
                identity_version=cls.get_identity_version())
        return cls._creds_provider

    @classmethod
    def are_roles_available(cls, roles):
        cred_provider = cls._get_credentials_provider()

        # Only check if the roles are available if we're using
        # the custom cred provider, otherwise return True
        # so we don't hold things up
        if hasattr(cred_provider, 'are_roles_available'):
            return cred_provider.are_roles_available(roles)
        else:
            return True

    @classmethod
    def get_client_manager(cls, credential_type=None, roles=None,
                           force_new=None):
        if roles:
            if not cls.are_roles_available(roles):
                skip_msg = (
                        "%s skipped because the configured credential provider"
                        " is not able to provide credentials with the roles "
                        "%s assigned" % (cls.__name__, roles))
                raise cls.skipException(skip_msg)
        return super(cls, cls).get_client_manager(
            credential_type=credential_type, roles=roles, force_new=force_new)

    cls._get_credentials_provider = _get_credentials_provider
    cls.are_roles_available = are_roles_available
    cls.get_client_manager = get_client_manager

    return cls


def get_credentials_provider(name, network_resources=None,
                             force_tenant_isolation=False,
                             identity_version=None):
    provider = credentials_factory.get_credentials_provider(
        name, network_resources=network_resources,
        force_tenant_isolation=force_tenant_isolation,
        identity_version=identity_version)

    if CONF.auth.test_accounts_file:
        return ppc.ExactRoleMatchingPreProvisionedCredentialProvider(
            name=name, identity_version=identity_version,
            **credentials_factory._get_preprov_provider_params())
    else:
        return provider
