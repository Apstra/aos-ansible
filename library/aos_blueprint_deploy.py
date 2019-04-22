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
module: aos_blueprint_deploy
author: ryan@apstra.com (@that1guy15)
version_added: "2.7"
short_description: Deploy staged blueprint in AOS
description:
  - Deploy staged blueprint changes in AOS. Changes to blueprint will be
    deployed to all devices in the bluerint. 
options:
  session:
    description:
      - Session details from aos_login generated session.
    required: true
  name:
    description:
      -Name of blueprint, as defined by AOS when created.
    required: Np
  id:
    description:
      - ID of blueprint, as defined by AOS when created.
    required: No
'''

EXAMPLES = '''

- name: Deploy Blueprint DC1-EVPN by name
  aos_blueprint_deploy:
    session: "{{ aos_session }}"
    name: 'DC1-EVPN'

- name: Deploy Blueprint DC1-EVPN by id
  aos_blueprint_deploy:
    session: "{{ aos_session }}"
    id: "{{ aos_blueprint_id }}"    
'''

RETURNS = '''
blueprint_id:
  description: ID of the AOS blueprint deployed
  returned: always
  type: string
  sample: "db6588fe-9f36-4b04-8def-89e7dcd00c17"
'''

import requests
import urllib3
from ansible.module_utils.basic import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_ATTEMPTS = 3


def get_blueprint_status(session, blueprint_id):

    aos_url = "https://{}/api/blueprints/{}/deploy"\
        .format(session['server'], blueprint_id)
    headers = {'AUTHTOKEN': session['token'],
               'Accept': "application/json",
               'Content-Type': "application/json",
               'cache-control': "no-cache"}
    resp_data = {}

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.get(aos_url, headers=headers, verify=False)

            if response.ok:
                resp_data = response.json()
            else:
                response.raise_for_status()

        except (requests.ConnectionError,
                requests.HTTPError,
                requests.Timeout) as e:
            return "Unable to connect to server {}: {}".format(aos_url, e)

    return resp_data


def get_blueprint_version(session, blueprint_id):
    aos_url = "https://{}/api/blueprints/{}"\
        .format(session['server'], blueprint_id)
    headers = {'AUTHTOKEN': session['token'],
               'Accept': "application/json",
               'Content-Type': "application/json",
               'cache-control': "no-cache"}
    resp_data = {}

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.get(aos_url, headers=headers, verify=False)

            if response.ok:
                resp_data = response.json()
            else:
                response.raise_for_status()

        except (requests.ConnectionError,
                requests.HTTPError,
                requests.Timeout) as e:
            return "Unable to connect to server {}: {}".format(aos_url, e)

    bp_ver = int(resp_data['version'])

    if bp_ver:
        return bp_ver
    else:
        return ''


def get_blueprint_id(session, blueprint_name):
    aos_url = "https://{}/api/blueprints".format(session['server'])
    headers = {'AUTHTOKEN': session['token'],
               'Accept': "application/json",
               'Content-Type': "application/json",
               'cache-control': "no-cache"}
    resp_data = {}

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.get(aos_url, headers=headers, verify=False)

            if response.ok:
                resp_data = response.json()
            else:
                response.raise_for_status()

        except (requests.ConnectionError,
                requests.HTTPError,
                requests.Timeout) as e:
            return "Unable to connect to server {}: {}".format(aos_url, e)

    bp_id = [i['id'] for i in resp_data['items']
             if i['label'] == blueprint_name]

    if bp_id:
        return bp_id[0]
    else:
        return []


def aos_blueprint_deploy(module):
    mod_args = module.params

    if mod_args['id']:
        bp_id = mod_args['id']
    else:
        bp_id = get_blueprint_id(mod_args['session'], mod_args['name'])

    aos_url = "https://{}/api/blueprints/{}/deploy" \
        .format(mod_args['session']['server'], bp_id)

    headers = {'AUTHTOKEN': mod_args['session']['token'],
               'Accept': "application/json",
               'Content-Type': "application/json",
               'cache-control': "no-cache"}

    staged_version = get_blueprint_version(mod_args['session'], bp_id)
    payload = {"version": staged_version}

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.put(aos_url,
                                    data=json.dumps(payload),
                                    headers=headers,
                                    verify=False)

            if response.ok:

                bp_status = get_blueprint_status(mod_args['session'], bp_id)

                if bp_status['state'] == 'failure':
                    module.fail_json(msg="Unable to commit blueprint: {}"
                                     .format(bp_status['error']))

                else:
                    module.exit_json(changed=True,
                                     ansible_facts=dict(blueprint_id=bp_id))

            else:
                module.fail_json(
                    msg="Issue deploying blueprint {}: {}"
                        .format(bp_id, response))

        except (requests.ConnectionError,
                requests.HTTPError,
                requests.Timeout) as e:
            module.fail_json(
                msg="Unable to connect to server {}: {}"
                    .format(aos_url, e))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(required=True, type="dict"),
            name=dict(required=False),
            id=dict(required=False)
        ),
        mutually_exclusive=[('name', 'id')],
        required_one_of=[('name', 'id')],
        supports_check_mode=False
    )

    aos_blueprint_deploy(module)


if __name__ == '__main__':
    main()
