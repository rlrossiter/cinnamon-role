from tempest.common import credentials_factory
from tempest import config

from cinnamon_role import preprov_creds as ppc

CONF = config.CONF


def with_role_matching_credentials(cls):
    """Make the class use only credentials with exact matching roles.

    In order to make the class get credentials for the exact roles on users,
    the credentials provider sections of tempest need to be overwritten to
    grab correct users for a given role set.
    """
    cls._get_credentials_provider = classmethod(_get_credentials_provider)
    cls.are_roles_available = classmethod(_are_roles_available)
    cls.get_client_manager = classmethod(_get_client_manager)

    return cls


def _get_credentials_provider(cls):
    # The new _get_credentails_provider() of the class
    # it runs the local get_credentials_provider() if _creds_provider is
    # not already set
    if (not hasattr(cls, '_creds_provider') or not cls._creds_provider or
            not cls._creds_provider.name == cls.__name__):
        force_tenant_isolation = getattr(cls, 'force_tenant_isolation',
                                         False)

        cls._creds_provider = get_credentials_provider(
            name=cls.__name__, network_resources=cls.network_resources,
            force_tenant_isolation=force_tenant_isolation,
            identity_version=cls.get_identity_version())
    return cls._creds_provider


def _are_roles_available(cls, roles):
    # A new method that checks to see if there exists a user with exactly
    # the roles specified.
    # Calls into the cred provider to get that information, if the
    # creds provider can supply it.
    cred_provider = cls._get_credentials_provider()

    # Only check if the roles are available if we're using
    # the custom cred provider, otherwise return True
    # so we don't hold things up
    if hasattr(cred_provider, 'are_roles_available'):
        return cred_provider.are_roles_available(roles)
    else:
        return True


def _get_client_manager(cls, credential_type=None, roles=None,
                        force_new=None):
    # The new get_client_manager() method of the class.
    # It raises a skip exception if there is no user with exactly the roles
    # on a user.
    if roles:
        if not cls.are_roles_available(roles):
            skip_msg = (
                "%s skipped because the configured credential provider"
                " is not able to provide credentials with the roles "
                "%s assigned" % (cls.__name__, roles))
            raise cls.skipException(skip_msg)
    return super(cls, cls).get_client_manager(
        credential_type=credential_type, roles=roles, force_new=force_new)


def get_credentials_provider(name, network_resources=None,
                             force_tenant_isolation=False,
                             identity_version=None):
    # A new get_credentials_provider() function. It gets the tempest
    # credentials provider, and if an accounts yaml is specified, gets
    # the new creds provider that is used to exactly match roles on users
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
