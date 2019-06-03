# Copyright (c) 2017 Apstra Inc, <community@apstra.com>

import mock
import library.aos_blueprint_deploy as aos_blueprint_deploy


@mock.patch('library.aos_blueprint_deploy.aos_blueprint_deploy')
@mock.patch('library.aos_blueprint_deploy.AnsibleModule')
def test_module_args(mock_module,
                     mock_aos_blueprint_deploy):
    """
    aos_blueprint_deploy - test module arguments
    """
    aos_blueprint_deploy.main()
    mock_module.assert_called_with(
        argument_spec={
            'session': {'required': True, 'type': 'dict'},
            'name': {'required': False},
            'id': {'required': False}
        },
        mutually_exclusive=[('name', 'id')],
        required_one_of=[('name', 'id')],
        supports_check_mode=False)
