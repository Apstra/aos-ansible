# Copyright (c) 2017 Apstra Inc, <community@apstra.com>

from ansible.compat.tests.mock import patch
import library.aos_asn_pool as aos_asn_pool


@patch('library.aos_asn_pool.asn_pool')
@patch('library.aos_asn_pool.AnsibleModule')
def test_module_args(mock_module,
                     mock_aos_asn_pool):
    """
    aos_asn_pool - test module arguments
    """
    aos_asn_pool.main()
    mock_module.assert_called_with(
        argument_spec={'session': {'required': True, 'type': 'dict'},
                       'name': {'required': False},
                       'id': {'required': False},
                       'state': {'required': False,
                                 'choices': ['present', 'absent'],
                                 'default': 'present'},
                       'ranges': {'required': False,
                                  'type': 'list',
                                  'default': []}},
        mutually_exclusive=[('name', 'id')],
        required_one_of=[('name', 'id')], supports_check_mode=True)


@patch('library.aos_asn_pool.asn_pool')
@patch('library.aos_asn_pool.AnsibleModule')
def test_aos_asn_pool_success(mock_module, mock_aos_asn_pool):
    """
    aos_asn_pool - test module returned data
    """
    mock_session = {"server": "foo",
                    "token": "bar"}

    mock_aos_asn_pool.return_value = mock_session
    resp = aos_asn_pool.asn_pool()
    assert resp == mock_session


class TestAsnPoolValidate(object):

    def test_asn_validate_valid_range(self):

        test_range = [[100, 200]]
        assert aos_asn_pool.validate_ranges(test_range) == []

    def test_asn_validate_valid_range_multiple(self):

        test_range = [[100, 200], [300, 400]]
        assert aos_asn_pool.validate_ranges(test_range) == []

    def test_asn_validate_valid_range_empty(self):

        test_range = []
        assert aos_asn_pool.validate_ranges(test_range) == []

    def test_asn_validate_invalid_type(self):

        test_range = [[100, 'test1']]
        assert aos_asn_pool.validate_ranges(test_range) == ['Invalid range: '
                                                            'Expected integer '
                                                            'values']

    def test_asn_validate_invalid_extra(self):

        test_range = [[100, 200, 300]]
        assert aos_asn_pool.validate_ranges(test_range) == ['Invalid range: '
                                                            'must be a list of '
                                                            '2 members']

    def test_asn_validate_invalid_order(self):

        test_range = [[200, 100]]
        assert aos_asn_pool.validate_ranges(test_range) == ['Invalid range: '
                                                            '2nd element must '
                                                            'be bigger than 1st']


class TestAsnGetRange(object):

    def test_asn_get_range_valid(self):

        test_range = [[100, 200]]
        assert aos_asn_pool.get_ranges(test_range) == [{'first': 100,
                                                        'last': 200}]

    def test_asn_get_range_valid_empty(self):

        test_range = []
        assert aos_asn_pool.get_ranges(test_range) == []

    def test_asn_get_range_valid_multiple(self):

        test_range = [[100, 200], [300, 400]]
        assert aos_asn_pool.get_ranges(test_range) == [{'first': 100,
                                                        'last': 200},
                                                       {'first': 300,
                                                        'last': 400}]
