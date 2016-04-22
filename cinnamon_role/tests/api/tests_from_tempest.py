from oslo_log import log as logging

from cinnamon_role import module_magic
from cinnamon_role import test

LOG = logging.getLogger(__name__)

for cls in module_magic.get_all_tempest_api_tests():
    test.for_each_role_set(cls, test_module=__name__)
