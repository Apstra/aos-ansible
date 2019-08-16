# Copyright (c) 2017 Apstra Inc, <community@apstra.com>

import library.aos_bp_security_zone as aos_sec_zone


class TestSzVniValidate(object):

    def test_vni_validate_valid_id(self):

        test_id = 4096
        assert aos_sec_zone.validate_vni_id(test_id) == []

    def test_vni_validate_invalid_range(self):

        test_id = 333
        assert aos_sec_zone.validate_vni_id(test_id) == ['Invalid ID: '
                                                         'must be a valid VNI '
                                                         'number between 4096 '
                                                         'and 16777214']


class TestSzVlanValidate(object):

    def test_vlan_validate_valid_id(self):

        test_id = 4094
        assert aos_sec_zone.validate_vlan_id(test_id) == []

    def test_vlan_validate_invalid_range(self):

        test_id = 4096
        assert aos_sec_zone.validate_vlan_id(test_id) == ['Invalid ID: must be a '
                                                          'valid vlan id between 1 '
                                                          'and 4094']
