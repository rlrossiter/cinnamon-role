# Copyright 2015
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import os

from oslo_config import cfg
from tempest import config
from tempest.test_discover import plugins


CinnamonGroup = [
    cfg.StrOpt('role_sets_file',
               help="""Path to the yaml file that contains the list of role
sets to test policies on. The file follows the following structure:
    admin:
      - admin_role_1
      - admin_role_2
    regular_user:
      - regular_user_role

The list under the role set is the list of roles that are assumed to be on a
user of that type. If pre-provisioned credentials are used, it is assumed that
users with these exact roles exist. If dynamic credentials are used,
users will be generated with these roles placed on them."""),

    cfg.StrOpt('expected_results_file',
               help="""Path to the yaml file that contains the list of tests,
and their expected results. The file follows the following structure:
    cinnamon_role.tests.scenario.TestGivenScenario.test_given_scenario_1:
      pass:
        - admin
      fail:
        - regular_user

If any tests are not listed, it is assumed that all users will pass it. If a
user is not listed under the test, it is assumed that that user will
pass."""),
]


cinnamon_group = cfg.OptGroup(name='cinnamon', title='Cinnamon Role Options')


class CinnamonRolePlugin(plugins.TempestPlugin):
    def load_tests(self):
        base_path = os.path.split(os.path.dirname(
            os.path.abspath(__file__)))[0]
        test_dir = "cinnamon_role/tests"
        full_test_dir = os.path.join(base_path, test_dir)
        return full_test_dir, base_path

    def register_opts(self, conf):
        for g, o in self.get_opt_lists():
            config.register_opt_group(conf, g, o)

    def get_opt_lists(self):
        return [(cinnamon_group, CinnamonGroup)]
