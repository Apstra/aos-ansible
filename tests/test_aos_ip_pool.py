# Copyright (c) 2017 Apstra Inc, <community@apstra.com>

import library.aos_ip_pool as aos_ip_pool


ADDR_TYPE_V4 = 'ipv4'
ADDR_TYPE_V6 = 'ipv6'


class TestIpPoolValidate(object):

    def test_ipv4_validate_valid_subnet_empty(self):

        test_range = []
        assert aos_ip_pool.validate_subnets(test_range,
                                            ADDR_TYPE_V4) == []

    def test_ipv4_validate_valid_subnet(self):

        test_range = ['192.168.59.0/24']
        assert aos_ip_pool.validate_subnets(test_range,
                                            ADDR_TYPE_V4) == []

    def test_ipv4_validate_valid_subnet_multiple(self):

        test_range = ['192.168.59.0/24', '10.10.10.0/23']
        assert aos_ip_pool.validate_subnets(test_range,
                                            ADDR_TYPE_V4) == []

    def test_ipv4_validate_invalid_subnet(self):

        test_range = ['192.168.359.0/24']
        assert aos_ip_pool.validate_subnets(test_range,
                                            ADDR_TYPE_V4) == ['Invalid subnet: '
                                                              '192.168.359.0/24']


class TestIpv6PoolValidate(object):

    def test_ipv6_validate_valid_subnet_empty(self):

        test_range = []
        assert aos_ip_pool.validate_subnets(test_range,
                                            ADDR_TYPE_V6) == []

    def test_ipv6_validate_valid_subnet(self):

        test_range = ['fe80:0:0:1::/64']
        assert aos_ip_pool.validate_subnets(test_range,
                                            ADDR_TYPE_V6) == []

    def test_ipv6_validate_valid_subnet_multiple(self):

        test_range = ['fe80:0:0:1::/64', 'fe80:0:0:3e::/64']
        assert aos_ip_pool.validate_subnets(test_range,
                                            ADDR_TYPE_V6) == []

    def test_ipv6_validate_invalid_subnet(self):

        test_range = ['fe80:0:g:1::/64']
        assert aos_ip_pool.validate_subnets(test_range,
                                            ADDR_TYPE_V6) == ['Invalid subnet: '
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
