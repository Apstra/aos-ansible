#!/usr/bin/env python
# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula


import os
import json

from ansible.module_utils.basic import AnsibleModule

try:
    from apstra.aosom.session import Session
    from apstra.aosom.exc import LoginError, SessionRqstError
    HAS_AOS_PYEZ = True
except ImportError:
    HAS_AOS_PYEZ = False


def ensure_present(module, blueprint):
    src_file = module.params['src']

    # TODO: use the built-in ansible module mech for this
    # ...
    if not src_file:
        module.fail_json(msg="'src' parameter required")

    try:
        datum = json.load(open(src_file))
    except Exception as exc:
        module.fail_json(msg="unable to load src file '%s': %s" %
                             (src_file, exc.message))

    name = datum['display_name']

    this_vnet = blueprint.VirtualNetworks[name]
    if this_vnet.exists:
        # TODO - it's possible that the user is providing new
        # vnet data, but here we are ignoring it.  need to handle
        # this use-case better
        module.exit_json(changed=False, contents=this_vnet.value)

    try:
        this_vnet.create(datum)
    except SessionRqstError as exc:
        module.fail_json(msg="umable to create virtual-network '%s': '%s'" %
                             (name, exc.message))

    module.exit_json(changed=True, contents=this_vnet.read())


def ensure_absent(module, blueprint):
    pass


def main():
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(required=True, type="dict"),
            blueprint_name=dict(required=True),
            src=dict(required=False),
            state=dict(choices=['present', 'absent'], default='present'))
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

    blueprint = aos.Blueprints[margs['blueprint_name']]

    if not blueprint.exists:
        module.fail_json(msg='blueprint %s does not exist.\n'
                             'known blueprints are [%s]'%
                             (margs['blueprint_name'],
                              ','.join(aos.Blueprints.names)))



    {
        'present': ensure_present,
        'absent': ensure_absent

    }[margs['state']](module, blueprint)


if __name__ == '__main__':
    main()
