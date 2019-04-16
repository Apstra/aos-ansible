from ansible.compat.tests.mock import patch
from ansible.module_utils import basic
from nose.tools import assert_equals
from nose.tools import assert_equals
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
    assert_equals(resp, mock_session)
