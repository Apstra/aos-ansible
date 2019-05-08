from ansible.compat.tests.mock import patch
from nose.tools import assert_equals
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
    assert_equals(resp, mock_session)
