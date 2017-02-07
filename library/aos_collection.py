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
    from apstra.aosom.exc import SessionRqstError
    HAS_AOS_PYEZ = True
except ImportError:
    HAS_AOS_PYEZ = False


def do_backup_resource(module, resources):
    margs = module.params

    name = margs['name']
    if margs[name] not in resources:
        module.fail_json(msg='unknown collection item: %s' % name)
        # unreachable

    item = resources[name]
    dest_file = margs['dest']

    try:
        json.dump(item.datum, open(dest_file, 'w+'), indent=3)

    except IOError as exc:
        module.fail_json(msg="unable to write file '%s': %s" %
                             (dest_file, exc.message))

    module.exit_json(change=False,
                     dest=dest_file,
                     item_name=item.name,
                     item_id=item.id)


def do_load_resource(module, resources):
    margs = module.params
    src_file = margs['src']
    datum = None
    resource = None

    try:
        datum = json.load(open(src_file))
    except Exception as exc:
        module.fail_json(msg="unable to load src file '%s': %s" %
                             (src_file, exc.message))

    try:
        resource = resources[datum['display_name']]
        if resource.exists:
            module.exit_json(changed=False)

        resource.datum = datum
        resource.write()

    except KeyError:
        module.fail_json(msg="src data missing display_name, check file contents")

    except SessionRqstError as exc:
        module.fail_json(msg="unable to write item content: %s" % exc.message,
                         content=datum)

    module.exit_json(changed=True,
                     item_name=resource.name,
                     item_id=resource.id)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(required=True, type="dict"),
            collection=dict(required=True),
            src=dict(required=False),
            name=dict(required=False),
            dest=dict(require=False)
        )
    )

    if not HAS_AOS_PYEZ:
        module.fail_json(msg='aos-pyez is not installed.  Please see details '
                             'here: https://github.com/Apstra/aos-pyez')

    margs = module.params
    resources = None

    aos = Session()
    aos.session = margs['session']

    try:
        resources = getattr(aos, margs['collection'])

    except NotImplementedError:
        module.fail_json(msg="unknown resource '%s'" % margs['collection'])

    if margs['dest'] and margs['name']:
        do_backup_resource(module, resources)

    elif 'src' in margs:
        do_load_resource(module, resources)


if __name__ == "__main__":
    main()
