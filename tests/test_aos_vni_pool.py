# Copyright (c) 2017 Apstra Inc, <community@apstra.com>

import library.aos_vni_pool as aos_vni_pool


class TestVniPoolValidate(object):

    def test_vni_validate_valid_range(self):

        test_range = [[4096, 4200]]
        assert aos_vni_pool.validate_ranges(test_range) == []

    def test_vni_validate_valid_range_multiple(self):

        test_range = [[4096, 4200], [4300, 4400]]
        assert aos_vni_pool.validate_ranges(test_range) == []

    def test_vni_validate_valid_range_empty(self):

        test_range = []
        assert aos_vni_pool.validate_ranges(test_range) == []

    def test_vni_validate_invalid_type(self):

        test_range = [[4200, 'test1']]
        assert aos_vni_pool.validate_ranges(test_range) == ['Invalid range: '
                                                            'Expected integer '
                                                            'values']

    def test_vni_validate_invalid_extra(self):

        test_range = [[4200, 4096, 4400]]
        assert aos_vni_pool.validate_ranges(test_range) == ['Invalid range: '
                                                            'must be a list of '
                                                            '2 members']

    def test_vni_validate_invalid_order(self):

        test_range = [[4200, 4096]]
        assert aos_vni_pool.validate_ranges(test_range) == ['Invalid range: '
                                                            '2nd element must be '
                                                            'bigger than 1st']

    def test_vni_validate_invalid_range(self):

        test_range = [[111, 222]]
        assert aos_vni_pool.validate_ranges(test_range) == ['Invalid range: '
                                                            'must be a valid range '
                                                            'between 4096 and '
                                                            '16777214']


class TestVniGetRange(object):

    def test_vni_get_range_valid(self):

        test_range = [[4096, 4200]]
        assert aos_vni_pool.get_ranges(test_range) == [{'first': 4096,
                                                        'last': 4200}]

    def test_vni_get_range_valid_empty(self):

        test_range = []
        assert aos_vni_pool.get_ranges(test_range) == []

    def test_vni_get_range_valid_multiple(self):

        test_range = [[4096, 4200], [4396, 4500]]
        assert aos_vni_pool.get_ranges(test_range) == [{'first': 4096,
                                                        'last': 4200},
                                                       {'first': 4396,
                                                        'last': 4500}]
