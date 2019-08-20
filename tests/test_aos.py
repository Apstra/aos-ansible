# Copyright (c) 2017 Apstra Inc, <community@apstra.com>

import os
import json
import pytest
from mock import patch
from library.aos import validate_vlan_id, validate_ip_format, validate_vni_ranges, \
    validate_asn_ranges, validate_vni_id, find_bp_system_nodes


def read_fixture(name):
    with open(os.path.join("tests/fixtures", name)) as f:
        return f.read()


def deserialize_fixture(name):
    return json.loads(read_fixture(name))


class TestVlanValidate(object):

    def test_vlan_validate_valid_id_high(self):

        test_id = 4094
        assert validate_vlan_id(test_id) == []

    def test_vlan_validate_valid_id_low(self):

        test_id = 1
        assert validate_vlan_id(test_id) == []

    def test_vlan_validate_invalid_id_low(self):

        test_id = 0
        assert validate_vlan_id(test_id) == ['Invalid ID: must be a '
                                             'valid vlan id between 1 '
                                             'and 4094']

    def test_vlan_validate_invalid_id_high(self):

        test_id = 4095
        assert validate_vlan_id(test_id) == ['Invalid ID: must be a '
                                             'valid vlan id between 1 '
                                             'and 4094']


class TestAsnPoolValidate(object):
    def test_asn_validate_valid_range(self):

        test_range = [[100, 200]]
        assert validate_asn_ranges(test_range) == []

    def test_asn_validate_valid_range_multiple(self):

        test_range = [[100, 200], [300, 400]]
        assert validate_asn_ranges(test_range) == []

    def test_asn_validate_valid_range_empty(self):

        test_range = []
        assert validate_asn_ranges(test_range) == []

    def test_asn_validate_invalid_type(self):

        test_range = [[100, 'test1']]
        assert validate_asn_ranges(test_range) == ['Invalid range: '
                                                   'Expected integer '
                                                   'values']

    def test_asn_validate_invalid_extra(self):

        test_range = [[100, 200, 300]]
        assert validate_asn_ranges(test_range) == ['Invalid range: '
                                                   'must be a list of '
                                                   '2 members']

    def test_asn_validate_invalid_order(self):

        test_range = [[200, 100]]
        assert validate_asn_ranges(test_range) == ['Invalid range: '
                                                   '2nd element must '
                                                   'be bigger than 1st']

    def test_asn_validate_invalid_out_of_range_low(self):

        test_range = [[0, 100]]
        assert validate_asn_ranges(test_range) == ['Invalid range: must be '
                                                   'a valid range between 1 '
                                                   'and 4294967295']

    def test_asn_validate_invalid_out_of_range_high(self):

        test_range = [[100, 4294967296]]
        assert validate_asn_ranges(test_range) == ['Invalid range: must be '
                                                   'a valid range between 1 '
                                                   'and 4294967295']


class TestVniPoolValidate(object):

    def test_vni_validate_valid_range(self):

        test_range = [[4096, 4200]]
        assert validate_vni_ranges(test_range) == []

    def test_vni_validate_valid_range_multiple(self):

        test_range = [[4096, 4200], [4300, 4400]]
        assert validate_vni_ranges(test_range) == []

    def test_vni_validate_valid_range_empty(self):

        test_range = []
        assert validate_vni_ranges(test_range) == []

    def test_vni_validate_invalid_type(self):

        test_range = [[4200, 'test1']]
        assert validate_vni_ranges(test_range) == ['Invalid range: '
                                                   'Expected integer '
                                                   'values']

    def test_vni_validate_invalid_extra(self):

        test_range = [[4200, 4096, 4400]]
        assert validate_vni_ranges(test_range) == ['Invalid range: '
                                                   'must be a list of '
                                                   '2 members']

    def test_vni_validate_invalid_order(self):

        test_range = [[4200, 4096]]
        assert validate_vni_ranges(test_range) == ['Invalid range: '
                                                   '2nd element must be '
                                                   'bigger than 1st']

    def test_vni_validate_invalid_range(self):

        test_range = [[111, 222]]
        assert validate_vni_ranges(test_range) == ['Invalid range: '
                                                   'must be a valid range '
                                                   'between 4096 and '
                                                   '16777214']


class TestVniIdValidate(object):

    def test_vni_validate_id(self):

        test_id = 4096
        assert validate_vni_id(test_id) == []

    def test_vni_validate_id_invalid_low(self):
        test_id = 4095
        assert validate_vni_id(test_id) == ["Invalid ID: must be a valid VNI "
                                            "number between 4096 and 16777214"]

    def test_vni_validate_id_invalid_high(self):
        test_id = 16777215
        assert validate_vni_id(test_id) == ["Invalid ID: must be a valid VNI "
                                            "number between 4096 and 16777214"]


