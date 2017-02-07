#!/usr/bin/env python
# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

DOCUMENTATION = '''
---
module: aos_login
author: jeremy@apstra.com (@jeremyschulman)
version_added: "2.3"
short_description: Login to AOS server for session token
description:
  - Obtain the AOS server session token by providing the required
    username and password credentials.  Upon successful authentication,
    this module will return the session-token that is required by all
    subsequent AOS module usage.
requirements:
  - aos-pyez
options:
  server:
    description:
      - Set to {{ inventory_hostname }}
    required: true
  port:
    description:
      - port number to use when connecting to the device
    required: false
  user:
    description:
      - Login username
    required: false
    default: admin
  passwd:
    description:
      - Login password
    required: false
    default: admin
'''

EXAMPLES = '''
# create a session with the AOS-server

- aos_login:
    server: "{{ inventory_hostname }}"
    user: admin
    passwd: admin

# now use that aos_session with other AOS modules, e.g.:

- aos_blueprint:
    session: "{{ aos_session }}"
    name: my-blueprint
    state: present
'''

RETURNS = '''
aos_session:
  description: Authenticated session information
  retured: always
  type: dict
  sample: { 'url': <str>, 'headers': {...} }
'''

from ansible.module_utils.basic import AnsibleModule

try:
    from apstra.aosom.session import Session
    import apstra.aosom.exc as aosexc
    HAS_AOS_PYEZ = True
except ImportError:
    HAS_AOS_PYEZ = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server=dict(required=True),
            port=dict(),
            user=dict(default='admin'),
            passwd=dict(default='admin', no_log=True)))

    if not HAS_AOS_PYEZ:
        module.fail_json(msg='aos-pyez is not installed.  Please see details '
                             'here: https://github.com/Apstra/aos-pyez')

    mod_args = module.params

    aos = Session(server=mod_args['server'], port=mod_args['port'],
                  user=mod_args['user'], passwd=mod_args['passwd'])

    try:
        aos.login()

    except aosexc.LoginServerUnreachableError:
        module.fail_json(
            msg="AOS-server [%s] API not available/reachable, check server" % aos.server)

    except aosexc.LoginAuthError:
        module.fail_json(msg="AOS-server login credentials failed")

    module.exit_json(
        changed=False,
        ansible_facts=dict(aos_session=aos.session))

if __name__ == '__main__':
    main()
