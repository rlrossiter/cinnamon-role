from tempest.api.compute.servers import test_server_actions

from cinnamon_role import test


@test.for_each_role_set(__name__)
class ServerActionsTestJSON(test_server_actions.ServerActionsTestJSON):
    @classmethod
    def get_tenant_network(cls, credentials_type='primary'):
        return super(ServerActionsTestJSON, cls).get_tenant_network(
            credentials_type=cls.credentials[0][0])
