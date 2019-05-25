import pytest
from library.aos_resource import AsnPool, VniPool, IpPool


class TestAsnPool(object):
    def setup(self):
        module = 'foo'
        session = 'foo'
        check_mode = 'foo'
        self.asn_pool = AsnPool(module, session, check_mode)

    def test_asn_validate_valid_range(self):

        test_range = [[100, 200]]
        assert self.asn_pool.validate(test_range) == []

    def test_asn_validate_valid_range_multiple(self):

        test_range = [[100, 200], [300, 400]]
        assert self.asn_pool.validate(test_range) == []

    def test_asn_validate_valid_range_empty(self):

        test_range = []
        assert self.asn_pool.validate(test_range) == []

    def test_asn_validate_invalid_type(self):

        test_range = [[100, 'test1']]
        assert self.asn_pool.validate(test_range) == ['Invalid range: Expected integer values']

    def test_asn_validate_invalid_extra(self):

        test_range = [[100, 200, 300]]
        assert self.asn_pool.validate(test_range) == ['Invalid range: must be a list of 2 members']

    def test_asn_validate_invalid_order(self):

        test_range = [[200, 100]]
        assert self.asn_pool.validate(test_range) == ['Invalid range: 2nd element must be bigger than 1st']


class TestVniPool(object):
    def setup(self):
        module = 'foo'
        session = 'foo'
        check_mode = 'foo'
        self.vni_pool = VniPool(module, session, check_mode)

    def test_vni_validate_valid_range(self):

        test_range = [[4096, 4200]]
        assert self.vni_pool.validate(test_range) == []

    def test_vni_validate_valid_range_multiple(self):

        test_range = [[4096, 4200], [4300, 4400]]
        assert self.vni_pool.validate(test_range) == []

    def test_vni_validate_valid_range_empty(self):

        test_range = []
        assert self.vni_pool.validate(test_range) == []

    def test_vni_validate_invalid_type(self):

        test_range = [[4200, 'test1']]
        assert self.vni_pool.validate(test_range) == ['Invalid range: Expected integer values']

    def test_vni_validate_invalid_extra(self):

        test_range = [[4200, 4096, 4400]]
        assert self.vni_pool.validate(test_range) == ['Invalid range: must be a list of 2 members']

    def test_vni_validate_invalid_order(self):

        test_range = [[4200, 4096]]
        assert self.vni_pool.validate(test_range) == ['Invalid range: 2nd element must be bigger than 1st']

    def test_vni_validate_invalid_range(self):

        test_range = [[111, 222]]
        assert self.vni_pool.validate(test_range) == ['Invalid range: must be a valid range between 4096 and 16777214']


class TestIpv4Pool(object):
    def setup(self):
        module = 'foo'
        session = 'foo'
        check_mode = 'foo'
        addr_type = 4
        self.ip_pool = IpPool(module, session, addr_type, check_mode)

    def test_ipv4_validate_valid_subnet_empty(self):

        test_range = []
        assert self.ip_pool.validate(test_range) == []

    def test_ipv4_validate_valid_subnet(self):

        test_range = ['192.168.59.0/24']
        assert self.ip_pool.validate(test_range) == []

    def test_ipv4_validate_valid_subnet_multiple(self):

        test_range = ['192.168.59.0/24', '10.10.10.0/23']
        assert self.ip_pool.validate(test_range) == []

    def test_ipv4_validate_invalid_subnet(self):

        test_range = ['192.168.359.0/24']
        assert self.ip_pool.validate(test_range) == ['Invalid subnet: 192.168.359.0/24']


class TestIpv6Pool(object):
    def setup(self):
        module = 'foo'
        session = 'foo'
        check_mode = 'foo'
        addr_type = 6
        self.ip_pool = IpPool(module, session, addr_type, check_mode)

    def test_ipv6_validate_valid_subnet_empty(self):

        test_range = []
        assert self.ip_pool.validate(test_range) == []

    def test_ipv6_validate_valid_subnet(self):

        test_range = ['fe80:0:0:1::/64']
        assert self.ip_pool.validate(test_range) == []

    def test_ipv6_validate_valid_subnet_multiple(self):

        test_range = ['fe80:0:0:1::/64', 'fe80:0:0:3e::/64']
        assert self.ip_pool.validate(test_range) == []

    def test_ipv6_validate_invalid_subnet(self):

        test_range = ['fe80:0:g:1::/64']
        assert self.ip_pool.validate(test_range) == ['Invalid subnet: fe80:0:g:1::/64']