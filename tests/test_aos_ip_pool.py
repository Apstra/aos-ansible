from ansible.compat.tests.mock import patch
from nose.tools import assert_equals
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
                           'type': 'int',
                           'choices': [4, 6],
                           'default': 4}},
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
    assert_equals(resp, mock_session)
