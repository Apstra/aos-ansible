#!/usr/bin/env python
# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

DOCUMENTATION = '''
---
module: aos_blueprint_param
author: jeremy@apstra.com (@jeremyschulman)
version_added: "2.3"
short_description: Manage AOS blueprint parameter values
description:
requirements:
  - aos-pyez
options:
  session:
    description:
      - An existing AOS session as obtained by aos_login module
    required: true
  blueprint_name:
    description:
      - Blueprint user-defined name
    required: true
  param_name:
    description:
      - Name of blueprint parameter, as defined by AOS design template
    required: true
  param_value:
    description:
      - blueprint parameter value.  This value may be transformed by using the
        param_map field; used when the caller provides a user-defined item-name
        and the blueprint param requires an AOS unique ID value.
    required: true
  param_map:
    description:
      - defines the aos-pyez collection that will is used to map the user-defined
        item name into the AOS unique ID value.  For example, if the caller
        provides an IP address pool (param_value) called "Server-IpAddrs", then
        the aos-pyez collection is 'IpPools'.
    required: false
'''

import json

from ansible.module_utils.basic import AnsibleModule

try:
    from apstra.aosom.session import Session
    from apstra.aosom.exc import LoginError, SessionError
    from apstra.aosom.collection_mapper import CollectionMapper, MultiCollectionMapper
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
    aos, blueprint, param = [None] * 3

    try:
        aos = Session()
        aos.session = margs['session']
    except LoginError as exc:
        module.fail_json(msg='unable to login to AOS API: %s' % str(exc))

    try:
        blueprint = aos.Blueprints[margs['blueprint_name']]

        if not blueprint.exists:
            module.fail_json(msg='blueprint %s does not exist.\n'
                                 'known blueprints are [%s]'%
                                 (margs['blueprint_name'],
                                  ','.join(aos.Blueprints.names)))

        param = blueprint.params[margs['param_name']]

    except SessionError as exc:
        module.fail_json(msg='unable to access param %s: %s' %
                             (margs['param_name'], str(exc)))

    changed = False

    try:
        param_value = margs['param_value']
        param_map = margs['param_map']
        param_map = json.loads(param_map)

        if param_map:
            if isinstance(param_map, dict):
                xf = MultiCollectionMapper(aos, param_map)
            else:
                xf = CollectionMapper(getattr(aos, param_map))
            param_value = xf.from_label(param_value)

        if param.value != param_value:
            param.value = param_value
            changed = True

    except SessionError as exc:
        module.fail_json(msg='unable to write to param {}: data={}\nexc={}'.format(
            margs['param_name'], json.dumps(param.value, indent=2), str(exc)))

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
