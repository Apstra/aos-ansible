from ansible.compat.tests.mock import patch
import library.aos_ip_pool as aos_ip_pool


@patch('library.aos_ip_pool.ip_pool')
@patch('library.aos_ip_pool.AnsibleModule')
def test_module_args(mock_module,
                     mock_aos_ip_pool):
    """
    aos_ip_pool - test module arguments
    """
    aos_ip_pool.main()
    mock_module.assert_called_with(
        argument_spec={
            'session': {'required': True, 'type': 'dict'},
            'name': {'required': False},
            'id': {'required': False},
            'state': {'required': False,
                      'choices': ['present', 'absent'],
                      'default': 'present'},
            'subnets': {'required': False,
                        'type': 'list',
                        'default': []},
            'ip_version': {'required': False,
                           'choices': ['ipv4', 'ipv6'],
                           'default': 'ipv4'}},
        mutually_exclusive=[('name', 'id')],
        required_one_of=[('name', 'id')],
        supports_check_mode=True)


@patch('library.aos_ip_pool.ip_pool')
@patch('library.aos_ip_pool.AnsibleModule')
def test_aos_ip_pool_success(mock_module, mock_aos_ip_pool):
    """
    aos_ip_pool - test module returned data
    """
    mock_session = {"server": "foo",
                    "token": "bar"}

    mock_aos_ip_pool.return_value = mock_session
    resp = aos_ip_pool.ip_pool()
    assert resp == mock_session


class TestIpPoolValidate(object):

    def setup(self):
        self.addr_type = 'ipv4'

    def test_ipv4_validate_valid_subnet_empty(self):

        test_range = []
        assert aos_ip_pool.validate_subnets(test_range,
                                            self.addr_type) == []

    def test_ipv4_validate_valid_subnet(self):

        test_range = ['192.168.59.0/24']
        assert aos_ip_pool.validate_subnets(test_range,
                                            self.addr_type) == []

    def test_ipv4_validate_valid_subnet_multiple(self):

        test_range = ['192.168.59.0/24', '10.10.10.0/23']
        assert aos_ip_pool.validate_subnets(test_range,
                                            self.addr_type) == []

    def test_ipv4_validate_invalid_subnet(self):

        test_range = ['192.168.359.0/24']
        assert aos_ip_pool.validate_subnets(test_range,
                                            self.addr_type) == ['Invalid subnet: '
                                                                '192.168.359.0/24']


class TestIpv6PoolValidate(object):

    def setup(self):
        self.addr_type = 'ipv6'

    def test_ipv6_validate_valid_subnet_empty(self):

        test_range = []
        assert aos_ip_pool.validate_subnets(test_range,
                                            self.addr_type) == []

    def test_ipv6_validate_valid_subnet(self):

        test_range = ['fe80:0:0:1::/64']
        assert aos_ip_pool.validate_subnets(test_range,
                                            self.addr_type) == []

    def test_ipv6_validate_valid_subnet_multiple(self):

        test_range = ['fe80:0:0:1::/64', 'fe80:0:0:3e::/64']
        assert aos_ip_pool.validate_subnets(test_range,
                                            self.addr_type) == []

    def test_ipv6_validate_invalid_subnet(self):

        test_range = ['fe80:0:g:1::/64']
        assert aos_ip_pool.validate_subnets(test_range,
                                            self.addr_type) == ['Invalid subnet: '
                                                                'fe80:0:g:1::/64']


class TestIpGetSubnet(object):

    def test_ip_get_subnet_valid(self):

        test_subnet = [['192.168.59.0/24']]
        assert aos_ip_pool.get_subnets(test_subnet) == [{'network':
                                                        ['192.168.59.0/24']}]

    def test_ip_get_subnet_valid_empty(self):

        test_subnet = []
        assert aos_ip_pool.get_subnets(test_subnet) == []

    def test_ip_get_subnet_valid_multiple(self):

        test_subnet = [['192.168.59.0/24', '10.10.10.0/23']]
        assert aos_ip_pool.get_subnets(test_subnet) == [{'network':
                                                        ['192.168.59.0/24',
                                                         '10.10.10.0/23']}]
