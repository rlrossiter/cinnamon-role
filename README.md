# Cinnamon Role

## Purpose
Cinnamon Role allows you to test policy-related workflows with different levels of users. Each level of user is associated with a group of OpenStack roles. When a test is run in Cinnamon Role, it runs the test against each level of user. When the user is forbidden from performing a certain action, a 403 Forbidden error will be returned from the OpenStack API. If it is expected that the user will not be able to perform the action, Cinnamon Role will catch the Forbidden error and pass the test being run appropriately. If the user is expected to pass the test, the test will run normally.

This method of testing allows you to catch policy-related changes in either a positive or negative direction. If a user had access to perform an action that is now restricted, the test for that action will now fail with an uncaught Forbidden. This allows the tester to then update the policy to again allow the action, or update Cinnamon Role's itinerary to now expect the user to be performing the action.

If the user used to be forbidden from performing an action, but the policy files become more permissive, Cinnamon Role will fail the test for that action, because it expects a failure to occur.

With Cinnamon Role, policy testing becomes fully customizable.

## Terminology
Cinnamon Role defines a few new terms with respect to user level testing. Here is an explanation for the terms used by Cinnamon Role:

- **Role Set** (also called *user type*) - A user that is specified as a group of OpenStack roles.
- **Expected Result** - The expected result (pass or fail) of a given test. A mismatch in the expected result and the actual result will result in a test failure. Ex:
    - Expected: Pass // Result: Pass - *Test Case Success*
    - Expected: Pass // Result: Fail - *Test Case Failure*
    - Expected: Fail // Result: Pass - *Test Case Failure*
    - Expected: Fail // Result: Fail (Forbidden) - *Test Case Success*
    - Expected: Fail // Result: Fail (404 Not Found) - *Test Case Failure*

## How To Use
Cinnamon Role is implemented as a Tempest plugin, and uses [Tempest's plugin architecture](http://docs.openstack.org/developer/tempest/plugin.html "Tempest Plugin Interface").

### Cinnamon Role Config
Cinnamon Role piggy back's on Tempest's config, so when running Cinnamon Role through Tempest, Cinnamon Role will need configuration options to be set in the tempest.conf. Here are the configuration values Cinnamon Role expects:

```
[cinnamon]
# Path to the yaml file that contains the list of role
# sets to test policies on. The file follows the following structure:
#     admin:
#       - admin_role_1
#       - admin_role_2
#     regular_user:
#       - regular_user_role
#
# The list under the role set is the list of roles that are assumed to be on a
# user of that type. If pre-provisioned credentials are used, it is assumed that
# users with these exact roles exist. If dynamic credentials are used,
# users will be generated with these roles placed on them.
#role_sets_file = <None>

# Path to the yaml file that contains the list of tests,
# and their expected results. The file follows the following structure:
#     cinnamon_role.tests.scenario.TestGivenScenario.test_given_scenario_1:
#       pass:
#         - admin
#       fail:
#         - regular_user
#
# If any tests are not listed, it is assumed that all users will pass it. If a
# user is not listed under the test, it is assumed that that user will
# pass.
#expected_results_file = <None>
```

### Setting up your environment
Here are the steps needed to setup your Cinnamon Role environment and run Cinnamon Role's tests:

1. Clone Tempest
   - ```git clone http://github.com/openstack/tempest```
2. Clone Cinnamon Role
   - ```git clone https://github.rtp.raleigh.ibm.com/rlrossit-us/cinnamon-role.git```
3. Add ```[cinnamon]``` section to tempest.conf
4. Install the Tempest virtual environment
   - ```python tools/install_venv.py```
5. Install Cinnamon Role within Tempest's virtual environment
   - ```pip install cinnamon-role/```
6. Set up role sets file
   - See [role sets file example](examples/cinnamon-roles.yaml.sample)
7. Set up expected results file
   - See [expected results file example](examples/cinnamon-results.yaml.sample)
8. Do any additional Tempest setup (user/project/network creation)
9. Run Cinnamon Role
   - ```./run_tempest.sh -V cinnamon_role```
10. Bob's your uncle!

## Implementing Tests
In order for Cinnamon Role to run tests, tests need to become a part of Cinnamon Role. Because Tempest already holds a large number of tests, the preferred method of testing will be done by borrowing a Tempest test and running it against each user type. Sometimes there is not a Tempest test to fit the needs, so Cinnamon Role also allows for new tests to be written that borrow from Tempest's rest clients.

### Using existing Tempest tests
Here is an example of using an existing Tempest test for running in Cinnamon Role:
```
from tempest.api.compute.servers import test_server_actions

from cinnamon_role import test


@test.for_each_role_set(__name__)
class ServerActionsTestJSON(test_server_actions.ServerActionsTestJSON):
    @classmethod
    def get_tenant_network(cls, credentials_type='primary'):
        return super(ServerActionsTestJSON, cls).get_tenant_network(
            credentials_type=cls.credentials[0][0])
```
The decorator ```@test.for_each_role_set(__name__)``` is where the magic happens. Cinnamon Role automatically uses this test case to dynamically create test cases for each role set defined in the role sets file. The original test is not run, because the original test is not aware of the role-specified credentials available to it (it has no association with a specific role set).

In most cases, the subclass will just inherit from the Tempest test class with only a ```pass``` body. But, sometimes Tempest performs unwanted operations, so overriding functions is sometimes necessary.

This same example can be found in [this example](examples/test_server_actions.py)

### Writing your own tests
TODO(rlrossit)
