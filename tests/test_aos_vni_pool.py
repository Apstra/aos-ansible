from ansible.compat.tests.mock import patch
import library.aos_vni_pool as aos_vni_pool


@patch('library.aos_vni_pool.vni_pool')
@patch('library.aos_vni_pool.AnsibleModule')
def test_module_args(mock_module,
                     mock_aos_vni_pool):
    """
    aos_vni_pool - test module arguments
    """
    aos_vni_pool.main()
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


@patch('library.aos_vni_pool.vni_pool')
@patch('library.aos_vni_pool.AnsibleModule')
def test_aos_vni_pool_success(mock_module, mock_aos_vni_pool):
    """
    aos_vni_pool - test module returned data
    """
    mock_session = {"server": "foo",
                    "token": "bar"}

    mock_aos_vni_pool.return_value = mock_session
    resp = aos_vni_pool.vni_pool()
    assert resp == mock_session


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
