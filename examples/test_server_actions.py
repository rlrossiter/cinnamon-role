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

from tempest.api.compute.servers import test_server_actions

from cinnamon_role import test


@test.for_each_role_set
class ServerActionsTestJSON(test_server_actions.ServerActionsTestJSON):
    @classmethod
    def get_tenant_network(cls, credentials_type='primary'):
        return super(ServerActionsTestJSON, cls).get_tenant_network(
            credentials_type=cls.credentials[0])
