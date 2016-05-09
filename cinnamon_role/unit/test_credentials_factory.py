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

import mock
from tempest.common import credentials_factory as t_creds

from cinnamon_role import credentials_factory as creds
from cinnamon_role import preprov_creds as ppc
from cinnamon_role.unit import base


class TestCredentialsFactory(base.BaseTestCase):
    @mock.patch.object(creds, '_get_credentials_provider')
    @mock.patch.object(creds, '_are_roles_available')
    @mock.patch.object(creds, '_get_client_manager')
    def test_with_role_matching_credentials(self, mock_gcm, mock_ara,
                                            mock_gcp):
        with mock.patch('cinnamon_role.credentials_factory.classmethod') as cm:
            cm.side_effect = lambda x: x
            new_cls = creds.with_role_matching_credentials(mock.Mock())

        self.assertEqual(new_cls._get_credentials_provider, mock_gcp)
        self.assertEqual(new_cls.are_roles_available, mock_ara)
        self.assertEqual(new_cls.get_client_manager, mock_gcm)

    @mock.patch.object(creds, 'get_credentials_provider')
    def test_get_credentials_provider(self, mock_gcp):
        cls = mock.Mock()
        del cls.force_tenant_isolation
        del cls._creds_provider

        self._do_creds_provider_test(cls, mock_gcp)

    @mock.patch.object(creds, 'get_credentials_provider')
    def test_get_credentials_provider_with_tenant_iso(self, mock_gcp):
        cls = mock.Mock()

        self._do_creds_provider_test(cls, mock_gcp, tenant_iso=True)

    @mock.patch.object(creds, 'get_credentials_provider')
    def test_get_credentials_provider_none_creds_provider(self, mock_gcp):
        cls = mock.Mock()
        del cls.force_tenant_isolation
        cls._creds_provider = None

        self._do_creds_provider_test(cls, mock_gcp)

    @mock.patch.object(creds, 'get_credentials_provider')
    def test_get_credentials_provider_with_different_name(self, mock_gcp):
        cls = mock.Mock()
        del cls.force_tenant_isolation
        cls._creds_provider.__name__ = 'notfoo'

        self._do_creds_provider_test(cls, mock_gcp)

    @mock.patch.object(creds, 'get_credentials_provider')
    def test_get_credentials_already_has_provider(self, mock_gcp):
        cls = mock.Mock()
        cls.__name__ = 'foo'
        mock_prov = mock.Mock()
        mock_prov.name = cls.__name__
        cls._creds_provider = mock_prov

        prov = creds._get_credentials_provider(cls)

        self.assertEqual(mock_prov, prov)
        mock_gcp.assert_not_called()

    def test_are_roles_available(self):
        cls = mock.Mock()
        mock_prov = mock.Mock()
        mock_prov.are_roles_available.return_value = False
        cls._get_credentials_provider.return_value = mock_prov
        roles = ['foo', 'bar']

        are_avail = creds._are_roles_available(cls, roles)

        self.assertFalse(are_avail)
        mock_prov.are_roles_available.assert_called_once_with(roles)

    def test_are_roles_available_not_on_cred_provider(self):
        cls = mock.Mock()
        mock_prov = mock.Mock()
        del mock_prov.are_roles_available
        cls._get_credentials_provider.return_value = mock_prov
        roles = ['foo', 'bar']

        are_avail = creds._are_roles_available(cls, roles)

        self.assertTrue(are_avail)

    def test_get_client_manager(self):
        cls = mock.Mock()
        cls.are_roles_available.return_value = True

        self._do_client_manager_test(cls, roles=['foo', 'bar'])
        cls.are_roles_available.assert_called_once_with(['foo', 'bar'])

    def test_get_client_manager_without_roles(self):
        self._do_client_manager_test(mock.Mock())

    def test_get_client_manager_raises_skip(self):
        cls = mock.Mock()
        cls.__name__ = 'foo'
        cls.are_roles_available.return_value = False

        class MyException(Exception):
            pass

        cls.skipException = MyException

        self.assertRaises(MyException, creds._get_client_manager,
                          cls, roles=['foo'])

    @mock.patch.object(t_creds, 'get_credentials_provider')
    @mock.patch.object(t_creds, '_get_preprov_provider_params')
    @mock.patch.object(creds, 'CONF')
    def test_public_get_credentials_provider(self, mock_conf,
                                             mock_params, mock_gcp):
        cls_name = 'ExactRoleMatchingPreProvisionedCredentialProvider'
        mock_conf.auth.test_accounts_file = 'foo.yaml'
        name = 'foo'
        params = {'foo': 'bar'}
        mock_params.return_value = params

        kwargs = {'network_resources': ['net1', 'net2'],
                  'force_tenant_isolation': False, 'identity_version': 'v3'}

        with mock.patch.object(ppc, cls_name) as mock_creds:
            mock_provider = mock.Mock()
            mock_creds.return_value = mock_provider
            prov = creds.get_credentials_provider(name, **kwargs)

        self.assertEqual(mock_provider, prov)
        mock_gcp.assert_called_once_with(name, **kwargs)
        mock_params.assert_called_once_with()
        kwargs.update(params)
        del kwargs['force_tenant_isolation']
        del kwargs['network_resources']
        mock_creds.assert_called_once_with(name=name, **kwargs)

    @mock.patch.object(t_creds, 'get_credentials_provider')
    @mock.patch.object(creds, 'CONF')
    def test_get_credentials_provider_no_accounts_file(self, mock_conf,
                                                       mock_gcp):
        mock_conf.auth.test_accounts_file = None
        mock_prov = mock.Mock()
        mock_gcp.return_value = mock_prov

        name = 'foo'
        kwargs = {'network_resources': ['net1', 'net2'],
                  'force_tenant_isolation': True, 'identity_version': 'v3'}

        prov = creds.get_credentials_provider(name, **kwargs)

        self.assertEqual(mock_prov, prov)
        mock_gcp.assert_called_once_with(name, **kwargs)

    def _do_creds_provider_test(self, mock_cls, mock_get, tenant_iso=False):
        mock_cls.__name__ = 'foo'
        mock_cls.network_resources = ['net1', 'net2']
        mock_cls.get_identity_version = mock.Mock()
        mock_cls.get_identity_version.return_value = 'v3'
        mock_cls.force_tenant_isolation = tenant_iso
        mock_prov = mock.Mock()
        mock_get.return_value = mock_prov

        provider = creds._get_credentials_provider(mock_cls)

        self.assertEqual(provider, mock_prov)
        self.assertEqual(provider, mock_cls._creds_provider)
        mock_get.assert_called_once_with(
            name=mock_cls.__name__,
            network_resources=mock_cls.network_resources,
            force_tenant_isolation=tenant_iso,
            identity_version=mock_cls.get_identity_version())

    def _do_client_manager_test(self, cls, roles=None):
        mock_gcm = mock.Mock()
        mock_man = mock.Mock()
        mock_gcm.return_value = mock_man
        my_super = mock.Mock()
        my_super.get_client_manager = mock_gcm

        with mock.patch('cinnamon_role.credentials_factory.super') as mock_sup:
            mock_sup.return_value = my_super
            cm = creds._get_client_manager(cls, credential_type='foo',
                                           roles=roles, force_new=True)

        self.assertEqual(mock_man, cm)
        mock_gcm.assert_called_once_with(credential_type='foo', roles=roles,
                                         force_new=True)
