from ansible.compat.tests.mock import patch
import library.aos_login as aos_login


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json
    and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json
    and caught by the test case"""
    pass


@patch('library.aos_login.aos_login')
@patch('library.aos_login.AnsibleModule')
def test_module_args(mock_module, mock_aos_login):
    """
    aos_login - test module arguments
    """
    aos_login.main()
    mock_module.assert_called_with(
        argument_spec={
            'server': {'required': True},
            'port': {'default': '443', 'type': 'int'},
            'user': {'default': 'admin'},
            'passwd': {'default': 'admin', 'no_log': True}})


@patch('library.aos_login.aos_login')
@patch('library.aos_login.AnsibleModule')
def test_aos_login_success(mock_module, mock_aos_login):
    """
    aos_login - test module returned data
    """
    mock_session = {"server": "foo",
                    "token": "bar"}

    mock_aos_login.return_value = mock_session
    resp = aos_login.aos_login()
    assert resp == mock_session
