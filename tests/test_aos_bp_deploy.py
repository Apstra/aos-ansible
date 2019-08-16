# Copyright (c) 2017 Apstra Inc, <community@apstra.com>

import mock
import library.aos_bp_deploy as aos_bp_deploy


@mock.patch('library.aos_bp_deploy.aos_bp_deploy')
@mock.patch('library.aos_bp_deploy.AnsibleModule')
def test_module_args(mock_module,
                     mock_aos_bp_deploy):
    """
    aos_bp_deploy - test module arguments
    """
    aos_bp_deploy.main()
    mock_module.assert_called_with(
        argument_spec={
            'session': {'required': True, 'type': 'dict'},
            'name': {'required': False},
            'id': {'required': False}
        },
        mutually_exclusive=[('name', 'id')],
        required_one_of=[('name', 'id')],
        supports_check_mode=False)
