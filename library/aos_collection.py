#!/usr/bin/env python
# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

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
        module.fail_json(msg='unknown resource: %s' % name)
        # unreachable

    item = resources[name]
    dest_file = margs['backup']
    try:
        json.dump(item.datum, open(dest_file, 'w+'), indent=3)
    except IOError as exc:
        module.fail_json(msg="unable to write file '%s': %s" %
                             (dest_file, exc.message))

    module.exit_json(change=True)


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
        module.fail_json(msg="unable to write ip-pool content: %s" % exc.message,
                         content=datum)

    module.exit_json(changed=True,
                     ip_pool=dict(name=resource.name, id=resource.id))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(required=True, type="dict"),
            collection=dict(required=True),
            src=dict(required=False),
            name=dict(required=False),
            backup=dict(require=False)
        )
    )

    if not HAS_AOS_PYEZ:
        module.fail_json(msg='aos-pyez is not installed.  Please see details '
                             'here: https://github.com/Apstra/aos-pyez')

    margs = module.params
    auth = margs['session']
    resources = None

    aos = Session()
    aos.api.resume(auth['url'], auth['headers'])

    try:
        resources = getattr(aos, margs['collection'])

    except NotImplementedError:
        module.fail_json(msg="unknown resource '%s'" % margs['collection'])

    if margs['backup'] and margs['name']:
        do_backup_resource(module, resources)

    elif 'src' in margs:
        do_load_resource(module, resources)


if __name__ == "__main__":
    main()
