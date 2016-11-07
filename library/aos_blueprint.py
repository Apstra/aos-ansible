#!/usr/bin/env python
# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

from ansible.module_utils.basic import AnsibleModule

try:
    from apstra.aosom.session import Session
    from apstra.aosom.exc import LoginError, SessionError
    HAS_AOS_PYEZ = True
except ImportError:
    HAS_AOS_PYEZ = False

DOCUMENTATION = '''
---
module: aos_blueprint
author: jeremy@apstra.com (community@apstra.com)
version_added: "2.3"
short_description: Manage AOS blueprint instance
description:
    - Create a new blueprint instance
    - Delete a blueprint instance
    - Retrieve blueprint contents data-dictionary
    - Await blueprint build-ready status, obtain contents data-dictionary
requirements:
  - aos-pyez
options:
  session:
    description:
      - An existing AOS session as obtained by aos_login module
    required: true
  name:
    description:
      - Blueprint user-defined name
    required: true
  state:
    description:
      - Expected blueprint state
    choices: ['present', 'absent', 'build-ready']
    default: present
  timeout:
    description:
      - When state='build-ready', this timeout identifies timeout in seconds to wait before
        declaring a failure
  design_template:
    description:
      - When creating a blueprint, this value identifies, by user-name, an existing engineering
        design template within the AOS-server
    required: false
  reference_arch:
     description:
        - When creating a blueprint, this value identifies a known AOS reference
          architecture value.  Refer to AOS-server documentation for available values.
'''

EXAMPLES = '''
- name: Creating blueprint {{ blueprint_name }}
  aos_blueprint:
    session: "{{aos_session}}"
    name: "{{ blueprint_name }}"
    design_template: "{{ blueprint_template }}"
    reference_arch: two_stage_l3clos

- name: Deleting blueprint
  aos_blueprint:
    session: "{{aos_session}}"
    name: "{{ blueprint_name }}"
    state: absent

- name: Await blueprint build-ready, and obtain contents
  aos_blueprint:
    session: "{{aos_session}}"
    name: "{{ blueprint_name }}"
    state: build-ready
  register: bp
'''

RETURNS = '''
contents:
  description: Blueprint contents data-dictionary
  returned: always
  type: dict
  sample: { ... }

build_errors:
  description: When state='build-ready', and build errors exist, this contains list of errors
  returned: only when build-ready returns fail
  type: list
  sample: [{...}, {...}]
'''


def create_blueprint(aos, blueprint, module):
    margs = module.params

    try:
        template_id = aos.DesignTemplates[margs['design_template']].id
        blueprint.create(template_id, reference_arch=margs['reference_arch'])

    except SessionError as exc:
        msg = 'likely missing dependencies' if 'UNPROCESSABLE ENTITY' in exc.message \
            else exc.message

        module.fail_json(msg="unable to create blueprint: %s" % msg)

    module.exit_json(changed=True, contents=blueprint.contents)


def ensure_absent(aos, blueprint, module):
    if not blueprint.exists:
        module.exit_json(changed=False)

    try:
        del blueprint.contents
    except SessionError as exc:
        module.fail_json(msg='unable to delete blueprint, %s' % exc.message)

    module.exit_json(changed=True)


def ensure_present(aos, blueprint, module):
    margs = module.params

    if blueprint.exists:
        module.exit_json(changed=False, contents=blueprint.contents)

    if margs['design_template'] and margs['reference_arch']:
        create_blueprint(aos, blueprint, module)

    module.fail_json(msg='blueprint %s does not exist' % blueprint.name)


def ensure_build_ready(aos, blueprint, module):
    margs = module.params

    if not blueprint.exists:
        module.fail_json(msg='blueprint %s does not exist' % blueprint.name)

    if blueprint.await_build_ready(timeout=margs['timeout']*1000):
        module.exit_json(contents=blueprint.contents)
    else:
        module.fail_json(msg='blueprint %s has build errors',
                         build_erros=blueprint.build_errors)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(required=True, type="dict"),
            name=dict(required=True),
            state=dict(choices=[
                'present', 'absent', 'build-ready'],
                default='present'),
            timeout=dict(type="int", default=5),
            design_template=dict(required=False),
            reference_arch=dict(required=False)
        ))

    if not HAS_AOS_PYEZ:
        module.fail_json(msg='aos-pyez is not installed.  Please see details '
                             'here: https://github.com/Apstra/aos-pyez')

    margs = module.params
    auth = margs['session']
    aos, blueprint = None, None

    try:
        aos = Session()
        aos.api.resume(url=auth['url'], headers=auth['headers'])
    except LoginError as exc:
        module.fail_json(msg='Unable to login to AOS API: %s' % str(exc))

    blueprint = aos.Blueprints[margs['name']]

    {
        'absent': ensure_absent,
        'present': ensure_present,
        'build-ready': ensure_build_ready

    }.get(margs['state'])(aos, blueprint, module)


if __name__ == '__main__':
    main()
