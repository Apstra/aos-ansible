#!/usr/bin/env python
# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

DOCUMENTATION = '''
---
module: aos_collection
author: jeremy@apstra.com (@jeremyschulman)
version_added: "2.3"
short_description: Manage AOS collections
description:
  - Used to add a collection item to AOS-server from a JSON file
  - Used to backup a collection item to JSON file
requirements:
  - aos-pyez
options:
  session:
    description:
      - An existing AOS session as obtained by aos_login module
    required: true
  collection:
    description:
      - A specific collection name.  The list of available collection
        names depends on the AOS version.  See aos-pyez documentation for details.
    required: true
  src:
    description:
      - filepath to JSON file containing the collection item data
    required: false
  name:
    description:
      - collection item name, used in conjunction with the dest parameter
    required: false
  dest:
    description:
        - filepath to JSON file that will store the collection item data
    required: false
'''

EXAMPLES = '''
# add an IP address pool to AOS-server

- aos_collection:
    session: "{{ aos_session }}"
    collection: IpPools
    src: resources/ip-pools/dc1_switches.json

# backup an IP address from AOS-server to local file

- aos_collection:
    session: "{{ aos_session }}"
    collection: IpPools
    name: Switches-IpAddrs
    dest: resources/ip-pools/dc1_switches.json
'''

RETURNS = '''
item_name:
  description: user-name given to item
  retured: always
  type: str
  sample: Server-IpAddrs

item_id:
  description: AOS unique ID assigned to item
  returned: always
  type: str
  sample: fcc4ac1c-e249-4fe7-b458-2138bfb44c06
'''

import json

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
        module.fail_json(msg="unknown device '%s'" %margs['name'])

    if dev.is_approved:
        module.exit_json(changed=False)

    try:
        dev.approve(location=margs['location'])
        module.exit_json(changed=True)

    except (SessionError, SessionRqstError) as exc:
        module.fail_json(msg="unable to approve device '%s'" % exc.message)


if __name__ == "__main__":
    main()