ADDR_TYPE_V4 = 'ipv4'
ADDR_TYPE_V6 = 'ipv6'


class TestIpPoolValidate(object):

    def test_ipv4_validate_valid_subnet_empty(self):

        test_range = []
        assert validate_ip_format(test_range,
                                  ADDR_TYPE_V4) == []

    def test_ipv4_validate_valid_subnet(self):

        test_range = ['192.168.59.0/24']
        assert validate_ip_format(test_range,
                                  ADDR_TYPE_V4) == []

    def test_ipv4_validate_valid_subnet_multiple(self):

        test_range = ['192.168.59.0/24', '10.10.10.0/23']
        assert validate_ip_format(test_range,
                                  ADDR_TYPE_V4) == []

    def test_ipv4_validate_invalid_subnet(self):

        test_range = ['192.168.359.0/24']
        assert validate_ip_format(test_range,
                                  ADDR_TYPE_V4) == ["Invalid format: "
                                                    "['192.168.359.0/24']"]

    def test_ipv4_validate_invalid_ip_version(self):

        test_range = ['192.168.359.0/24']
        bad_addr_type = 'ipv5'
        with pytest.raises(AssertionError) as e:
            validate_ip_format(test_range, bad_addr_type)

        assert "Invalid IP version: ipv5" in str(e.value)


class TestIpv6PoolValidate(object):

    def test_ipv6_validate_valid_subnet_empty(self):

        test_range = []
        assert validate_ip_format(test_range,
                                  ADDR_TYPE_V6) == []

    def test_ipv6_validate_valid_subnet(self):

        test_range = ['fe80:0:0:1::/64']
        assert validate_ip_format(test_range,
                                  ADDR_TYPE_V6) == []

    def test_ipv6_validate_valid_subnet_multiple(self):

        test_range = ['fe80:0:0:1::/64', 'fe80:0:0:3e::/64']
        assert validate_ip_format(test_range,
                                  ADDR_TYPE_V6) == []

    def test_ipv6_validate_invalid_subnet(self):

        test_range = ['fe80:0:g:1::/64']
        assert validate_ip_format(test_range,
                                  ADDR_TYPE_V6) == ["Invalid format: "
                                                    "['fe80:0:g:1::/64']"]


class TestFindBpSystemNodes:

    @patch('library.aos.aos_post')
    def test_find_system_node_id_valid(self, mock_post):

        mock_return = deserialize_fixture('bp_system_nodes_ql.json')

        mock_post.return_value = mock_return
        test_session = 'test'
        test_nodes = ['spine1']
        test_bp = 'testbpid'

        return_node = find_bp_system_nodes(test_session, test_bp, nodes=test_nodes)
        assert return_node[0]['id'] == '06b3424a-6f6a-422f-b6fa-a340f117981a'

    @patch('library.aos.aos_post')
    def test_find_system_node_id_valid_multiple(self, mock_post):

        mock_return = deserialize_fixture('bp_system_nodes_ql.json')

        mock_post.return_value = mock_return
        test_session = 'test'
        test_nodes = ['spine1', 'spine2']
        test_bp = 'testbpid'

        expected = [
            {
                'id': 'e0fc723a-114d-4080-89ab-789d7da6c0eb',
                'label': 'spine2',
                'role': 'spine'
            },
            {
                'id': '06b3424a-6f6a-422f-b6fa-a340f117981a',
                'label': 'spine1',
                'role': 'spine'
            }
        ]

        return_node = find_bp_system_nodes(test_session, test_bp, nodes=test_nodes)
        assert return_node == expected

    @patch('library.aos.aos_post')
    def test_find_system_node_id_invalid(self, mock_post):
        mock_return = deserialize_fixture('bp_system_nodes_ql.json')

        mock_post.return_value = mock_return
        test_session = 'test'
        test_nodes = ['bad_name']
        test_bp = 'testbpid'

        return_node = find_bp_system_nodes(test_session, test_bp, nodes=test_nodes)
        assert return_node == []

    @patch('library.aos.aos_post')
    def test_find_system_node_id_all(self, mock_post):
        mock_return = deserialize_fixture('bp_system_nodes_ql.json')

        mock_post.return_value = mock_return
        test_session = 'test'
        test_bp = 'testbpid'

        return_node = find_bp_system_nodes(test_session, test_bp)
        assert return_node == mock_return['data']['system_nodes']

    @patch('library.aos.aos_post')
    def test_find_system_node_id_blank_nodes(self, mock_post):
        mock_return = deserialize_fixture('bp_system_nodes_ql.json')

        mock_post.return_value = mock_return
        test_session = 'test'
        test_nodes = []
        test_bp = 'testbpid'

        return_node = find_bp_system_nodes(test_session, test_bp, nodes=test_nodes)
        assert return_node == mock_return['data']['system_nodes']
