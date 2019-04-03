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

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'version': '1.0'}

DOCUMENTATION = '''
---
module: aos_hcl
author: Jeremy Schulman (@jeremyschulman)
version_added: "2.4"
short_description: Manage AOS Hardware Compatibility List
description:
  - Apstra AOS HCL module let you manage your Hardware entries easily.
    You can create create and delete an item by Name, ID or by using a JSON File.
    This module is idempotent and support the I(check) mode.
    It's using the AOS REST API.
requirements:
  - "aos-pyez >= 0.6.1"
options:
  session:
    description:
      - An existing AOS session as obtained by M(aos_login) module.
    required: true
  name:
    description:
      - Name of the HCL entry to manage.
        Only one of I(name), I(id) or I(content) can be set.
  id:
    description:
      - AOS Id of the HCL entry to manage (can't be used to create a new item),
        Only one of I(name), I(id) or I(content) can be set.
  content:
    description:
      - Datastructure of the HCL to create. The data can be in YAML / JSON or
        directly a variable. It's the same datastructure that is returned
        on success in I(value).
  state:
    description:
      - Indicate what is the expected state of the item (present or not).
    default: present
    choices: ['present', 'absent']
'''

EXAMPLES = '''

- name: "Delete a HCL by name"
  aos_hcl:
    session: "{{ aos_session }}"
    name: "my-hcl"
    state: absent

- name: "Delete a HCL by id"
  aos_hcl:
    session: "{{ aos_session }}"
    id: "45ab26fc-c2ed-4307-b330-0870488fa13e"
    state: absent

# Save a HCL to a file

- name: "Access HCL 1/3"
  aos_hcl:
    session: "{{ aos_session }}"
    name: "my-hcl"
    state: present
  register: hcl
- name: "Save HCL into a JSON file 2/3"
  copy:
    content: "{{ hcl.value | to_nice_json }}"
    dest: hcl_saved.json
- name: "Save HCL into a YAML file 3/3"
  copy:
    content: "{{ hcl.value | to_nice_yaml }}"
    dest: hcl_saved.yaml

- name: "Load HCL from a JSON file"
  aos_hcl:
    session: "{{ aos_session }}"
    content: "{{ lookup('file', 'resources/hcl_saved.json') }}"
    state: present

- name: "Load HCL from a YAML file"
  aos_hcl:
    session: "{{ aos_session }}"
    content: "{{ lookup('file', 'resources/hcl_saved.yaml') }}"
    state: present
'''

RETURNS = '''
name:
  description: Name of the HCL
  returned: always
  type: str
  sample: AOS-1x25-1

id:
  description: AOS unique ID assigned to the HCL
  returned: always
  type: str
  sample: fcc4ac1c-e249-4fe7-b458-2138bfb44c06

value:
  description: Value of the object as returned by the AOS Server
  returned: always
  type: dict
  sample: {'...'}
'''

import time

from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.aos import (
    get_aos_session, find_collection_item,
    do_load_resource, content_to_dict)


#########################################################
# State Processing
#########################################################

def item_absent(module, item):

    margs = module.params

    # If the module do not exist, return directly
    if item.exists is False:
        module.exit_json(changed=False,
                         name=margs['name'],
                         id=margs['id'],
                         value={})

    # If not in check mode, delete HCL
    if not module.check_mode:
        try:
            # Need to way 1sec before a delete to workaround a current limitation in AOS
            time.sleep(1)
            item.delete()
        except:
            module.fail_json(msg="An error occured, while trying to delete the HCL")

    module.exit_json(changed=True, name=item.name,
                     id=item.id, value={})


def item_present(module, item):

    margs = module.params

    if margs['content'] is not None:

        if 'display_name' in module.params['content'].keys():
            do_load_resource(module, item.collection, module.params['content']['display_name'])
        else:
            module.fail_json(msg="Unable to find display_name in 'content', Mandatory")

    # if item doesn't exist already, create a new one

    if item.exists is False and 'content' not in margs.keys():
        module.fail_json(msg="'content' is mandatory for module that don't exist currently")

    module.exit_json(changed=False, name=item.name,
                     id=item.id, value=item.value)


#########################################################
# Main Function
#########################################################

def aos_hardware(module):

    margs = module.params

    try:
        aos = get_aos_session(module, margs['session'])
    except Exception as exc:
        module.fail_json(
            msg="Unable to login to the AOS server: %s" % str(exc))

    item_name = False
    item_id = False

    if margs['content'] is not None:

        content = content_to_dict(module, margs['content'])

        if 'display_name' in content.keys():
            item_name = content['display_name']
        else:
            module.fail_json(msg="Unable to extract 'display_name' from 'content'")

    elif margs['name'] is not None:
        item_name = margs['name']

    elif margs['id'] is not None:
        item_id = margs['id']

    # ----------------------------------------------------
    # Find Object if available based on ID or Name
    # ----------------------------------------------------

    item = find_collection_item(aos.Hardware,
                                item_name=item_name,
                                item_id=item_id)

    # ----------------------------------------------------
    # Proceed based on State value
    # ----------------------------------------------------

    if margs['state'] == 'absent':
        item_absent(module, item)
    elif margs['state'] == 'present':
        item_present(module, item)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            session=dict(required=True, type="dict"),
            name=dict(required=False),
            id=dict(required=False),
            content=dict(required=False, type="json"),
            state=dict(required=False,
                       choices=['present', 'absent'],
                       default="present")
        ),
        mutually_exclusive=[('name', 'id', 'content')],
        required_one_of=[('name', 'id', 'content')],
        supports_check_mode=True
    )

    aos_hardware(module)

if __name__ == "__main__":
    main()
