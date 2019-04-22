#!/usr/bin/python
#
# (c) 2017 Apstra Inc, <community@apstra.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: aos_login
author: ryan@apstra.com (@that1guy15)
version_added: "2.7"
short_description: Login to AOS server for session token
description:
  - Obtain the AOS server session token by providing the required
    username and password credentials.  Upon successful authentication,
    this module will return the session-token that is required by all
    subsequent AOS module usage. On success the module will automatically
    populate ansible facts with the variable I(aos_session)
    This module is not idempotent and do not support check mode.
options:
  server:
    description:
      - Address of the AOS Server on which you want to open a connection.
    required: true
  port:
    description:
      - Port number to use when connecting to the AOS server.
    default: 443
  user:
    description:
      - Login username to use when connecting to the AOS server.
    default: admin
  passwd:
    description:
      - Password to use when connecting to the AOS server.
    default: admin
'''

EXAMPLES = '''

- name: Create a session with the AOS-server
  aos_login:
    server: "{{ inventory_hostname }}"
    user: admin
    passwd: admin

- name: Use the newly created session (register is not mandatory)
  aos_ip_pool:
    session: "{{ aos_session }}"
    name: my_ip_pool
    state: present
'''

RETURNS = '''
aos_session:
  description: Authenticated session information
  returned: always
  type: string
  sample: "eyJhbUdm45OiJIUzI1Ni3asvdsInR5cCI6IkpXVCJ9.eyJ1c2V..."
'''

import json
from ansible.module_utils.basic import AnsibleModule
from module_utils.aos import requests_retry, set_requests_verify


def aos_login(module):

    mod_args = module.params

    aos_url = "https://{}/api/user/login".format(mod_args['server'])

    headers = {'Accept': "application/json",
               'Content-Type': "application/json",
               'cache-control': "no-cache"}
    payload = {"username": mod_args['user'],
               "password": mod_args['passwd']}

    response = requests_retry().post(aos_url,
                                     data=json.dumps(payload),
                                     headers=headers,
                                     verify=set_requests_verify())

    if response.status_code == 201:
        return {"server": mod_args['server'],
                "token": response.json()['token']}
    else:
        module.fail_json(
            msg="Issue logging into AOS-server {}: {}"
                .format(aos_url, response.json()))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server=dict(required=True),
            port=dict(default='443', type="int"),
            user=dict(default='admin'),
            passwd=dict(default='admin', no_log=True)))

    aos_session = aos_login(module)
    module.exit_json(changed=True,
                     ansible_facts=dict(aos_session=aos_session),
                     aos_session=dict(aos_session=aos_session))


if __name__ == '__main__':
    main()
