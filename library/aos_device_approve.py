#!/usr/bin/env python
# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

DOCUMENTATION = '''
---
module: aos_device_approve
author: jeremy@apstra.com (@jeremyschulman)
version_added: "2.3"
short_description: Manage AOS collections
description:
  - Used to approve a device that is currently in the "Quarantined" state.
  - Also can be used to assign the location property
requirements:
  - aos-pyez
options:
  session:
    description:
      - An existing AOS session as obtained by aos_login module
    required: true
  name:
    description:
      - The device serial-number; i.e. uniquely identifies the device in the
        AOS system
    required: true
  dest:
    location:
        - User defined location property
    required: false
'''

EXAMPLES = '''
# add an IP address pool to AOS-server

- aos_device_approve:
    session: "{{ aos_session }}"
    name: D2060B2F105429GDABCD123
    location: "rack-45, ru-18"
'''

from ansible.module_utils.basic import AnsibleModule

try:
    from apstra.aosom.session import Session
    from apstra.aosom.exc import SessionError, SessionRqstError, LoginError
    HAS_AOS_PYEZ = True
except ImportError:
    HAS_AOS_PYEZ = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(required=True, type="dict"),
            name=dict(required=True),
            location=dict(default=''))
    )

    if not HAS_AOS_PYEZ:
        module.fail_json(msg='aos-pyez is not installed.  Please see details '
                             'here: https://github.com/Apstra/aos-pyez')

    margs = module.params
    auth = margs['session']

    try:
        aos = Session()
        aos.api.resume(auth['url'], auth['headers'])
    except LoginError:
        module.fail_json(msg="unable to login")

    dev = aos.Devices[margs['name']]
    if not dev.exists:
        module.fail_json(msg="unknown device '%s'" % margs['name'])

    if dev.is_approved:
        module.exit_json(changed=False)

    try:
        dev.approve(location=margs['location'])
        module.exit_json(changed=True)

    except (SessionError, SessionRqstError) as exc:
        module.fail_json(msg="unable to approve device '%s'" % exc.message)


if __name__ == "__main__":
    main()
