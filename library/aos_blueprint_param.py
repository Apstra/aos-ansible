#!/usr/bin/env python
# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import json

from ansible.module_utils.basic import AnsibleModule

try:
    from apstra.aosom.session import Session
    from apstra.aosom.exc import LoginError, SessionError
    from apstra.aosom.collection import CollectionValueTransformer
    from apstra.aosom.collection import CollectionValueMultiTransformer
    HAS_AOS_PYEZ = True
except ImportError:
    HAS_AOS_PYEZ = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(required=True, type="dict"),
            blueprint_name=dict(required=True),
            param_name=dict(required=True),
            param_map=dict(required=False, default="null"),
            param_value=dict(required=True, type="dict"),
            state=dict(choices=['present', 'absent', 'merged'], default='present'))
    )

    if not HAS_AOS_PYEZ:
        module.fail_json(msg='aos-pyez is not installed.  Please see details '
                             'here: https://github.com/Apstra/aos-pyez')

    margs = module.params
    auth = margs['session']
    aos, blueprint, param = [None] * 3

    try:
        aos = Session()
        aos.api.resume(url=auth['url'], headers=auth['headers'])
    except LoginError as exc:
        module.fail_json(msg='unable to login to AOS API: %s' % str(exc))

    try:
        blueprint = aos.Blueprints[margs['blueprint_name']]
        param = blueprint.params[margs['param_name']]
    except SessionError as exc:
        module.fail_json(msg='unable to access param %s: %s' %
                             (margs['param_name'], str(exc)))

    try:
        param_value = margs['param_value']
        param_map = margs['param_map']
        param_map = json.loads(param_map)

        if param_map:
            if isinstance(param_map, dict):
                xf = CollectionValueMultiTransformer(aos, param_map)
            else:
                xf = CollectionValueTransformer(getattr(aos, param_map))
            param_value = xf.xf_out(param_value)

        param.value = param_value

    except SessionError as exc:
        module.fail_json(msg='unable to write to param %s: %s' %
                             (margs['param_name'], str(exc)))

    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
